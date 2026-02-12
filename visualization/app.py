import os
import sys
import streamlit as st

# Add the parent directory to the path to import db_connection
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from config.page_config import setup_page_config
from utils.data_loader import load_all_data, get_summary_stats
from components.sidebar import render_sidebar
from components.metrics import render_summary_metrics
from components.tabs.trends import render_trends_tab
from components.tabs.manufacturers import render_manufacturers_tab
from components.tabs.geographic import render_geographic_tab
from components.tabs.performance import render_performance_tab
from components.tabs.data_table import render_data_table_tab
from components.tabs.ai_analyst import render_ai_analyst_tab
from components.tabs.prediction import render_prediction_tab
from components.tabs.forecast import render_forecast_tab


def main():
    # Page configuration
    setup_page_config()

    st.title("Electric Vehicles Analysis Dashboard")
    st.markdown("---")

    # Load data
    with st.spinner("Loading data..."):
        df, df_expanded = load_all_data()
        stats = get_summary_stats()

    if df.empty:
        st.error("No data available. Please check your database connection and data.")
        return

    # Sidebar filters
    filter_values = render_sidebar(df_expanded)

    # Apply filters
    filtered_df = df.copy()
    if filter_values["state"] != "All":
        filtered_df = filtered_df[filtered_df["state"] == filter_values["state"]]
    if filter_values["make"] != "All":
        filtered_df = filtered_df[filtered_df["make"] == filter_values["make"]]
    if filter_values["ev_type"] != "All":
        filtered_df = filtered_df[filtered_df["ev_type"] == filter_values["ev_type"]]
    filtered_df = filtered_df[
        (filtered_df["model_year"] >= filter_values["year_range"][0])
        & (filtered_df["model_year"] <= filter_values["year_range"][1])
    ]

    # Summary metrics
    render_summary_metrics(filtered_df, stats)

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
        render_trends_tab(filtered_df)

    with tab2:
        render_manufacturers_tab(filtered_df)

    with tab3:
        render_geographic_tab(filtered_df)

    with tab4:
        render_performance_tab(filtered_df)

    with tab5:
        render_data_table_tab(filter_values)

    with tab6:
        render_ai_analyst_tab()

    with tab7:
        render_prediction_tab(df)

    with tab8:
        render_forecast_tab(df)

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
