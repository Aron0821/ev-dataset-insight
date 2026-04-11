import streamlit as st


def render_summary_metrics(filtered_df, stats):
    total_vehicles = int(filtered_df["vehicle_count"].sum())

    valid_range = filtered_df[filtered_df["electric_range"] > 0]
    if not valid_range.empty:
        weighted_avg = (
            valid_range["electric_range"] * valid_range["vehicle_count"]
        ).sum() / valid_range["vehicle_count"].sum()
        avg_range_val = f"{weighted_avg:.0f}"
    else:
        avg_range_val = "N/A"

    st.markdown(f"""
    <div style="
        display:grid;
        grid-template-columns:repeat(5,1fr);
        gap:1rem;
        margin:1.5rem 0 0.5rem 0;
    ">
        {_card("Total Vehicles",  f"{total_vehicles:,}", "#00f5d4", "+45% YoY")}
        {_card("Manufacturers",   str(stats.get("total_makes", 0)),   "#b8ff57", "unique makes")}
        {_card("Models",          str(stats.get("total_models", 0)),  "#7b6cff", "unique models")}
        {_card("Avg Range",       f"{avg_range_val} mi",              "#ffb830", "electric range")}
        {_card("States",          str(stats.get("total_states", 0)),  "#00f5d4", "coverage")}
    </div>
    """, unsafe_allow_html=True)


def _card(label, value, accent, sub):
    return f"""
    <div style="
        background:#14141e;
        border:1px solid rgba(255,255,255,0.07);
        border-radius:16px;
        padding:1.4rem 1.6rem;
        position:relative;
        overflow:hidden;
        transition:transform 0.2s, border-color 0.2s;
    ">
        <div style="
            position:absolute; top:0; left:0; right:0; height:2px;
            background:linear-gradient(90deg,{accent},transparent);
        "></div>
        <div style="
            font-family:'Syne',sans-serif; font-size:0.67rem; font-weight:700;
            letter-spacing:0.11em; text-transform:uppercase; color:#50506a;
            margin-bottom:0.65rem;
        ">{label}</div>
        <div style="
            font-family:'JetBrains Mono',monospace; font-size:1.9rem; font-weight:500;
            color:{accent}; letter-spacing:-0.02em; line-height:1; margin-bottom:0.45rem;
        ">{value}</div>
        <div style="
            font-family:'JetBrains Mono',monospace; font-size:0.71rem; color:#50506a;
        ">{sub}</div>
    </div>
    """