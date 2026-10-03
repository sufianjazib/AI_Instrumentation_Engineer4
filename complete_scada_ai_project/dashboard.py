import plotly.graph_objects as go

def render_svg_schematic(level_pct: float, status: str) -> str:
    color_map = {
        "NORMAL": "#10B981",
        "FAULT": "#EF4444",
        "WARNING": "#F59E0B"
    }
    status_color = color_map.get(status, "#6B7280")
    fill_height = max(10, min(180, int((level_pct / 100.0) * 180)))
    y_pos = 220 - fill_height

    svg = f"""
    <svg width="100%" height="280" viewBox="0 0 500 280" xmlns="http://www.w3.org/2000/svg">
        <rect width="500" height="280" fill="#1e293b" rx="10"/>
        <rect x="150" y="40" width="200" height="180" fill="none" stroke="#94a3b8" stroke-width="4" rx="8"/>
        <rect x="152" y="{y_pos}" width="196" height="{fill_height}" fill="#0284c7" opacity="0.75" rx="4"/>
        <circle cx="250" cy="40" r="18" fill="{status_color}" stroke="#ffffff" stroke-width="2"/>
        <text x="250" y="45" font-size="11" fill="#ffffff" font-weight="bold" text-anchor="middle">LT-101</text>
        <line x1="250" y1="40" x2="250" y2="{y_pos}" stroke="#f59e0b" stroke-width="2" stroke-dasharray="4"/>
        <line x1="50" y1="80" x2="150" y2="80" stroke="#64748b" stroke-width="6"/>
        <polygon points="140,75 150,80 140,85" fill="#64748b"/>
        <text x="80" y="70" font-size="12" fill="#cbd5e1" font-weight="bold">Inlet Flow</text>
        <line x1="350" y1="190" x2="450" y2="190" stroke="#64748b" stroke-width="6"/>
        <polygon points="440,185 450,190 440,195" fill="#64748b"/>
        <text x="370" y="180" font-size="12" fill="#cbd5e1" font-weight="bold">Outlet Flow</text>
        <rect x="370" y="30" width="110" height="40" fill="#0f172a" rx="5" stroke="{status_color}" stroke-width="2"/>
        <text x="425" y="55" font-size="13" fill="{status_color}" font-weight="bold" text-anchor="middle">{status}</text>
        <text x="250" y="140" font-size="20" fill="#ffffff" font-weight="bold" text-anchor="middle">{level_pct}%</text>
    </svg>
    """
    return svg


def create_trend_chart(history: list, tag: str = "LT_101"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=history,
        mode='lines+markers',
        name='Current (mA)',
        line=dict(color='#3B82F6', width=3),
        marker=dict(size=8, color='#60A5FA')
    ))
    
    fig.add_hline(y=20.0, line_dash="dash", line_color="#EF4444", annotation_text="URV (20mA)")
    fig.add_hline(y=4.0, line_dash="dash", line_color="#EF4444", annotation_text="LRV (4mA)")
    fig.add_hline(y=3.6, line_dash="dot", line_color="#F59E0B", annotation_text="Underrange (3.6mA)")
    fig.add_hline(y=21.0, line_dash="dot", line_color="#F59E0B", annotation_text="Overrange (21.0mA)")

    fig.update_layout(
        title=f"Real-Time Signal Trend ({tag})",
        xaxis_title="Sample Window",
        yaxis_title="Current (mA)",
        template="plotly_dark",
        margin=dict(l=40, r=40, t=50, b=40),
        height=320
    )
    return fig
