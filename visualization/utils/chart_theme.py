"""
Shared Plotly dark theme for consistent chart styling across all tabs.
"""

CHART_COLORS = {
    "electric": "#00f5d4",
    "volt": "#b8ff57",
    "plasma": "#7b6cff",
    "amber": "#ffb830",
    "crimson": "#ff5577",
    "sky": "#38bdf8",
}

PALETTE = [
    "#00f5d4", "#b8ff57", "#7b6cff", "#ffb830",
    "#ff5577", "#38bdf8", "#f472b6", "#a78bfa",
    "#34d399", "#fb923c",
]

DARK_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(
        family="JetBrains Mono, monospace",
        color="#8888aa",
        size=11,
    ),
    title=dict(
        font=dict(
            family="Syne, sans-serif",
            color="#f0f0f8",
            size=15,
        ),
        x=0,
        xanchor="left",
        pad=dict(b=12),
    ),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        linecolor="rgba(255,255,255,0.08)",
        tickcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.06)",
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        linecolor="rgba(255,255,255,0.08)",
        tickcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.06)",
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(255,255,255,0.08)",
        borderwidth=1,
        font=dict(size=11, color="#8888aa"),
    ),
    margin=dict(l=12, r=12, t=48, b=12),
    colorway=PALETTE,
    hoverlabel=dict(
        bgcolor="#16161f",
        bordercolor="rgba(0,245,212,0.3)",
        font=dict(family="JetBrains Mono, monospace", size=12, color="#f0f0f8"),
    ),
)


def apply_dark_theme(fig, height=420):
    """Apply the dark theme to any plotly figure."""
    fig.update_layout(height=height, **DARK_LAYOUT)
    fig.update_xaxes(
        gridcolor="rgba(255,255,255,0.04)",
        linecolor="rgba(255,255,255,0.08)",
        tickfont=dict(family="JetBrains Mono, monospace", size=10, color="#55556a"),
    )
    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.04)",
        linecolor="rgba(255,255,255,0.08)",
        tickfont=dict(family="JetBrains Mono, monospace", size=10, color="#55556a"),
    )
    return fig


def section_header(title, subtitle=None, icon=None):
    """Return HTML for a consistent section header."""
    icon_html = f'<span style="font-size:1.1rem; margin-right:0.5rem;">{icon}</span>' if icon else ""
    sub_html = f'<div style="font-family: JetBrains Mono, monospace; font-size:0.72rem; color:#55556a; margin-top:0.2rem;">{subtitle}</div>' if subtitle else ""
    return f"""
    <div style="
        padding: 0.25rem 0 1rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 1.25rem;
    ">
        <div style="
            font-family: Syne, sans-serif;
            font-size: 1.05rem;
            font-weight: 700;
            color: #f0f0f8;
            letter-spacing: -0.01em;
        ">{icon_html}{title}</div>
        {sub_html}
    </div>
    """