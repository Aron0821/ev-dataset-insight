import streamlit as st


def render_sidebar(df_expanded):
    """Render sidebar with filters and return selected filter values"""
    st.sidebar.header("Filters")

    states = ["All"] + sorted(df_expanded["state"].unique().tolist())
    selected_state = st.sidebar.selectbox("Select State", states)

    makes = ["All"] + sorted(df_expanded["make"].unique().tolist())
    selected_make = st.sidebar.selectbox("Select Make", makes)

    ev_types = ["All"] + sorted(df_expanded["ev_type"].unique().tolist())
    selected_ev_type = st.sidebar.selectbox("Select EV Type", ev_types)

    min_year = int(df_expanded["model_year"].min())
    max_year = int(df_expanded["model_year"].max())
    year_range = st.sidebar.slider(
        "Select Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
    )

    return {
        "state": selected_state,
        "make": selected_make,
        "ev_type": selected_ev_type,
        "year_range": year_range,
    }