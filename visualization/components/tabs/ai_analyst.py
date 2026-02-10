import streamlit as st
import requests


API_URL = "http://localhost:8000/query"


def render_ai_analyst_tab():
    """Render the AI analyst chatbot tab"""
    st.subheader("AI Electric Vehicle Analyst")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Ask anything about EV data..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing EV dataset..."):
                try:
                    response = requests.post(
                        API_URL, json={"question": prompt}, timeout=60
                    )
                    response.raise_for_status()

                    data = response.json()
                    answer = data.get("answer")
                    if isinstance(answer, dict) and "content" in answer:
                        answer = answer["content"]

                    st.write(answer)

                except Exception as e:
                    answer = "Sorry, I couldn't process that question right now."
                    st.error(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})