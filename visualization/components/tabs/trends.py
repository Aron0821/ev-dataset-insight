import streamlit as st
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
from utils.chart_theme import apply_dark_theme, section_header, PALETTE


def render_trends_tab(filtered_df):
    st.markdown(section_header("Registration Trends", "EV adoption over time by year and type", "📈"), unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        year_data = (
            filtered_df.groupby("model_year")["vehicle_count"]
            .sum().sort_index().reset_index()
        )
        year_data.columns = ["model_year", "count"]
        fig1 = px.bar(
            year_data, x="model_year", y="count",
            labels={"model_year": "Model Year", "count": "Vehicles"},
            title="Vehicles by Model Year",
        )
        fig1.update_traces(
            marker_color=PALETTE[0],
            marker_line_width=0,
            opacity=0.85,
        )
        apply_dark_theme(fig1)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        ev_type_data = filtered_df.groupby("ev_type")["vehicle_count"].sum()
        fig2 = px.pie(
            values=ev_type_data.values,
            names=ev_type_data.index,
            title="Distribution by EV Type",
            hole=0.55,
            color_discrete_sequence=PALETTE,
        )
        fig2.update_traces(
            textfont=dict(family="JetBrains Mono, monospace", size=11),
        )
        apply_dark_theme(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    trend_data = (
        filtered_df.groupby(["model_year", "ev_type"])["vehicle_count"]
        .sum().reset_index()
    )
    fig3 = px.line(
        trend_data, x="model_year", y="vehicle_count", color="ev_type",
        title="EV Registration Trends by Type",
        labels={"model_year": "Model Year", "vehicle_count": "Vehicles"},
        color_discrete_sequence=PALETTE,
    )
    fig3.update_traces(line_width=2.5)
    apply_dark_theme(fig3, height=380)
    st.plotly_chart(fig3, use_container_width=True)