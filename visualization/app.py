import os
import sys
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
    setup_page_config()

    # ── Hero Header ──────────────────────────────────────────
    st.markdown("""
    <div style="padding: 0.75rem 0 2rem 0;">
        <div style="
            display: inline-block;
            background: rgba(0,245,212,0.08);
            border: 1px solid rgba(0,245,212,0.2);
            border-radius: 999px;
            padding: 0.28rem 0.85rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.68rem;
            letter-spacing: 0.12em;
            color: #00f5d4;
            text-transform: uppercase;
            margin-bottom: 0.85rem;
        ">Real-time Intelligence Platform</div>
        <h1 style="margin:0; padding:0;">EV Analytics Dashboard</h1>
        <p style="
            margin: 0.55rem 0 0 0;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            color: #50506a;
            letter-spacing: 0.05em;
            max-width: 520px;
        ">Washington State electric vehicle registrations — explore trends,
        performance, and geographic distribution across 270K+ records.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Data Load ────────────────────────────────────────────
    with st.spinner("Loading data..."):
        df, df_expanded = load_all_data()
        stats = get_summary_stats()

    if df.empty:
        st.error("No data available. Please check your database connection.")
        return

    # ── Sidebar ──────────────────────────────────────────────
    filter_values = render_sidebar(df_expanded)

    # ── Apply Filters ────────────────────────────────────────
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

    # ── Metrics ──────────────────────────────────────────────
    render_summary_metrics(filtered_df, stats)

    st.markdown(
        "<div style='margin: 2rem 0 0 0; border-top: 1px solid rgba(255,255,255,0.07);'></div>",
        unsafe_allow_html=True,
    )

    # ── Tabs ─────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "Trends",
        "Manufacturers",
        "Geographic",
        "Performance",
        "Data Table",
        "AI Analyst",
        "Range Prediction",
        "Adoption Forecast",
    ])

    with tab1:  render_trends_tab(filtered_df)
    with tab2:  render_manufacturers_tab(filtered_df)
    with tab3:  render_geographic_tab(filtered_df)
    with tab4:  render_performance_tab(filtered_df)
    with tab5:  render_data_table_tab(filter_values)
    with tab6:  render_ai_analyst_tab()
    with tab7:  render_prediction_tab(df)
    with tab8:  render_forecast_tab(df)

    # ── Footer ───────────────────────────────────────────────
    st.markdown("""
    <div style="
        margin-top: 4rem;
        padding: 1.25rem 0;
        border-top: 1px solid rgba(255,255,255,0.07);
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 0.5rem;
    ">
        <span style="font-family:'JetBrains Mono',monospace; font-size:0.72rem; color:#50506a;">
            EV Analytics &nbsp;&middot;&nbsp; Data synced in real-time
        </span>
        <span style="font-family:'JetBrains Mono',monospace; font-size:0.72rem; color:#50506a;">
            Built with <span style="color:#00f5d4;">Streamlit</span>
            &nbsp;&middot;&nbsp;
            Powered by <span style="color:#b8ff57;">PostgreSQL</span>
        </span>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()