"""
Plotly Sci-Fi Cyberpunk Theme Module
Defines dark cyan/orange/purple sci-fi color palette and unified layout template.
"""

import plotly.graph_objects as go
import plotly.io as pio

# Color Tokens matching reference picture
DARK_BG = "#040711"
CARD_BG = "rgba(10, 16, 35, 0.75)"
ACCENT_CYAN = "#00f2fe"
ACCENT_BLUE = "#00c6ff"
ACCENT_PURPLE = "#a855f7"
ACCENT_ORANGE = "#ff6b35"
ACCENT_PINK = "#ff0844"
ACCENT_AMBER = "#ffb199"
ACCENT_GREEN = "#00e676"
SEDENTARY_DARK = "rgba(30, 41, 59, 0.75)"
TEXT_COLOR = "#f1f5f9"
MUTED_TEXT = "#94a3b8"
GRID_COLOR = "rgba(0, 242, 254, 0.1)"

# Color sequences for categorical charts
COLOR_SEQUENCE = [ACCENT_CYAN, ACCENT_ORANGE, ACCENT_PURPLE, ACCENT_BLUE, ACCENT_GREEN, ACCENT_PINK]

# Custom Continuous Cyber Scales
CYBER_SCALE_CYAN = [[0.0, "#040711"], [0.4, "#005580"], [0.8, "#00c6ff"], [1.0, "#00f2fe"]]
CYBER_SCALE_ORANGE = [[0.0, "#040711"], [0.4, "#802b00"], [0.8, "#ff8000"], [1.0, "#ff6b35"]]
CYBER_SCALE_PURPLE = [[0.0, "#040711"], [0.4, "#4b0082"], [0.8, "#8a2be2"], [1.0, "#a855f7"]]

# Plotly Layout Custom Theme
theme_layout = go.Layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Rajdhani, Inter, sans-serif", size=13, color=TEXT_COLOR),
    title=dict(font=dict(size=17, color=ACCENT_CYAN, family="Rajdhani, Orbitron, sans-serif")),
    xaxis=dict(
        gridcolor=GRID_COLOR,
        zerolinecolor=GRID_COLOR,
        tickfont=dict(color=MUTED_TEXT, family="Rajdhani, sans-serif", size=12),
        title_font=dict(color=TEXT_COLOR, family="Rajdhani, sans-serif")
    ),
    yaxis=dict(
        gridcolor=GRID_COLOR,
        zerolinecolor=GRID_COLOR,
        tickfont=dict(color=MUTED_TEXT, family="Rajdhani, sans-serif", size=12),
        title_font=dict(color=TEXT_COLOR, family="Rajdhani, sans-serif")
    ),
    legend=dict(
        font=dict(color=TEXT_COLOR, family="Rajdhani, sans-serif"),
        bgcolor="rgba(6, 10, 23, 0.8)",
        bordercolor="rgba(0, 242, 254, 0.3)",
        borderwidth=1
    ),
    hoverlabel=dict(
        bgcolor="#060a17",
        bordercolor="#00f2fe",
        font_size=13,
        font_family="Rajdhani, sans-serif",
        font_color="#ffffff"
    ),
    margin=dict(l=40, r=40, t=50, b=40)
)

# Register custom template
custom_template = pio.templates.default = go.layout.Template(layout=theme_layout)
