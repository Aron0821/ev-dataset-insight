import streamlit as st
import plotly.express as px


def render_trends_tab(filtered_df):
    """Render the trends analysis tab"""
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
