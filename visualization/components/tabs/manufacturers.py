import streamlit as st
import plotly.express as px


def render_manufacturers_tab(filtered_df):
    """Render the manufacturers analysis tab"""
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