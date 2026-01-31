import os
import sys
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
import plotly.graph_objects as go


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
    """Load data for map visualization"""
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()

    limit_clause = f"LIMIT {limit}" if limit else ""

    query = f"""
    SELECT 
        m.make,
        m.model,
        v.model_year,
        l.city,
        l.state,
        ST_X(l.vehicle_location) as longitude,
        ST_Y(l.vehicle_location) as latitude
    FROM vehicle v
    JOIN model m ON v.model_id = m.model_id
    JOIN location l ON v.location_id = l.location_id
    WHERE l.vehicle_location IS NOT NULL
    ORDER BY RANDOM()
    {limit_clause}
    """

    try:
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error loading map data: {e}")
        # Try to rollback the transaction
        try:
            conn.rollback()
        except:
            pass
        return pd.DataFrame()
    finally:
        if conn:
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
            # Ensure year values are integers
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

    # Get total count
    count_query = f"""
    SELECT COUNT(*) as total
    FROM vehicle v
    JOIN model m ON v.model_id = m.model_id
    JOIN location l ON v.location_id = l.location_id
    {where_clause}
    """

    # Get paginated data
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
        # Try to rollback the transaction
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

    # Expand aggregated data for filtering (weighted by vehicle_count)
    expanded_rows = []
    for _, row in df.iterrows():
        expanded_rows.extend([row.to_dict()] * int(row["vehicle_count"]))
    df_expanded = pd.DataFrame(expanded_rows)
    df_expanded = df_expanded.drop("vehicle_count", axis=1)

    # Sidebar filters
    st.sidebar.header("Filters")

    # State filter
    states = ["All"] + sorted(df_expanded["state"].unique().tolist())
    selected_state = st.sidebar.selectbox("Select State", states)

    # Make filter
    makes = ["All"] + sorted(df_expanded["make"].unique().tolist())
    selected_make = st.sidebar.selectbox("Select Make", makes)

    # EV Type filter
    ev_types = ["All"] + sorted(df_expanded["ev_type"].unique().tolist())
    selected_ev_type = st.sidebar.selectbox("Select EV Type", ev_types)

    # Year range filter
    min_year = int(df_expanded["model_year"].min())
    max_year = int(df_expanded["model_year"].max())
    year_range = st.sidebar.slider(
        "Select Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
    )

    # Apply filters to aggregated data
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

    # Calculate total vehicles from aggregated data
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
        # Calculate weighted average for electric range
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

    # Tabs for different visualizations
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Trends",
        "🏭 Manufacturers",
        "🗺️ Geographic",
        "⚡ Performance",
        "📋 Data Table",
        "🤖 AI Analyst"
    ])

    with tab1:
        st.subheader("Vehicle Registration Trends")

        col1, col2 = st.columns(2)

        with col1:
            # Vehicles by year - aggregate counts
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
            # EV Type distribution
            ev_type_data = filtered_df.groupby("ev_type")["vehicle_count"].sum()
            fig2 = px.pie(
                values=ev_type_data.values,
                names=ev_type_data.index,
                title="Distribution by EV Type",
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Trend over time by EV type
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
            # Top 10 makes
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
            # Market share of top manufacturers
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

        # Top models
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
            # Vehicles by state
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
            # Vehicles by county (top 10)
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

        # Map visualization
        st.subheader("Vehicle Locations Map")

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
            # Determine limit based on user selection
            limit = 5000 if "Sample" in map_option else None

            with st.spinner("Loading map data..."):
                map_df = load_map_data(limit=limit)

                if not map_df.empty:
                    if limit:
                        st.info(
                            f"📍 Showing {len(map_df):,} sample locations (random selection)"
                        )
                    else:
                        st.info(f"📍 Showing all {len(map_df):,} vehicle locations")

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
        else:
            st.info(
                "👆 Select your preferred data size and click 'Load Map' to view the interactive map"
            )

    with tab4:
        st.subheader("Electric Range Analysis")

        # Check if there's any range data
        total_with_range = filtered_df[filtered_df["electric_range"] > 0][
            "vehicle_count"
        ].sum()
        total_vehicles = filtered_df["vehicle_count"].sum()

        st.info(
            f"📊 {int(total_with_range):,} out of {int(total_vehicles):,} vehicles have reported electric range data ({total_with_range/total_vehicles*100:.1f}%)"
        )

        # Separate data into BEV and PHEV for better analysis
        bev_df = filtered_df[
            filtered_df["ev_type"] == "Battery Electric Vehicle (BEV)"
        ].copy()
        phev_df = filtered_df[
            filtered_df["ev_type"] == "Plug-in Hybrid Electric Vehicle (PHEV)"
        ].copy()

        # Remove zero ranges for BEVs (should all have range)
        bev_range_df = bev_df[bev_df["electric_range"] > 0].copy()
        # For PHEVs, include all since many may have 0 reported range
        phev_range_df = phev_df[phev_df["electric_range"] > 0].copy()

        # Combine for overall analysis
        range_df = filtered_df[filtered_df["electric_range"] > 0].copy()

        if not range_df.empty:
            col1, col2 = st.columns(2)

            with col1:
                # Range distribution - expand for histogram
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
                # Average range by make (top 10) - weighted average
                # Calculate weighted average manually for each make
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

            # Range trend over years - weighted average
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

        # EV Type breakdown - always show this
        st.subheader("Vehicle Type Distribution")
        col1, col2 = st.columns(2)

        with col1:
            # EV type counts
            ev_type_counts = filtered_df.groupby("ev_type")["vehicle_count"].sum()
            fig_ev_type = px.pie(
                values=ev_type_counts.values,
                names=ev_type_counts.index,
                title="BEV vs PHEV Distribution",
            )
            st.plotly_chart(fig_ev_type, use_container_width=True)

        with col2:
            # Show statistics
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

        # CAFV Eligibility
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

        # Display options
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            search = st.text_input("Search (VIN, Make, Model, City)", "")
        with col2:
            rows_per_page = st.selectbox("Rows per page", [25, 50, 100, 250], index=0)
        with col3:
            page_number = st.number_input("Page", min_value=1, value=1, step=1)

        # Prepare filters for pagination
        # Extract year range values safely
        if year_range is not None:
            try:
                # Handle tuple/list from slider
                if isinstance(year_range, (tuple, list)):
                    year_min, year_max = int(year_range[0]), int(year_range[1])
                else:
                    # Handle if it's a different type
                    year_min, year_max = int(year_range), int(year_range)
                year_range_tuple = (year_min, year_max)
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

        # Calculate offset
        offset = (page_number - 1) * rows_per_page

        # Load paginated data
        with st.spinner("Loading data..."):
            display_df, total_count = load_paginated_data(
                offset=offset, limit=rows_per_page, filters=table_filters
            )

        if not display_df.empty:
            # Display table
            st.dataframe(display_df, use_container_width=True, height=400)

            # Pagination info
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
    
    with tab6:
        st.subheader("AI Electric Vehicle Analyst")

        retriever, llm = load_rag()

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

                    docs = retriever.invoke(prompt)

                    context = "\n\n".join(
                        [d.page_content for d in docs]
                    )

                    final_prompt = f"""
                    You are an EV data expert.

                    Answer ONLY using this dataset.
                    If unknown, say you couldn't find it.

                    DATA:
                    {context}

                    QUESTION:
                    {prompt}
                    """

                    response = llm.invoke(final_prompt).content
                    st.write(response)

            st.session_state.messages.append(
                {"role": "assistant", "content": response}
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


@st.cache_resource
def load_rag():

    from langchain_groq import ChatGroq
    from chatbot.retriever import load_vector_store

    vector_db = load_vector_store()

    retriever = vector_db.as_retriever(search_kwargs={"k": 5})

    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model="llama-3.1-8b-instant",
        temperature=0
    )

    return retriever, llm


    


if __name__ == "__main__":
    main()
