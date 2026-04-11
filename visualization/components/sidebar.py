import streamlit as st


def render_sidebar(df_expanded):
    st.sidebar.markdown("""
    <div style="padding:0.5rem 0 1.5rem 0; border-bottom:1px solid rgba(255,255,255,0.07);">
        <div style="
            font-family:'Syne',sans-serif; font-size:1rem; font-weight:800;
            letter-spacing:-0.01em; color:#eeeef8; margin-bottom:0.2rem;
        ">EV Analytics</div>
        <div style="
            font-family:'JetBrains Mono',monospace; font-size:0.68rem;
            color:#50506a; letter-spacing:0.08em; text-transform:uppercase;
        ">Filter & explore</div>
    </div>
    """, unsafe_allow_html=True)

    def _label(text):
        st.sidebar.markdown(f"""
        <div style="
            font-family:'Syne',sans-serif; font-size:0.67rem; font-weight:700;
            letter-spacing:0.1em; text-transform:uppercase; color:#8888aa;
            margin:1.1rem 0 0.3rem 0;
        ">{text}</div>
        """, unsafe_allow_html=True)

    _label("State")
    states = ["All"] + sorted(df_expanded["state"].unique().tolist())
    selected_state = st.sidebar.selectbox("State", states, label_visibility="collapsed")

    _label("Manufacturer")
    makes = ["All"] + sorted(df_expanded["make"].unique().tolist())
    selected_make = st.sidebar.selectbox("Make", makes, label_visibility="collapsed")

    _label("EV Type")
    ev_types = ["All"] + sorted(df_expanded["ev_type"].unique().tolist())
    selected_ev_type = st.sidebar.selectbox("EV Type", ev_types, label_visibility="collapsed")

    _label("Model Year Range")
    min_year = int(df_expanded["model_year"].min())
    max_year = int(df_expanded["model_year"].max())
    year_range = st.sidebar.slider(
        "Year Range", min_value=min_year, max_value=max_year,
        value=(min_year, max_year), label_visibility="collapsed",
    )

    # ── Dataset scope pill ───────────────────────────────────
    st.sidebar.markdown("<div style='margin-top:1.75rem;'></div>", unsafe_allow_html=True)
    st.sidebar.markdown(f"""
    <div style="
        background:rgba(0,245,212,0.05); border:1px solid rgba(0,245,212,0.14);
        border-radius:12px; padding:0.9rem 1rem;
    ">
        <div style="
            font-family:'Syne',sans-serif; font-size:0.67rem; font-weight:700;
            letter-spacing:0.1em; text-transform:uppercase;
            color:#00f5d4; margin-bottom:0.55rem;
        ">Dataset Scope</div>
        <div style="display:flex; flex-direction:column; gap:0.3rem;">
            <div style="display:flex; justify-content:space-between;
                        font-family:'JetBrains Mono',monospace; font-size:0.75rem;">
                <span style="color:#50506a;">States</span>
                <span style="color:#eeeef8;">{len(df_expanded['state'].unique())}</span>
            </div>
            <div style="display:flex; justify-content:space-between;
                        font-family:'JetBrains Mono',monospace; font-size:0.75rem;">
                <span style="color:#50506a;">Makes</span>
                <span style="color:#eeeef8;">{len(df_expanded['make'].unique())}</span>
            </div>
            <div style="display:flex; justify-content:space-between;
                        font-family:'JetBrains Mono',monospace; font-size:0.75rem;">
                <span style="color:#50506a;">Years</span>
                <span style="color:#eeeef8;">{min_year} – {max_year}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    return {
        "state": selected_state,
        "make": selected_make,
        "ev_type": selected_ev_type,
        "year_range": year_range,
    }