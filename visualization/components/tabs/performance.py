import streamlit as st
import plotly.express as px
import pandas as pd


def render_performance_tab(filtered_df):
    """Render the performance/electric range analysis tab"""
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
                make_range = make_range.sort_values("avg_range", ascending=False).head(
                    10
                )

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
        st.metric("Battery Electric (BEV)", f"{int(bev_df['vehicle_count'].sum()):,}")
        st.metric("Plug-in Hybrid (PHEV)", f"{int(phev_df['vehicle_count'].sum()):,}")

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
