import streamlit as st
from datetime import datetime
from utils.data_loader import load_paginated_data


def render_data_table_tab(filter_values):
    """Render the data table tab with pagination"""
    st.subheader("Vehicle Data Table")

    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        search = st.text_input("Search (VIN, Make, Model, City)", "")
    with col2:
        rows_per_page = st.selectbox("Rows per page", [25, 50, 100, 250], index=0)
    with col3:
        page_number = st.number_input("Page", min_value=1, value=1, step=1)

    year_range = filter_values.get("year_range")
    if year_range is not None:
        try:
            if isinstance(year_range, (tuple, list)):
                year_min_val, year_max_val = int(year_range[0]), int(year_range[1])
            else:
                year_min_val, year_max_val = int(year_range), int(year_range)
            year_range_tuple = (year_min_val, year_max_val)
        except:
            year_range_tuple = None
    else:
        year_range_tuple = None

    table_filters = {
        "state": filter_values.get("state"),
        "make": filter_values.get("make"),
        "ev_type": filter_values.get("ev_type"),
        "year_range": year_range_tuple,
        "search": search if search else None,
    }

    offset = (page_number - 1) * rows_per_page

    with st.spinner("Loading data..."):
        display_df, total_count = load_paginated_data(
            offset=offset, limit=rows_per_page, filters=table_filters
        )

    if not display_df.empty:
        st.dataframe(display_df, use_container_width=True, height=400)

        total_pages = (total_count + rows_per_page - 1) // rows_per_page
        start_row = offset + 1
        end_row = min(offset + rows_per_page, total_count)

        col1, col2, col3 = st.columns([2, 2, 2])
        with col1:
            st.info(f"Showing {start_row:,} - {end_row:,} of {total_count:,} vehicles")
        with col2:
            st.info(f"Page {page_number:,} of {total_pages:,}")
        with col3:
            if st.button("Export Current Page to CSV"):
                csv = display_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"ev_data_page{page_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                )
    else:
        st.warning("No data found matching the current filters.")