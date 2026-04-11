import streamlit as st
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
from utils.chart_theme import apply_dark_theme, section_header, PALETTE


def render_manufacturers_tab(filtered_df):
    st.markdown(section_header("Manufacturer Analysis", "Market share and model breakdown", "🏭"), unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        top_makes = (
            filtered_df.groupby("make")["vehicle_count"]
            .sum().sort_values(ascending=False).head(10).reset_index()
        )
        top_makes.columns = ["make", "count"]
        fig4 = px.bar(
            top_makes, x="count", y="make", orientation="h",
            labels={"count": "Vehicles", "make": "Make"},
            title="Top 10 Manufacturers",
            color="count",
            color_continuous_scale=[[0, "#1a2a2a"], [0.5, "#00a08a"], [1, "#00f5d4"]],
        )
        fig4.update_traces(marker_line_width=0)
        fig4.update_coloraxes(showscale=False)
        apply_dark_theme(fig4)
        st.plotly_chart(fig4, use_container_width=True)

    with col2:
        top_5_makes = (
            filtered_df.groupby("make")["vehicle_count"]
            .sum().sort_values(ascending=False).head(5)
        )
        fig5 = px.pie(
            values=top_5_makes.values,
            names=top_5_makes.index,
            title="Market Share — Top 5",
            hole=0.5,
            color_discrete_sequence=PALETTE,
        )
        apply_dark_theme(fig5)
        st.plotly_chart(fig5, use_container_width=True)

    st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)
    st.markdown(section_header("Top 15 Models", "Most registered EV models in the dataset", "🚗"), unsafe_allow_html=True)

    filtered_df = filtered_df.copy()
    filtered_df["make_model"] = filtered_df["make"] + "  " + filtered_df["model"]
    top_models = (
        filtered_df.groupby("make_model")["vehicle_count"]
        .sum().sort_values(ascending=False).head(15).reset_index()
    )
    top_models.columns = ["make_model", "count"]
    fig6 = px.bar(
        top_models, x="count", y="make_model", orientation="h",
        labels={"count": "Vehicles", "make_model": "Model"},
        title="Top 15 Vehicle Models",
        color="count",
        color_continuous_scale=[[0, "#1a1a2e"], [0.5, "#5c4bc4"], [1, "#b8ff57"]],
    )
    fig6.update_traces(marker_line_width=0)
    fig6.update_coloraxes(showscale=False)
    apply_dark_theme(fig6, height=500)
    st.plotly_chart(fig6, use_container_width=True)