import streamlit as st


def render_summary_metrics(filtered_df, stats):
    """Render summary statistics metrics"""
    st.header("Summary Statistics")
    col1, col2, col3, col4, col5 = st.columns(5)

    total_vehicles = int(filtered_df["vehicle_count"].sum())

    with col1:
        st.metric("Total Vehicles", f"{total_vehicles:,}")
    with col2:
        st.metric("Total Makes", stats.get("total_makes", 0))
    with col3:
        st.metric("Total Models", stats.get("total_models", 0))
    with col4:
        valid_range = filtered_df[filtered_df["electric_range"] > 0]
        if not valid_range.empty:
            weighted_avg = (
                valid_range["electric_range"] * valid_range["vehicle_count"]
            ).sum() / valid_range["vehicle_count"].sum()
            st.metric("Avg Range (mi)", f"{weighted_avg:.0f}")
        else:
            st.metric("Avg Range (mi)", "N/A")
    with col5:
        st.metric("States", stats.get("total_states", 0))
