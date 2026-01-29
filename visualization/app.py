import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

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


# Database connection
@st.cache_resource
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


# Data loading functions
@st.cache_data(ttl=600)
def load_vehicle_data():
    """Load vehicle data with model and location information"""
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()

    query = """
    SELECT 
        v.vin,
        v.model_year,
        m.make,
        m.model,
        v.ev_type,
        v.electric_range,
        v.cafv_eligibility,
        v.electric_utility,
        l.city,
        l.county,
        l.state,
        l.postal_code,
        l.legislative_district,
        ST_X(l.vehicle_location) as longitude,
        ST_Y(l.vehicle_location) as latitude
    FROM vehicle v
    JOIN model m ON v.model_id = m.model_id
    JOIN location l ON v.location_id = l.location_id
    """

    try:
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()


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


# Main app
def main():
    st.title("Electric Vehicles Analysis Dashboard")
    st.markdown("---")

    # Load data
    with st.spinner("Loading data..."):
        df = load_vehicle_data()
        stats = get_summary_stats()

    if df.empty:
        st.error("No data available. Please check your database connection and data.")
        return

    # Sidebar filters
    st.sidebar.header("🔍 Filters")

    # State filter
    states = ["All"] + sorted(df["state"].unique().tolist())
    selected_state = st.sidebar.selectbox("Select State", states)

    # Make filter
    makes = ["All"] + sorted(df["make"].unique().tolist())
    selected_make = st.sidebar.selectbox("Select Make", makes)

    # EV Type filter
    ev_types = ["All"] + sorted(df["ev_type"].unique().tolist())
    selected_ev_type = st.sidebar.selectbox("Select EV Type", ev_types)

    # Year range filter
    min_year = int(df["model_year"].min())
    max_year = int(df["model_year"].max())
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

    # Summary metrics
    st.header("Summary Statistics")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Vehicles", f"{len(filtered_df):,}")
    with col2:
        st.metric("Total Makes", stats.get("total_makes", 0))
    with col3:
        st.metric("Total Models", stats.get("total_models", 0))
    with col4:
        avg_range = filtered_df["electric_range"].mean()
        st.metric(
            "Avg Range (mi)", f"{avg_range:.0f}" if not pd.isna(avg_range) else "N/A"
        )
    with col5:
        st.metric("States", stats.get("total_states", 0))

    st.markdown("---")

    # Tabs for different visualizations
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Trends", "Manufacturers", "Geographic", "Performance", "Data Table"]
    )

    with tab1:
        st.subheader("Vehicle Registration Trends")

        col1, col2 = st.columns(2)

        with col1:
            # Vehicles by year
            year_counts = filtered_df["model_year"].value_counts().sort_index()
            fig1 = px.bar(
                x=year_counts.index,
                y=year_counts.values,
                labels={"x": "Model Year", "y": "Number of Vehicles"},
                title="Vehicles by Model Year",
            )
            fig1.update_traces(marker_color="#1f77b4")
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            # EV Type distribution
            ev_type_counts = filtered_df["ev_type"].value_counts()
            fig2 = px.pie(
                values=ev_type_counts.values,
                names=ev_type_counts.index,
                title="Distribution by EV Type",
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Trend over time by EV type
        trend_data = (
            filtered_df.groupby(["model_year", "ev_type"])
            .size()
            .reset_index(name="count")
        )
        fig3 = px.line(
            trend_data,
            x="model_year",
            y="count",
            color="ev_type",
            title="EV Registration Trends by Type",
            labels={"model_year": "Model Year", "count": "Number of Vehicles"},
        )
        st.plotly_chart(fig3, use_container_width=True)

    with tab2:
        st.subheader("Manufacturer Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # Top 10 makes
            top_makes = filtered_df["make"].value_counts().head(10)
            fig4 = px.bar(
                x=top_makes.values,
                y=top_makes.index,
                orientation="h",
                labels={"x": "Number of Vehicles", "y": "Make"},
                title="Top 10 Manufacturers",
            )
            fig4.update_traces(marker_color="#2ca02c")
            st.plotly_chart(fig4, use_container_width=True)

        with col2:
            # Market share of top manufacturers
            top_5_makes = filtered_df["make"].value_counts().head(5)
            fig5 = px.pie(
                values=top_5_makes.values,
                names=top_5_makes.index,
                title="Market Share (Top 5 Manufacturers)",
            )
            st.plotly_chart(fig5, use_container_width=True)

        # Top models
        st.subheader("Top 15 Models")
        filtered_df["make_model"] = filtered_df["make"] + " " + filtered_df["model"]
        top_models = filtered_df["make_model"].value_counts().head(15)
        fig6 = px.bar(
            x=top_models.values,
            y=top_models.index,
            orientation="h",
            labels={"x": "Number of Vehicles", "y": "Model"},
            title="Top 15 Vehicle Models",
        )
        fig6.update_traces(marker_color="#ff7f0e")
        st.plotly_chart(fig6, use_container_width=True)

    with tab3:
        st.subheader("Geographic Distribution")

        col1, col2 = st.columns(2)

        with col1:
            # Vehicles by state
            state_counts = filtered_df["state"].value_counts().head(15)
            fig7 = px.bar(
                x=state_counts.index,
                y=state_counts.values,
                labels={"x": "State", "y": "Number of Vehicles"},
                title="Top 15 States by EV Count",
            )
            fig7.update_traces(marker_color="#d62728")
            st.plotly_chart(fig7, use_container_width=True)

        with col2:
            # Vehicles by county (top 10)
            county_counts = filtered_df["county"].value_counts().head(10)
            fig8 = px.bar(
                x=county_counts.values,
                y=county_counts.index,
                orientation="h",
                labels={"x": "Number of Vehicles", "y": "County"},
                title="Top 10 Counties by EV Count",
            )
            fig8.update_traces(marker_color="#9467bd")
            st.plotly_chart(fig8, use_container_width=True)

        # Map visualization
        st.subheader("Vehicle Locations Map")
        if not filtered_df[["latitude", "longitude"]].isna().all().any():
            # Sample data for performance if too many points
            map_df = filtered_df.dropna(subset=["latitude", "longitude"])
            if len(map_df) > 5000:
                map_df = map_df.sample(5000)
                st.info("Showing 5,000 random samples for performance")

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
            st.warning("No location data available for mapping")

    with tab4:
        st.subheader("Electric Range Analysis")

        # Remove zero or null ranges for meaningful analysis
        range_df = filtered_df[filtered_df["electric_range"] > 0].copy()

        col1, col2 = st.columns(2)

        with col1:
            # Range distribution
            fig10 = px.histogram(
                range_df,
                x="electric_range",
                nbins=50,
                labels={"electric_range": "Electric Range (miles)"},
                title="Electric Range Distribution",
            )
            fig10.update_traces(marker_color="#17becf")
            st.plotly_chart(fig10, use_container_width=True)

        with col2:
            # Average range by make (top 10)
            avg_range_by_make = (
                range_df.groupby("make")["electric_range"]
                .mean()
                .sort_values(ascending=False)
                .head(10)
            )
            fig11 = px.bar(
                x=avg_range_by_make.values,
                y=avg_range_by_make.index,
                orientation="h",
                labels={"x": "Average Range (miles)", "y": "Make"},
                title="Average Range by Manufacturer (Top 10)",
            )
            fig11.update_traces(marker_color="#bcbd22")
            st.plotly_chart(fig11, use_container_width=True)

        # Range trend over years
        avg_range_by_year = (
            range_df.groupby("model_year")["electric_range"].mean().reset_index()
        )
        fig12 = px.line(
            avg_range_by_year,
            x="model_year",
            y="electric_range",
            title="Average Electric Range Trend Over Years",
            labels={
                "model_year": "Model Year",
                "electric_range": "Average Range (miles)",
            },
        )
        fig12.update_traces(line_color="#e377c2", line_width=3)
        st.plotly_chart(fig12, use_container_width=True)

        # CAFV Eligibility
        st.subheader("Clean Alternative Fuel Vehicle (CAFV) Eligibility")
        cafv_counts = filtered_df["cafv_eligibility"].value_counts()
        fig13 = px.pie(
            values=cafv_counts.values,
            names=cafv_counts.index,
            title="CAFV Eligibility Distribution",
        )
        st.plotly_chart(fig13, use_container_width=True)

    with tab5:
        st.subheader("Vehicle Data Table")

        # Display options
        col1, col2 = st.columns([3, 1])
        with col1:
            search = st.text_input("🔍 Search (VIN, Make, Model, City)", "")
        with col2:
            show_rows = st.selectbox("Rows per page", [10, 25, 50, 100], index=1)

        # Apply search filter
        display_df = filtered_df.copy()
        if search:
            mask = (
                display_df["vin"].str.contains(search, case=False, na=False)
                | display_df["make"].str.contains(search, case=False, na=False)
                | display_df["model"].str.contains(search, case=False, na=False)
                | display_df["city"].str.contains(search, case=False, na=False)
            )
            display_df = display_df[mask]

        # Select columns to display
        display_columns = [
            "vin",
            "model_year",
            "make",
            "model",
            "ev_type",
            "electric_range",
            "city",
            "county",
            "state",
            "postal_code",
        ]

        st.dataframe(
            display_df[display_columns].head(show_rows),
            use_container_width=True,
            height=400,
        )

        st.info(
            f"Showing {min(show_rows, len(display_df))} of {len(display_df):,} vehicles"
        )

        # Download button
        csv = display_df[display_columns].to_csv(index=False)
        st.download_button(
            label="📥 Download filtered data as CSV",
            data=csv,
            file_name=f"ev_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
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
