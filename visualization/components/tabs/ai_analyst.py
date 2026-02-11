import streamlit as st
import sys
import os

# Add chatbot to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from chatbot.intelligent_chatbot import EVChatbot
from utils.database import get_connection


def render_ai_analyst_tab():
    """Render the AI analyst chatbot tab with intelligent query handling"""
    st.subheader("🤖 AI Electric Vehicle Analyst")
    
    st.info("""
    Ask me anything! I can help with:
    - 💡 General EV knowledge (What is an EV? How do they work?)
    - 📊 Database queries (How many Teslas? Average range by year?)
    - 🔍 Custom analysis (Show me trends, patterns, insights)
    """)

    # Add refresh button for database connection issues
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("Refresh", help="Reset chatbot connection"):
            if "chatbot" in st.session_state:
                del st.session_state.chatbot
            if "messages" in st.session_state:
                st.session_state.messages = []
            st.rerun()

    # Initialize chatbot
    if "chatbot" not in st.session_state:
        try:
            db = get_connection()
            if db:
                st.session_state.chatbot = EVChatbot(db)
                st.success("Chatbot connected")
            else:
                st.error("❌ Could not connect to database. Please check your database settings.")
                return
        except Exception as e:
            st.error(f"❌ Error initializing chatbot: {str(e)}")
            st.info("💡 Try clicking the Refresh button above")
            return
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
            # Show SQL if available
            if msg.get("sql"):
                with st.expander("🔧 SQL Query Used"):
                    st.code(msg["sql"], language="sql")
            
            # Show raw data if available
            if msg.get("data") and msg["data"].get("rows"):
                with st.expander(f"📊 Raw Data ({len(msg['data']['rows'])} rows)"):
                    import pandas as pd
                    df = pd.DataFrame(
                        msg["data"]["rows"],
                        columns=msg["data"]["columns"]
                    )
                    st.dataframe(df, use_container_width=True)

    # Chat input
    if prompt := st.chat_input("Ask anything about electric vehicles..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.write(prompt)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                try:
                    response = st.session_state.chatbot.chat(prompt)
                    
                    answer = response["answer"]
                    query_type = response["type"]
                    sql = response.get("sql")
                    data = response.get("data")
                    
                    # Display answer
                    st.write(answer)
                    
                    # Show SQL if available
                    if sql:
                        with st.expander("🔧 SQL Query Used"):
                            st.code(sql, language="sql")
                    
                    # Show raw data if available
                    if data and data.get("rows"):
                        with st.expander(f"📊 Raw Data ({len(data['rows'])} rows)"):
                            import pandas as pd
                            df = pd.DataFrame(
                                data["rows"],
                                columns=data["columns"]
                            )
                            st.dataframe(df, use_container_width=True)
                    
                    # Add badge for query type
                    type_badges = {
                        "general": "💡 General Knowledge",
                        "data_query": "📊 Database Query",
                        "hybrid": "🔍 Hybrid Analysis",
                        "error": "⚠️ Error"
                    }
                    st.caption(type_badges.get(query_type, ""))
                    
                except Exception as e:
                    answer = f"Sorry, I encountered an error: {str(e)}"
                    sql = None
                    data = None
                    st.error(answer)

        # Save assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sql": sql,
            "data": data
        })