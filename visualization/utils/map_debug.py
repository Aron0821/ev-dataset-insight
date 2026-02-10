import streamlit as st
import pandas as pd
from utils.database import get_connection


def debug_map_data():
    """Debug function to check map data availability - shows detailed diagnostics"""
    conn = get_connection()
    if not conn:
        st.error("Cannot connect to database")
        return

    try:
        # Check 1: Count total vehicles with location data
        st.write("### 📊 Location Data Statistics")
        count_query = """
        SELECT 
            COUNT(*) as total_locations,
            COUNT(CASE WHEN vehicle_location IS NOT NULL THEN 1 END) as with_coords,
            COUNT(CASE WHEN vehicle_location IS NULL THEN 1 END) as without_coords
        FROM location
        """
        count_df = pd.read_sql(count_query, conn)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Locations", f"{count_df['total_locations'].iloc[0]:,}")
        with col2:
            st.metric("With Coordinates", f"{count_df['with_coords'].iloc[0]:,}")
        with col3:
            st.metric("Without Coordinates", f"{count_df['without_coords'].iloc[0]:,}")

        if count_df["with_coords"].iloc[0] == 0:
            st.error("❌ No location data found in database!")
            st.info("The vehicle_location column is NULL for all records.")
            return

        # Check 2: Sample location data format
        st.write("### 🔍 Sample Location Data")
        sample_query = """
        SELECT 
            city,
            state,
            vehicle_location::text as location_raw
        FROM location 
        WHERE vehicle_location IS NOT NULL 
        LIMIT 5
        """
        sample_df = pd.read_sql(sample_query, conn)
        st.dataframe(sample_df, use_container_width=True)

        # Check 3: Test POINT parsing on sample
        if not sample_df.empty:
            st.write("### 🧪 Parsing Test")
            sample_point = sample_df["location_raw"].iloc[0]
            st.code(f"Raw value: {sample_point}")

            # Try to parse it
            def parse_test(point_str):
                try:
                    clean = str(point_str).strip()
                    if "POINT" in clean.upper():
                        clean = clean.upper().replace("POINT", "").strip()
                    clean = clean.replace("(", "").replace(")", "").strip()
                    parts = clean.replace(",", " ").split()
                    if len(parts) >= 2:
                        lon, lat = float(parts[0]), float(parts[1])
                        return lon, lat
                except Exception as e:
                    return None, None, str(e)
                return None, None

            result = parse_test(sample_point)
            if len(result) == 2:
                lon, lat = result
                if lon is not None:
                    st.success(
                        f"✅ Successfully parsed: Longitude = {lon}, Latitude = {lat}"
                    )
                else:
                    st.error("❌ Failed to parse coordinates")
            else:
                st.error(f"❌ Parse error: {result[2]}")

        # Check 4: Location table schema
        st.write("### 📋 Location Table Schema")
        schema_query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'location'
        ORDER BY ordinal_position
        """
        schema_df = pd.read_sql(schema_query, conn)
        st.dataframe(schema_df, use_container_width=True)

        # Check 5: Test actual query used by map
        st.write("### 🗺️ Map Query Test (First 3 Results)")
        test_query = """
        SELECT 
            m.make,
            m.model,
            v.model_year,
            l.city,
            l.state,
            l.vehicle_location::text as location
        FROM vehicle v
        JOIN model m ON v.model_id = m.model_id
        JOIN location l ON v.location_id = l.location_id
        WHERE l.vehicle_location IS NOT NULL
        LIMIT 3
        """
        test_df = pd.read_sql(test_query, conn)
        st.dataframe(test_df, use_container_width=True)

        st.success("✅ Debug check complete!")

    except Exception as e:
        st.error(f"Debug error: {e}")
        import traceback

        st.code(traceback.format_exc())
    finally:
        conn.close()