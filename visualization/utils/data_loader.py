import pandas as pd
import streamlit as st
from utils.database import get_connection


@st.cache_data(ttl=600)
def load_vehicle_data_summary():
    """Load aggregated summary data for visualizations"""
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()

    query = """
    SELECT 
        v.model_year,
        m.make,
        m.model,
        v.ev_type,
        v.electric_range,
        v.cafv_eligibility,
        l.city,
        l.county,
        l.state,
        l.postal_code,
        COUNT(*) as vehicle_count
    FROM vehicle v
    JOIN model m ON v.model_id = m.model_id
    JOIN location l ON v.location_id = l.location_id
    GROUP BY 
        v.model_year, m.make, m.model, v.ev_type, 
        v.electric_range, v.cafv_eligibility,
        l.city, l.county, l.state, l.postal_code
    """

    try:
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error loading summary data: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()


@st.cache_data(ttl=600)
def load_map_data(limit=None):
    """Load data for map visualization with improved error handling and multiple strategies"""
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()

    limit_clause = f"LIMIT {limit}" if limit else ""

    # Strategy 1: Try PostGIS/Geometry functions (ST_X, ST_Y)
    try:
        query = f"""
        SELECT 
            m.make,
            m.model,
            v.model_year,
            l.city,
            l.state,
            ST_X(l.vehicle_location::geometry) as longitude,
            ST_Y(l.vehicle_location::geometry) as latitude
        FROM vehicle v
        JOIN model m ON v.model_id = m.model_id
        JOIN location l ON v.location_id = l.location_id
        WHERE l.vehicle_location IS NOT NULL
        ORDER BY RANDOM()
        {limit_clause}
        """

        df = pd.read_sql(query, conn)

        if not df.empty:
            # Validate coordinates
            df = df[(df["longitude"].notna()) & (df["latitude"].notna())]
            df = df[(df["longitude"] >= -180) & (df["longitude"] <= 180)]
            df = df[(df["latitude"] >= -90) & (df["latitude"] <= 90)]

            if not df.empty:
                conn.close()
                return df

    except Exception as e:
        # PostGIS method failed, will try manual parsing
        pass

    # Strategy 2: Manual string parsing of POINT data
    try:
        query = f"""
        SELECT 
            m.make,
            m.model,
            v.model_year,
            l.city,
            l.state,
            l.vehicle_location::text as vehicle_location
        FROM vehicle v
        JOIN model m ON v.model_id = m.model_id
        JOIN location l ON v.location_id = l.location_id
        WHERE l.vehicle_location IS NOT NULL
        ORDER BY RANDOM()
        {limit_clause}
        """

        df = pd.read_sql(query, conn)

        if df.empty:
            conn.close()
            return pd.DataFrame()

        # Parse POINT format manually with robust error handling
        def parse_point_robust(point_str):
            if pd.isna(point_str):
                return pd.Series([None, None])
            try:
                # Handle various POINT formats
                clean = str(point_str).strip()

                # Remove POINT wrapper (case insensitive)
                if "POINT" in clean.upper():
                    clean = clean.upper().replace("POINT", "").strip()
                clean = clean.replace("(", "").replace(")", "").strip()

                # Split by space or comma
                parts = clean.replace(",", " ").split()

                if len(parts) >= 2:
                    try:
                        lon = float(parts[0])
                        lat = float(parts[1])

                        # Validate ranges
                        if -180 <= lon <= 180 and -90 <= lat <= 90:
                            return pd.Series([lon, lat])
                    except ValueError:
                        pass

            except Exception:
                pass

            return pd.Series([None, None])

        df[["longitude", "latitude"]] = df["vehicle_location"].apply(parse_point_robust)
        df = df.dropna(subset=["longitude", "latitude"])

        conn.close()
        return df

    except Exception as e:
        st.error(f"Error loading map data: {e}")
        try:
            conn.rollback()
        except:
            pass
        return pd.DataFrame()
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass


@st.cache_data(ttl=600)
def load_paginated_data(offset=0, limit=100, filters=None):
    """Load paginated vehicle data for table view"""
    conn = get_connection()
    if conn is None:
        return pd.DataFrame(), 0

    where_clause = "WHERE 1=1"
    params = []

    if filters:
        if filters.get("state") and filters["state"] != "All":
            where_clause += " AND l.state = %s"
            params.append(filters["state"])
        if filters.get("make") and filters["make"] != "All":
            where_clause += " AND m.make = %s"
            params.append(filters["make"])
        if filters.get("ev_type") and filters["ev_type"] != "All":
            where_clause += " AND v.ev_type = %s"
            params.append(filters["ev_type"])
        if filters.get("year_range") is not None:
            year_range = filters["year_range"]
            where_clause += " AND v.model_year BETWEEN %s AND %s"
            params.extend([int(year_range[0]), int(year_range[1])])
        if filters.get("search"):
            where_clause += """ AND (
                v.vin ILIKE %s OR 
                m.make ILIKE %s OR 
                m.model ILIKE %s OR 
                l.city ILIKE %s
            )"""
            search_term = f"%{filters['search']}%"
            params.extend([search_term] * 4)

    count_query = f"""
    SELECT COUNT(*) as total
    FROM vehicle v
    JOIN model m ON v.model_id = m.model_id
    JOIN location l ON v.location_id = l.location_id
    {where_clause}
    """

    data_query = f"""
    SELECT 
        v.vin,
        v.model_year,
        m.make,
        m.model,
        v.ev_type,
        v.electric_range,
        l.city,
        l.county,
        l.state,
        l.postal_code
    FROM vehicle v
    JOIN model m ON v.model_id = m.model_id
    JOIN location l ON v.location_id = l.location_id
    {where_clause}
    ORDER BY v.model_year DESC, m.make, m.model
    LIMIT {limit} OFFSET {offset}
    """

    try:
        cur = conn.cursor()
        cur.execute(count_query, params)
        total_count = cur.fetchone()[0]
        cur.close()

        df = pd.read_sql(data_query, conn, params=params)
        return df, total_count
    except Exception as e:
        st.error(f"Error loading paginated data: {e}")
        try:
            conn.rollback()
        except:
            pass
        return pd.DataFrame(), 0
    finally:
        if conn:
            conn.close()


@st.cache_data(ttl=600)
def get_summary_stats():
    """Get summary statistics"""
    conn = get_connection()
    if conn is None:
        return {}

    query = """
    SELECT 
        COUNT(*) as total_vehicles,
        COUNT(DISTINCT m.make) as total_makes,
        COUNT(DISTINCT m.model) as total_models,
        COUNT(DISTINCT l.state) as total_states,
        AVG(v.electric_range) as avg_range,
        MAX(v.model_year) as latest_year,
        MIN(v.model_year) as earliest_year
    FROM vehicle v
    JOIN model m ON v.model_id = m.model_id
    JOIN location l ON v.location_id = l.location_id
    """

    try:
        df = pd.read_sql(query, conn)
        return df.iloc[0].to_dict()
    except Exception as e:
        st.error(f"Error loading summary stats: {e}")
        return {}
    finally:
        if conn:
            conn.close()


def load_all_data():
    """Load all required data and return both aggregated and expanded dataframes"""
    df = load_vehicle_data_summary()

    if df.empty:
        return pd.DataFrame(), pd.DataFrame()

    # Expand aggregated data for filtering
    expanded_rows = []
    for _, row in df.iterrows():
        expanded_rows.extend([row.to_dict()] * int(row["vehicle_count"]))
    df_expanded = pd.DataFrame(expanded_rows)
    df_expanded = df_expanded.drop("vehicle_count", axis=1)

    return df, df_expanded