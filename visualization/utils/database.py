import os
import sys
import streamlit as st

# Add the parent directory to the path to import db_connection
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.src.scripts.util.db_connection import db_connect


def get_connection():
    """Establish database connection using existing db_connect function"""
    try:
        conn = db_connect()
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        st.info(
            "Please check your database connection settings in db.src.scripts.util.db_connection"
        )
        return None
