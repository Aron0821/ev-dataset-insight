import streamlit as st
import plotly.express as px
from utils.data_loader import load_map_data
from utils.map_debug import debug_map_data


def render_geographic_tab(filtered_df):
    """Render the geographic distribution tab"""
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
    with st.expander("🔍 Debug Map Data (Click if map doesn't work)", expanded=False):
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
                            f"Loaded {len(map_df):,} sample locations (random selection)"
                        )
                    else:
                        st.success(f"Loaded all {len(map_df):,} vehicle locations")

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
