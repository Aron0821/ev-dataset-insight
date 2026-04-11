import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.database import get_connection
from utils.chart_theme import section_header

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
try:
    from chatbot.intelligent_chatbot import EVChatbot
except ImportError:
    EVChatbot = None


def render_ai_analyst_tab():
    st.markdown(
        section_header("AI Electric Vehicle Analyst", "Ask anything — general knowledge or live database queries", ""),
        unsafe_allow_html=True,
    )

    # ── Capability pills ─────────────────────────────────────
    st.markdown("""
    <div style="display:flex; gap:0.6rem; flex-wrap:wrap; margin-bottom:1.75rem;">
        <div style="
            background:rgba(0,245,212,0.07); border:1px solid rgba(0,245,212,0.22);
            border-radius:999px; padding:0.32rem 0.9rem;
            font-family:'JetBrains Mono',monospace; font-size:0.71rem;
            color:#00f5d4; letter-spacing:0.04em;
        ">General EV Knowledge</div>
        <div style="
            background:rgba(184,255,87,0.07); border:1px solid rgba(184,255,87,0.22);
            border-radius:999px; padding:0.32rem 0.9rem;
            font-family:'JetBrains Mono',monospace; font-size:0.71rem;
            color:#b8ff57; letter-spacing:0.04em;
        ">Live Database Queries</div>
        <div style="
            background:rgba(123,108,255,0.07); border:1px solid rgba(123,108,255,0.22);
            border-radius:999px; padding:0.32rem 0.9rem;
            font-family:'JetBrains Mono',monospace; font-size:0.71rem;
            color:#a89dff; letter-spacing:0.04em;
        ">Trend &amp; Pattern Analysis</div>
    </div>
    """, unsafe_allow_html=True)

    if EVChatbot is None:
        st.error("Chatbot module not found. Check your import path for `chatbot.intelligent_chatbot`.")
        return

    # ── Reset button ──────────────────────────────────────────
    col_main, col_btn = st.columns([9, 1])
    with col_btn:
        if st.button("Reset", key="chat_reset", type="secondary"):
            for key in ("chatbot", "messages"):
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    # ── Init chatbot ──────────────────────────────────────────
    if "chatbot" not in st.session_state:
        try:
            db = get_connection()
            if db:
                st.session_state.chatbot = EVChatbot(db)
            else:
                st.error("Could not connect to database.")
                return
        except Exception as e:
            st.error(f"Error initializing chatbot: {e}")
            return

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # ── Welcome card (shown when no messages yet) ─────────────
    if not st.session_state.messages:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(123,108,255,0.08), rgba(0,245,212,0.05));
            border: 1px solid rgba(123,108,255,0.2);
            border-radius: 16px;
            padding: 1.75rem 2rem;
            margin-bottom: 1.5rem;
        ">
            <div style="
                font-family:'Syne',sans-serif; font-size:1.05rem;
                font-weight:700; color:#eeeef8; margin-bottom:0.6rem;
            ">Hello! I'm your EV data analyst.</div>
            <p style="
                font-family:'Syne',sans-serif; font-size:0.85rem;
                color:#8888aa; line-height:1.7; margin:0 0 1.1rem 0;
            ">I can answer questions about electric vehicles and query the live database for specific stats. Try one of these:</p>
            <div style="display:flex; flex-direction:column; gap:0.5rem;">
                <div style="
                    background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08);
                    border-radius:10px; padding:0.55rem 0.9rem;
                    font-family:'JetBrains Mono',monospace; font-size:0.78rem; color:#8888aa;
                ">"How many Tesla vehicles are registered?"</div>
                <div style="
                    background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08);
                    border-radius:10px; padding:0.55rem 0.9rem;
                    font-family:'JetBrains Mono',monospace; font-size:0.78rem; color:#8888aa;
                ">"What is the average electric range by manufacturer?"</div>
                <div style="
                    background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08);
                    border-radius:10px; padding:0.55rem 0.9rem;
                    font-family:'JetBrains Mono',monospace; font-size:0.78rem; color:#8888aa;
                ">"Explain the difference between BEV and PHEV"</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Chat history ──────────────────────────────────────────
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("sql"):
                with st.expander("View SQL query"):
                    st.code(msg["sql"], language="sql")
            if msg.get("data") and msg["data"].get("rows"):
                with st.expander(f"View raw data  ({len(msg['data']['rows'])} rows)"):
                    import pandas as pd
                    df = pd.DataFrame(msg["data"]["rows"], columns=msg["data"]["columns"])
                    st.dataframe(df, use_container_width=True)

    # ── Chat input ────────────────────────────────────────────
    if prompt := st.chat_input("Ask anything about electric vehicles..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.chatbot.chat(prompt)
                    answer     = response["answer"]
                    query_type = response["type"]
                    sql        = response.get("sql")
                    data       = response.get("data")

                    st.write(answer)

                    if sql:
                        with st.expander("View SQL query"):
                            st.code(sql, language="sql")
                    if data and data.get("rows"):
                        with st.expander(f"View raw data ({len(data['rows'])} rows)"):
                            import pandas as pd
                            df = pd.DataFrame(data["rows"], columns=data["columns"])
                            st.dataframe(df, use_container_width=True)

                    type_labels = {
                        "general":    ("General Knowledge",  "#00f5d4"),
                        "data_query": ("Database Query",     "#b8ff57"),
                        "hybrid":     ("Hybrid Analysis",    "#a89dff"),
                        "error":      ("Error",              "#ff6b6b"),
                    }
                    label, color = type_labels.get(query_type, ("Response", "#8888aa"))
                    st.markdown(
                        f'<span style="font-family:JetBrains Mono,monospace;font-size:0.7rem;'
                        f'color:{color};background:rgba(255,255,255,0.04);border:1px solid '
                        f'rgba(255,255,255,0.1);border-radius:6px;padding:0.2rem 0.5rem;">'
                        f'{label}</span>',
                        unsafe_allow_html=True,
                    )

                except Exception as e:
                    answer = f"Error: {e}"
                    sql = None
                    data = None
                    st.error(answer)

        st.session_state.messages.append({
            "role": "assistant", "content": answer, "sql": sql, "data": data
        })