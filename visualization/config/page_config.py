import streamlit as st


def setup_page_config():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="Electric Vehicles Dashboard",
        page_icon="🚗",
        layout="wide",
        initial_sidebar_state="expanded",
    )
