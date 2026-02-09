import os
import sys
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
import plotly.graph_objects as go
import requests
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder, PolynomialFeatures
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Add the parent directory to the path to import db_connection
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.src.scripts.util.db_connection import db_connect

# Page configuration
st.set_page_config(
    page_title="Electric Vehicles Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Database connection - Don't cache the connection itself, create new ones as needed
def get_connection():
    """Establish database connection using existing db_connect function"""
    try:
        conn = db_connect()
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        st.info(
            "Please check your database connection settings in db.src.scripts.util.db_connection"
        )
        return None


# Data loading functions with chunking for large datasets
@st.cache_data(ttl=600)
def load_vehicle_data_summary():
    """Load aggregated summary data for visualizations"""
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()

    query = """
    SELECT 
        v.model_year,
        m.make,
        m.model,
        v.ev_type,
        v.electric_range,
        v.cafv_eligibility,
        l.city,
        l.county,
        l.state,
        l.postal_code,
        COUNT(*) as vehicle_count
    FROM vehicle v
    JOIN model m ON v.model_id = m.model_id
    JOIN location l ON v.location_id = l.location_id
    GROUP BY 
        v.model_year, m.make, m.model, v.ev_type, 
        v.electric_range, v.cafv_eligibility,
        l.city, l.county, l.state, l.postal_code
    """

    try:
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error loading summary data: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()


@st.cache_data(ttl=600)
def load_map_data(limit=None):
    """Load data for map visualization with improved error handling and multiple strategies"""
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()

    limit_clause = f"LIMIT {limit}" if limit else ""

    # Strategy 1: Try PostGIS/Geometry functions (ST_X, ST_Y)
    try:
        query = f"""
        SELECT 
            m.make,
            m.model,
            v.model_year,
            l.city,
            l.state,
            ST_X(l.vehicle_location::geometry) as longitude,
            ST_Y(l.vehicle_location::geometry) as latitude
        FROM vehicle v
        JOIN model m ON v.model_id = m.model_id
        JOIN location l ON v.location_id = l.location_id
        WHERE l.vehicle_location IS NOT NULL
        ORDER BY RANDOM()
        {limit_clause}
        """

        df = pd.read_sql(query, conn)

        if not df.empty:
            # Validate coordinates
            df = df[(df["longitude"].notna()) & (df["latitude"].notna())]
            df = df[(df["longitude"] >= -180) & (df["longitude"] <= 180)]
            df = df[(df["latitude"] >= -90) & (df["latitude"] <= 90)]

            if not df.empty:
                conn.close()
                return df

    except Exception as e:
        # PostGIS method failed, will try manual parsing
        pass

    # Strategy 2: Manual string parsing of POINT data
    try:
        query = f"""
        SELECT 
            m.make,
            m.model,
            v.model_year,
            l.city,
            l.state,
            l.vehicle_location::text as vehicle_location
        FROM vehicle v
        JOIN model m ON v.model_id = m.model_id
        JOIN location l ON v.location_id = l.location_id
        WHERE l.vehicle_location IS NOT NULL
        ORDER BY RANDOM()
        {limit_clause}
        """

        df = pd.read_sql(query, conn)

        if df.empty:
            conn.close()
            return pd.DataFrame()

        # Parse POINT format manually with robust error handling
        def parse_point_robust(point_str):
            if pd.isna(point_str):
                return pd.Series([None, None])
            try:
                # Handle various POINT formats
                clean = str(point_str).strip()

                # Remove POINT wrapper (case insensitive)
                if "POINT" in clean.upper():
                    clean = clean.upper().replace("POINT", "").strip()
                clean = clean.replace("(", "").replace(")", "").strip()

                # Split by space or comma
                parts = clean.replace(",", " ").split()

                if len(parts) >= 2:
                    try:
                        lon = float(parts[0])
                        lat = float(parts[1])

                        # Validate ranges
                        if -180 <= lon <= 180 and -90 <= lat <= 90:
                            return pd.Series([lon, lat])
                    except ValueError:
                        pass

            except Exception:
                pass

            return pd.Series([None, None])

        df[["longitude", "latitude"]] = df["vehicle_location"].apply(parse_point_robust)
        df = df.dropna(subset=["longitude", "latitude"])

        conn.close()
        return df

    except Exception as e:
        st.error(f"Error loading map data: {e}")
        try:
            conn.rollback()
        except:
            pass
        return pd.DataFrame()
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass


def debug_map_data():
    """Debug function to check map data availability - shows detailed diagnostics"""
    conn = get_connection()
    if not conn:
        st.error("Cannot connect to database")
        return

    try:
        # Check 1: Count total vehicles with location data
        st.write("### 📊 Location Data Statistics")
        count_query = """
        SELECT 
            COUNT(*) as total_locations,
            COUNT(CASE WHEN vehicle_location IS NOT NULL THEN 1 END) as with_coords,
            COUNT(CASE WHEN vehicle_location IS NULL THEN 1 END) as without_coords
        FROM location
        """
        count_df = pd.read_sql(count_query, conn)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Locations", f"{count_df['total_locations'].iloc[0]:,}")
        with col2:
            st.metric("With Coordinates", f"{count_df['with_coords'].iloc[0]:,}")
        with col3:
            st.metric("Without Coordinates", f"{count_df['without_coords'].iloc[0]:,}")

        if count_df["with_coords"].iloc[0] == 0:
            st.error("❌ No location data found in database!")
            st.info("The vehicle_location column is NULL for all records.")
            return

        # Check 2: Sample location data format
        st.write("### 🔍 Sample Location Data")
        sample_query = """
        SELECT 
            city,
            state,
            vehicle_location::text as location_raw
        FROM location 
        WHERE vehicle_location IS NOT NULL 
        LIMIT 5
        """
        sample_df = pd.read_sql(sample_query, conn)
        st.dataframe(sample_df, use_container_width=True)

        # Check 3: Test POINT parsing on sample
        if not sample_df.empty:
            st.write("### 🧪 Parsing Test")
            sample_point = sample_df["location_raw"].iloc[0]
            st.code(f"Raw value: {sample_point}")

            # Try to parse it
            def parse_test(point_str):
                try:
                    clean = str(point_str).strip()
                    if "POINT" in clean.upper():
                        clean = clean.upper().replace("POINT", "").strip()
                    clean = clean.replace("(", "").replace(")", "").strip()
                    parts = clean.replace(",", " ").split()
                    if len(parts) >= 2:
                        lon, lat = float(parts[0]), float(parts[1])
                        return lon, lat
                except Exception as e:
                    return None, None, str(e)
                return None, None

            result = parse_test(sample_point)
            if len(result) == 2:
                lon, lat = result
                if lon is not None:
                    st.success(
                        f"✅ Successfully parsed: Longitude = {lon}, Latitude = {lat}"
                    )
                else:
                    st.error("❌ Failed to parse coordinates")
            else:
                st.error(f"❌ Parse error: {result[2]}")

        # Check 4: Location table schema
        st.write("### 📋 Location Table Schema")
        schema_query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'location'
        ORDER BY ordinal_position
        """
        schema_df = pd.read_sql(schema_query, conn)
        st.dataframe(schema_df, use_container_width=True)

        # Check 5: Test actual query used by map
        st.write("### 🗺️ Map Query Test (First 3 Results)")
        test_query = """
        SELECT 
            m.make,
            m.model,
            v.model_year,
            l.city,
            l.state,
            l.vehicle_location::text as location
        FROM vehicle v
        JOIN model m ON v.model_id = m.model_id
        JOIN location l ON v.location_id = l.location_id
        WHERE l.vehicle_location IS NOT NULL
        LIMIT 3
        """
        test_df = pd.read_sql(test_query, conn)
        st.dataframe(test_df, use_container_width=True)

        st.success("✅ Debug check complete!")

    except Exception as e:
        st.error(f"Debug error: {e}")
        import traceback

        st.code(traceback.format_exc())
    finally:
        conn.close()


@st.cache_data(ttl=600)
def load_paginated_data(offset=0, limit=100, filters=None):
    """Load paginated vehicle data for table view"""
    conn = get_connection()
    if conn is None:
        return pd.DataFrame(), 0

    where_clause = "WHERE 1=1"
    params = []

    if filters:
        if filters.get("state") and filters["state"] != "All":
            where_clause += " AND l.state = %s"
            params.append(filters["state"])
        if filters.get("make") and filters["make"] != "All":
            where_clause += " AND m.make = %s"
            params.append(filters["make"])
        if filters.get("ev_type") and filters["ev_type"] != "All":
            where_clause += " AND v.ev_type = %s"
            params.append(filters["ev_type"])
        if filters.get("year_range") is not None:
            year_range = filters["year_range"]
            where_clause += " AND v.model_year BETWEEN %s AND %s"
            params.extend([int(year_range[0]), int(year_range[1])])
        if filters.get("search"):
            where_clause += """ AND (
                v.vin ILIKE %s OR 
                m.make ILIKE %s OR 
                m.model ILIKE %s OR 
                l.city ILIKE %s
            )"""
            search_term = f"%{filters['search']}%"
            params.extend([search_term] * 4)

    count_query = f"""
    SELECT COUNT(*) as total
    FROM vehicle v
    JOIN model m ON v.model_id = m.model_id
    JOIN location l ON v.location_id = l.location_id
    {where_clause}
    """

    data_query = f"""
    SELECT 
        v.vin,
        v.model_year,
        m.make,
        m.model,
        v.ev_type,
        v.electric_range,
        l.city,
        l.county,
        l.state,
        l.postal_code
    FROM vehicle v
    JOIN model m ON v.model_id = m.model_id
    JOIN location l ON v.location_id = l.location_id
    {where_clause}
    ORDER BY v.model_year DESC, m.make, m.model
    LIMIT {limit} OFFSET {offset}
    """

    try:
        cur = conn.cursor()
        cur.execute(count_query, params)
        total_count = cur.fetchone()[0]
        cur.close()

        df = pd.read_sql(data_query, conn, params=params)
        return df, total_count
    except Exception as e:
        st.error(f"Error loading paginated data: {e}")
        try:
            conn.rollback()
        except:
            pass
        return pd.DataFrame(), 0
    finally:
        if conn:
            conn.close()


@st.cache_data(ttl=600)
def get_summary_stats():
    """Get summary statistics"""
    conn = get_connection()
    if conn is None:
        return {}

    query = """
    SELECT 
        COUNT(*) as total_vehicles,
        COUNT(DISTINCT m.make) as total_makes,
        COUNT(DISTINCT m.model) as total_models,
        COUNT(DISTINCT l.state) as total_states,
        AVG(v.electric_range) as avg_range,
        MAX(v.model_year) as latest_year,
        MIN(v.model_year) as earliest_year
    FROM vehicle v
    JOIN model m ON v.model_id = m.model_id
    JOIN location l ON v.location_id = l.location_id
    """

    try:
        df = pd.read_sql(query, conn)
        return df.iloc[0].to_dict()
    except Exception as e:
        st.error(f"Error loading summary stats: {e}")
        return {}
    finally:
        if conn:
            conn.close()


# Prediction model functions
@st.cache_resource
def train_range_prediction_model(df):
    """Train range prediction model"""
    expanded_rows = []
    for _, row in df.iterrows():
        expanded_rows.extend([row.to_dict()] * int(row["vehicle_count"]))
    df_expanded = pd.DataFrame(expanded_rows)
    df_expanded = df_expanded.drop("vehicle_count", axis=1)

    le_make = LabelEncoder()
    le_model = LabelEncoder()
    le_ev_type = LabelEncoder()
    le_cafv = LabelEncoder()
    le_state = LabelEncoder()

    df_expanded["make_encoded"] = le_make.fit_transform(df_expanded["make"])
    df_expanded["model_encoded"] = le_model.fit_transform(df_expanded["model"])
    df_expanded["ev_type_encoded"] = le_ev_type.fit_transform(df_expanded["ev_type"])
    df_expanded["cafv_encoded"] = le_cafv.fit_transform(df_expanded["cafv_eligibility"])
    df_expanded["state_encoded"] = le_state.fit_transform(df_expanded["state"])

    features = [
        "model_year",
        "make_encoded",
        "model_encoded",
        "ev_type_encoded",
        "cafv_encoded",
        "state_encoded",
    ]
    X = df_expanded[features]
    y = df_expanded["electric_range"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    feature_importance = pd.DataFrame(
        {
            "feature": ["Model Year", "Make", "Model", "EV Type", "CAFV", "State"],
            "importance": model.feature_importances_,
        }
    ).sort_values("importance", ascending=False)

    return {
        "model": model,
        "encoders": {
            "make": le_make,
            "model": le_model,
            "ev_type": le_ev_type,
            "cafv": le_cafv,
            "state": le_state,
        },
        "metrics": {"mae": mae, "rmse": rmse, "r2": r2},
        "predictions": {"y_test": y_test, "y_pred": y_pred},
        "feature_importance": feature_importance,
    }


def forecast_adoption(df, years_ahead=5, degree=2):
    """Forecast future adoption using polynomial regression"""
    yearly_data = df.groupby("model_year")["vehicle_count"].sum().reset_index()
    yearly_data = yearly_data.sort_values("model_year")

    X = yearly_data["model_year"].values.reshape(-1, 1)
    y = yearly_data["vehicle_count"].values

    poly_features = PolynomialFeatures(degree=degree)
    X_poly = poly_features.fit_transform(X)

    model = LinearRegression()
    model.fit(X_poly, y)

    y_pred = model.predict(X_poly)
    mae = mean_absolute_error(y, y_pred)
    r2 = r2_score(y, y_pred)

    last_year = int(yearly_data["model_year"].max())
    future_years = np.array(range(last_year + 1, last_year + years_ahead + 1)).reshape(
        -1, 1
    )
    future_X_poly = poly_features.transform(future_years)
    future_predictions = model.predict(future_X_poly)

    results = pd.DataFrame(
        {"year": future_years.flatten(), "predicted_vehicles": future_predictions}
    )

    return {
        "historical": yearly_data,
        "predictions": results,
        "model_fit": {"mae": mae, "r2": r2, "fitted_values": y_pred},
        "fitted_values": y_pred,
    }


# Main app
def main():
    st.title("Electric Vehicles Analysis Dashboard")
    st.markdown("---")

    # Load data
    with st.spinner("Loading data..."):
        df = load_vehicle_data_summary()
        stats = get_summary_stats()

    if df.empty:
        st.error("No data available. Please check your database connection and data.")
        return

    # Expand aggregated data for filtering
    expanded_rows = []
    for _, row in df.iterrows():
        expanded_rows.extend([row.to_dict()] * int(row["vehicle_count"]))
    df_expanded = pd.DataFrame(expanded_rows)
    df_expanded = df_expanded.drop("vehicle_count", axis=1)

    # Sidebar filters
    st.sidebar.header("Filters")

    states = ["All"] + sorted(df_expanded["state"].unique().tolist())
    selected_state = st.sidebar.selectbox("Select State", states)

    makes = ["All"] + sorted(df_expanded["make"].unique().tolist())
    selected_make = st.sidebar.selectbox("Select Make", makes)

    ev_types = ["All"] + sorted(df_expanded["ev_type"].unique().tolist())
    selected_ev_type = st.sidebar.selectbox("Select EV Type", ev_types)

    min_year = int(df_expanded["model_year"].min())
    max_year = int(df_expanded["model_year"].max())
    year_range = st.sidebar.slider(
        "Select Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
    )

    # Apply filters
    filtered_df = df.copy()
    if selected_state != "All":
        filtered_df = filtered_df[filtered_df["state"] == selected_state]
    if selected_make != "All":
        filtered_df = filtered_df[filtered_df["make"] == selected_make]
    if selected_ev_type != "All":
        filtered_df = filtered_df[filtered_df["ev_type"] == selected_ev_type]
    filtered_df = filtered_df[
        (filtered_df["model_year"] >= year_range[0])
        & (filtered_df["model_year"] <= year_range[1])
    ]

    total_vehicles = int(filtered_df["vehicle_count"].sum())

    # Summary metrics
    st.header("Summary Statistics")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Vehicles", f"{total_vehicles:,}")
    with col2:
        st.metric("Total Makes", stats.get("total_makes", 0))
    with col3:
        st.metric("Total Models", stats.get("total_models", 0))
    with col4:
        valid_range = filtered_df[filtered_df["electric_range"] > 0]
        if not valid_range.empty:
            weighted_avg = (
                valid_range["electric_range"] * valid_range["vehicle_count"]
            ).sum() / valid_range["vehicle_count"].sum()
            st.metric("Avg Range (mi)", f"{weighted_avg:.0f}")
        else:
            st.metric("Avg Range (mi)", "N/A")
    with col5:
        st.metric("States", stats.get("total_states", 0))

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(
        [
            "📈 Trends",
            "🏭 Manufacturers",
            "🗺️ Geographic",
            "⚡ Performance",
            "📋 Data Table",
            "🤖 AI Analyst",
            "🔮 Range Prediction",
            "📊 Adoption Forecast",
        ]
    )

    with tab1:
        st.subheader("Vehicle Registration Trends")

        col1, col2 = st.columns(2)

        with col1:
            year_data = (
                filtered_df.groupby("model_year")["vehicle_count"]
                .sum()
                .sort_index()
                .reset_index()
            )
            year_data.columns = ["model_year", "count"]
            fig1 = px.bar(
                year_data,
                x="model_year",
                y="count",
                labels={"model_year": "Model Year", "count": "Number of Vehicles"},
                title="Vehicles by Model Year",
            )
            fig1.update_traces(marker_color="#1f77b4")
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            ev_type_data = filtered_df.groupby("ev_type")["vehicle_count"].sum()
            fig2 = px.pie(
                values=ev_type_data.values,
                names=ev_type_data.index,
                title="Distribution by EV Type",
                hole=0.3,
            )
            st.plotly_chart(fig2, use_container_width=True)

        trend_data = (
            filtered_df.groupby(["model_year", "ev_type"])["vehicle_count"]
            .sum()
            .reset_index()
        )
        fig3 = px.line(
            trend_data,
            x="model_year",
            y="vehicle_count",
            color="ev_type",
            title="EV Registration Trends by Type",
            labels={"model_year": "Model Year", "vehicle_count": "Number of Vehicles"},
        )
        st.plotly_chart(fig3, use_container_width=True)

    with tab2:
        st.subheader("Manufacturer Analysis")

        col1, col2 = st.columns(2)

        with col1:
            top_makes = (
                filtered_df.groupby("make")["vehicle_count"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
                .reset_index()
            )
            top_makes.columns = ["make", "count"]
            fig4 = px.bar(
                top_makes,
                x="count",
                y="make",
                orientation="h",
                labels={"count": "Number of Vehicles", "make": "Make"},
                title="Top 10 Manufacturers",
            )
            fig4.update_traces(marker_color="#2ca02c")
            st.plotly_chart(fig4, use_container_width=True)

        with col2:
            top_5_makes = (
                filtered_df.groupby("make")["vehicle_count"]
                .sum()
                .sort_values(ascending=False)
                .head(5)
            )
            fig5 = px.pie(
                values=top_5_makes.values,
                names=top_5_makes.index,
                title="Market Share (Top 5 Manufacturers)",
            )
            st.plotly_chart(fig5, use_container_width=True)

        st.subheader("Top 15 Models")
        filtered_df["make_model"] = filtered_df["make"] + " " + filtered_df["model"]
        top_models = (
            filtered_df.groupby("make_model")["vehicle_count"]
            .sum()
            .sort_values(ascending=False)
            .head(15)
            .reset_index()
        )
        top_models.columns = ["make_model", "count"]
        fig6 = px.bar(
            top_models,
            x="count",
            y="make_model",
            orientation="h",
            labels={"count": "Number of Vehicles", "make_model": "Model"},
            title="Top 15 Vehicle Models",
        )
        fig6.update_traces(marker_color="#ff7f0e")
        st.plotly_chart(fig6, use_container_width=True)

    with tab3:
        st.subheader("Geographic Distribution")

        col1, col2 = st.columns(2)

        with col1:
            state_counts = (
                filtered_df.groupby("state")["vehicle_count"]
                .sum()
                .sort_values(ascending=False)
                .head(15)
                .reset_index()
            )
            state_counts.columns = ["state", "count"]
            fig7 = px.bar(
                state_counts,
                x="state",
                y="count",
                labels={"state": "State", "count": "Number of Vehicles"},
                title="Top 15 States by EV Count",
            )
            fig7.update_traces(marker_color="#d62728")
            st.plotly_chart(fig7, use_container_width=True)

        with col2:
            county_counts = (
                filtered_df.groupby("county")["vehicle_count"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
                .reset_index()
            )
            county_counts.columns = ["county", "count"]
            fig8 = px.bar(
                county_counts,
                x="count",
                y="county",
                orientation="h",
                labels={"count": "Number of Vehicles", "county": "County"},
                title="Top 10 Counties by EV Count",
            )
            fig8.update_traces(marker_color="#9467bd")
            st.plotly_chart(fig8, use_container_width=True)

        st.markdown("---")
        st.subheader("Vehicle Locations Map")

        # Debug section
        with st.expander(
            "🔍 Debug Map Data (Click if map doesn't work)", expanded=False
        ):
            if st.button("Run Diagnostic Check", key="debug_map_btn", type="secondary"):
                debug_map_data()

        # Map loading section
        col1, col2 = st.columns([3, 1])
        with col1:
            map_option = st.radio(
                "Map data size:",
                ["Sample (5,000 locations - faster)", "All locations (may be slow)"],
                horizontal=True,
            )
        with col2:
            load_map_btn = st.button("Load Map", type="primary")

        if load_map_btn:
            limit = 5000 if "Sample" in map_option else None

            with st.spinner("Loading map data..."):
                map_df = load_map_data(limit=limit)

                if (
                    not map_df.empty
                    and "latitude" in map_df.columns
                    and "longitude" in map_df.columns
                ):
                    # Additional validation
                    map_df = map_df[
                        (map_df["latitude"].notna())
                        & (map_df["longitude"].notna())
                        & (map_df["latitude"] >= -90)
                        & (map_df["latitude"] <= 90)
                        & (map_df["longitude"] >= -180)
                        & (map_df["longitude"] <= 180)
                    ]

                    if not map_df.empty:
                        if limit:
                            st.success(
                                f"✅ Loaded {len(map_df):,} sample locations (random selection)"
                            )
                        else:
                            st.success(
                                f"✅ Loaded all {len(map_df):,} vehicle locations"
                            )

                        fig9 = px.scatter_mapbox(
                            map_df,
                            lat="latitude",
                            lon="longitude",
                            color="make",
                            hover_data=["make", "model", "model_year", "city", "state"],
                            title="EV Locations",
                            zoom=3,
                            height=600,
                        )
                        fig9.update_layout(mapbox_style="open-street-map")
                        st.plotly_chart(fig9, use_container_width=True)
                    else:
                        st.error("❌ No valid coordinates found after filtering")
                        st.warning("**Troubleshooting steps:**")
                        st.markdown("""
                        1. Click **"Debug Map Data"** above to check your database
                        2. Verify that `vehicle_location` column has data
                        3. Check that coordinates are in valid format (POINT(longitude latitude))
                        """)
                else:
                    st.warning("⚠️ No location data available for mapping")
                    st.info("**Possible reasons:**")
                    st.markdown("""
                    - The `vehicle_location` column is NULL for all records
                    - The POINT data format couldn't be parsed
                    - Database connection issue
                    
                    **👉 Click "Debug Map Data" above to investigate**
                    """)
        else:
            st.info(
                "👆 Select your preferred data size and click 'Load Map' to view the interactive map"
            )

    with tab4:
        st.subheader("Electric Range Analysis")

        total_with_range = filtered_df[filtered_df["electric_range"] > 0][
            "vehicle_count"
        ].sum()
        total_vehicles_tab = filtered_df["vehicle_count"].sum()

        st.info(
            f"📊 {int(total_with_range):,} out of {int(total_vehicles_tab):,} vehicles have reported electric range data ({total_with_range/total_vehicles_tab*100:.1f}%)"
        )

        bev_df = filtered_df[
            filtered_df["ev_type"] == "Battery Electric Vehicle (BEV)"
        ].copy()
        phev_df = filtered_df[
            filtered_df["ev_type"] == "Plug-in Hybrid Electric Vehicle (PHEV)"
        ].copy()

        bev_range_df = bev_df[bev_df["electric_range"] > 0].copy()
        phev_range_df = phev_df[phev_df["electric_range"] > 0].copy()

        range_df = filtered_df[filtered_df["electric_range"] > 0].copy()

        if not range_df.empty:
            col1, col2 = st.columns(2)

            with col1:
                range_expanded = []
                for _, row in range_df.iterrows():
                    range_expanded.extend(
                        [row["electric_range"]] * int(row["vehicle_count"])
                    )

                fig10 = px.histogram(
                    x=range_expanded,
                    nbins=50,
                    labels={"x": "Electric Range (miles)"},
                    title=f"Electric Range Distribution ({len(range_expanded):,} vehicles)",
                )
                fig10.update_traces(marker_color="#17becf")
                st.plotly_chart(fig10, use_container_width=True)

            with col2:
                make_stats = []
                for make in range_df["make"].unique():
                    make_data = range_df[range_df["make"] == make]
                    if len(make_data) > 0 and make_data["vehicle_count"].sum() > 0:
                        weighted_avg = (
                            make_data["electric_range"] * make_data["vehicle_count"]
                        ).sum() / make_data["vehicle_count"].sum()
                        total_count = make_data["vehicle_count"].sum()
                        make_stats.append(
                            {
                                "make": make,
                                "avg_range": weighted_avg,
                                "count": total_count,
                            }
                        )

                if make_stats:
                    make_range = pd.DataFrame(make_stats)
                    make_range = make_range.sort_values(
                        "avg_range", ascending=False
                    ).head(10)

                    fig11 = px.bar(
                        make_range,
                        x="avg_range",
                        y="make",
                        orientation="h",
                        labels={"avg_range": "Average Range (miles)", "make": "Make"},
                        title="Average Range by Manufacturer (Top 10)",
                        hover_data=["count"],
                    )
                    fig11.update_traces(marker_color="#bcbd22")
                    st.plotly_chart(fig11, use_container_width=True)
                else:
                    st.warning("No range data available for manufacturers")

            year_stats = []
            for year in sorted(range_df["model_year"].unique()):
                year_data = range_df[range_df["model_year"] == year]
                if len(year_data) > 0 and year_data["vehicle_count"].sum() > 0:
                    weighted_avg = (
                        year_data["electric_range"] * year_data["vehicle_count"]
                    ).sum() / year_data["vehicle_count"].sum()
                    year_stats.append({"model_year": year, "avg_range": weighted_avg})

            if year_stats:
                year_range_data = pd.DataFrame(year_stats)

                fig12 = px.line(
                    year_range_data,
                    x="model_year",
                    y="avg_range",
                    title="Average Electric Range Trend Over Years",
                    labels={
                        "model_year": "Model Year",
                        "avg_range": "Average Range (miles)",
                    },
                    markers=True,
                )
                fig12.update_traces(line_color="#e377c2", line_width=3)
                st.plotly_chart(fig12, use_container_width=True)
            else:
                st.warning("No range data available for year trend")
        else:
            st.warning("⚠️ No electric range data available for the selected filters.")
            st.info(
                "💡 Tip: Many Plug-in Hybrid Electric Vehicles (PHEV) have 0 or unreported electric range. Try filtering by 'Battery Electric Vehicle (BEV)' for better range analysis."
            )

        st.subheader("Vehicle Type Distribution")
        col1, col2 = st.columns(2)

        with col1:
            ev_type_counts = filtered_df.groupby("ev_type")["vehicle_count"].sum()
            fig_ev_type = px.pie(
                values=ev_type_counts.values,
                names=ev_type_counts.index,
                title="BEV vs PHEV Distribution",
            )
            st.plotly_chart(fig_ev_type, use_container_width=True)

        with col2:
            st.metric(
                "Battery Electric (BEV)", f"{int(bev_df['vehicle_count'].sum()):,}"
            )
            st.metric(
                "Plug-in Hybrid (PHEV)", f"{int(phev_df['vehicle_count'].sum()):,}"
            )

            if not bev_range_df.empty:
                bev_avg = (
                    bev_range_df["electric_range"] * bev_range_df["vehicle_count"]
                ).sum() / bev_range_df["vehicle_count"].sum()
                st.metric("Avg BEV Range", f"{bev_avg:.0f} mi")

            if not phev_range_df.empty:
                phev_avg = (
                    phev_range_df["electric_range"] * phev_range_df["vehicle_count"]
                ).sum() / phev_range_df["vehicle_count"].sum()
                st.metric("Avg PHEV Range", f"{phev_avg:.0f} mi")

        st.subheader("Clean Alternative Fuel Vehicle (CAFV) Eligibility")
        cafv_counts = filtered_df.groupby("cafv_eligibility")["vehicle_count"].sum()
        fig13 = px.pie(
            values=cafv_counts.values,
            names=cafv_counts.index,
            title="CAFV Eligibility Distribution",
        )
        st.plotly_chart(fig13, use_container_width=True)

    with tab5:
        st.subheader("Vehicle Data Table")

        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            search = st.text_input("Search (VIN, Make, Model, City)", "")
        with col2:
            rows_per_page = st.selectbox("Rows per page", [25, 50, 100, 250], index=0)
        with col3:
            page_number = st.number_input("Page", min_value=1, value=1, step=1)

        if year_range is not None:
            try:
                if isinstance(year_range, (tuple, list)):
                    year_min_val, year_max_val = int(year_range[0]), int(year_range[1])
                else:
                    year_min_val, year_max_val = int(year_range), int(year_range)
                year_range_tuple = (year_min_val, year_max_val)
            except:
                year_range_tuple = None
        else:
            year_range_tuple = None

        table_filters = {
            "state": selected_state,
            "make": selected_make,
            "ev_type": selected_ev_type,
            "year_range": year_range_tuple,
            "search": search if search else None,
        }

        offset = (page_number - 1) * rows_per_page

        with st.spinner("Loading data..."):
            display_df, total_count = load_paginated_data(
                offset=offset, limit=rows_per_page, filters=table_filters
            )

        if not display_df.empty:
            st.dataframe(display_df, use_container_width=True, height=400)

            total_pages = (total_count + rows_per_page - 1) // rows_per_page
            start_row = offset + 1
            end_row = min(offset + rows_per_page, total_count)

            col1, col2, col3 = st.columns([2, 2, 2])
            with col1:
                st.info(
                    f"Showing {start_row:,} - {end_row:,} of {total_count:,} vehicles"
                )
            with col2:
                st.info(f"Page {page_number:,} of {total_pages:,}")
            with col3:
                if st.button("Export Current Page to CSV"):
                    csv = display_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"ev_data_page{page_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                    )
        else:
            st.warning("No data found matching the current filters.")

    API_URL = "http://localhost:8000/query"

    with tab6:
        st.subheader("AI Electric Vehicle Analyst")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        if prompt := st.chat_input("Ask anything about EV data..."):
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing EV dataset..."):
                    try:
                        response = requests.post(
                            API_URL, json={"question": prompt}, timeout=60
                        )
                        response.raise_for_status()

                        data = response.json()
                        answer = data.get("answer")
                        if isinstance(answer, dict) and "content" in answer:
                            answer = answer["content"]

                        st.write(answer)

                    except Exception as e:
                        answer = "Sorry, I couldn't process that question right now."
                        st.error(answer)

            st.session_state.messages.append({"role": "assistant", "content": answer})

    with tab7:
        st.subheader("Electric Range Prediction Model")

        # Filter data with valid range
        range_data = df[df["electric_range"] > 0].copy()

        if not range_data.empty and len(range_data) > 10:
            # Train model button
            if st.button("Train Prediction Model", type="primary"):
                with st.spinner("Training model..."):
                    trained_model = train_range_prediction_model(range_data)
                    st.session_state.range_model = trained_model
                    st.success("✅ Model trained successfully!")

            if "range_model" in st.session_state:
                model_data = st.session_state.range_model
                metrics = model_data["metrics"]

                # Display metrics
                col1, col2, col3 = st.columns(3)
                col1.metric("Mean Absolute Error", f"{metrics['mae']:.2f} miles")
                col2.metric("Root Mean Squared Error", f"{metrics['rmse']:.2f} miles")
                col3.metric("R² Score", f"{metrics['r2']:.4f}")

                st.markdown("---")

                # Prediction interface
                st.subheader("Make a Prediction")

                expanded_range = []
                for _, row in range_data.iterrows():
                    expanded_range.append(row.to_dict())
                df_range_expanded = pd.DataFrame(expanded_range)

                col1, col2, col3 = st.columns(3)

                with col1:
                    pred_year = st.number_input(
                        "Model Year", min_value=2010, max_value=2030, value=2024
                    )
                    pred_make = st.selectbox(
                        "Make",
                        sorted(df_range_expanded["make"].unique()),
                        key="pred_make",
                    )

                with col2:
                    available_models = df_range_expanded[
                        df_range_expanded["make"] == pred_make
                    ]["model"].unique()
                    pred_model = st.selectbox(
                        "Model", sorted(available_models), key="pred_model"
                    )
                    pred_ev_type = st.selectbox(
                        "EV Type",
                        sorted(df_range_expanded["ev_type"].unique()),
                        key="pred_ev_type",
                    )

                with col3:
                    pred_cafv = st.selectbox(
                        "CAFV Eligibility",
                        sorted(df_range_expanded["cafv_eligibility"].unique()),
                        key="pred_cafv",
                    )
                    pred_state = st.selectbox(
                        "State",
                        sorted(df_range_expanded["state"].unique()),
                        key="pred_state",
                    )

                if st.button("Predict Range"):
                    try:
                        encoders = model_data["encoders"]
                        input_data = pd.DataFrame(
                            {
                                "model_year": [pred_year],
                                "make_encoded": [
                                    encoders["make"].transform([pred_make])[0]
                                ],
                                "model_encoded": [
                                    encoders["model"].transform([pred_model])[0]
                                ],
                                "ev_type_encoded": [
                                    encoders["ev_type"].transform([pred_ev_type])[0]
                                ],
                                "cafv_encoded": [
                                    encoders["cafv"].transform([pred_cafv])[0]
                                ],
                                "state_encoded": [
                                    encoders["state"].transform([pred_state])[0]
                                ],
                            }
                        )

                        prediction = model_data["model"].predict(input_data)[0]
                        st.success(
                            f"### Predicted Electric Range: **{prediction:.1f} miles**"
                        )

                        actual_range = df_range_expanded[
                            (df_range_expanded["make"] == pred_make)
                            & (df_range_expanded["model"] == pred_model)
                            & (df_range_expanded["model_year"] == pred_year)
                        ]["electric_range"]

                        if not actual_range.empty:
                            avg_actual = actual_range.mean()
                            st.info(
                                f"ℹ️ Actual average range for this vehicle: **{avg_actual:.1f} miles**"
                            )
                    except Exception as e:
                        st.error(f"Error: {e}")
                        st.info("This combination might not exist in training data.")

                # Feature importance chart
                st.markdown("---")
                st.subheader("Feature Importance")
                fig_imp = px.bar(
                    model_data["feature_importance"],
                    x="importance",
                    y="feature",
                    orientation="h",
                    title="Which factors matter most for predicting range?",
                )
                st.plotly_chart(fig_imp, use_container_width=True)
            else:
                st.info("👆 Click 'Train Prediction Model' to get started")
        else:
            st.warning("Not enough data with valid electric range for predictions")

    with tab8:
        st.subheader("EV Adoption Forecasting")

        years_ahead = st.slider("Years to forecast", 1, 10, 5, key="forecast_years")
        poly_degree = st.slider("Model complexity", 1, 4, 2, key="poly_degree")

        if st.button("Generate Forecast", type="primary"):
            with st.spinner("Generating forecast..."):
                forecast_results = forecast_adoption(df, years_ahead, poly_degree)

                # Metrics
                col1, col2, col3 = st.columns(3)

                current_year = int(forecast_results["historical"]["model_year"].max())
                current_count = int(
                    forecast_results["historical"]["vehicle_count"].iloc[-1]
                )

                with col1:
                    st.metric("Current Year", current_year)
                    st.metric("Vehicles in Latest Year", f"{current_count:,}")

                with col2:
                    st.metric(
                        "Model R² Score", f"{forecast_results['model_fit']['r2']:.4f}"
                    )
                    st.metric(
                        "Mean Absolute Error",
                        f"{forecast_results['model_fit']['mae']:,.0f}",
                    )

                with col3:
                    future_year = int(forecast_results["predictions"]["year"].iloc[-1])
                    future_count = int(
                        forecast_results["predictions"]["predicted_vehicles"].iloc[-1]
                    )
                    st.metric(f"Forecast for {future_year}", f"{future_count:,}")
                    growth_rate = ((future_count - current_count) / current_count) * 100
                    st.metric("Projected Growth", f"{growth_rate:.1f}%")

                # Visualization
                fig = go.Figure()

                fig.add_trace(
                    go.Scatter(
                        x=forecast_results["historical"]["model_year"],
                        y=forecast_results["historical"]["vehicle_count"],
                        mode="markers+lines",
                        name="Historical Data",
                        marker=dict(size=8, color="blue"),
                        line=dict(color="blue", width=2),
                    )
                )

                fig.add_trace(
                    go.Scatter(
                        x=forecast_results["historical"]["model_year"],
                        y=forecast_results["fitted_values"],
                        mode="lines",
                        name="Model Fit",
                        line=dict(color="green", dash="dot", width=2),
                    )
                )

                fig.add_trace(
                    go.Scatter(
                        x=forecast_results["predictions"]["year"],
                        y=forecast_results["predictions"]["predicted_vehicles"],
                        mode="markers+lines",
                        name="Forecast",
                        marker=dict(size=8, color="red", symbol="diamond"),
                        line=dict(color="red", width=2, dash="dash"),
                    )
                )

                fig.update_layout(
                    title="EV Adoption Trend and Forecast",
                    xaxis_title="Year",
                    yaxis_title="Number of Vehicles",
                    hovermode="x unified",
                    height=500,
                )

                st.plotly_chart(fig, use_container_width=True)

                # Forecast table
                st.subheader("Detailed Forecast")
                forecast_table = forecast_results["predictions"].copy()
                forecast_table["predicted_vehicles"] = forecast_table[
                    "predicted_vehicles"
                ].astype(int)
                st.dataframe(
                    forecast_table.style.format({"predicted_vehicles": "{:,}"}),
                    use_container_width=True,
                )

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>Electric Vehicles Analysis Dashboard | Data updated in real-time from database</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
