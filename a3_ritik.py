# a3_ritik.py
# FINAL — Stable coordinated multi-view dashboard (Gapminder, offline)
# Fixes:
# - No "expanding / going down" loop: graphs have fixed heights + debug=False
# - Dropdown menu overlays properly (z-index + overflow visible)
# - Light non-white background
# - Lasso selection stays stable (no 2ms snap-back) using dcc.Store + selectedpoints
# - Clear selection button

import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State
import dash
import pandas as pd

# =========================================================
# Dataset (offline, no SSL)
# =========================================================
df = pd.read_csv("gapminder.csv")
df["gdp_per_cap"] = df["gdpPercap"]
df["life_exp"] = df["lifeExp"]
df["pop_m"] = df["pop"] / 1e6

years = sorted(df["year"].unique())
continents = sorted(df["continent"].unique())

# =========================================================
# App
# =========================================================
app = Dash(__name__)
app.title = "Global Development Explorer"

# CSS injection (Dash-version safe)
GLOBAL_CSS = """
/* Dropdown menu above everything */
.Select, .Select-control, .Select-menu-outer { z-index: 9999 !important; }
"""

# Fixed heights (prevents Plotly autosize loop)
H_SCATTER = 420
H_MAP = 420
H_PC = 300
H_DIST = 300

def card(title, content, subtitle=None):
    return html.Div(
        style={
            "background": "rgba(248, 250, 252, 0.88)",
            "border": "1px solid #e5e7eb",
            "borderRadius": "18px",
            "padding": "14px",
            "boxShadow": "0 12px 30px rgba(15, 23, 42, 0.10)",
            "overflow": "visible",  # allow dropdown menu
        },
        children=[
            html.Div(title, style={"fontWeight": "800", "fontSize": "12px", "color": "#0f172a"}),
            html.Div(subtitle, style={"fontSize": "11px", "color": "#64748b", "marginTop": "2px"}) if subtitle else None,
            html.Div(style={"height": "8px"}),
            content,
        ],
    )

app.layout = html.Div(
    style={
        "minHeight": "100vh",
        "background": (
            "radial-gradient(1200px 600px at 20% 10%, #dbeafe 0%, rgba(219,234,254,0) 60%),"
            "radial-gradient(1200px 600px at 85% 25%, #e9d5ff 0%, rgba(233,213,255,0) 55%),"
            "linear-gradient(180deg, #f1f5f9 0%, #e7edf5 100%)"
        ),
        "color": "#0f172a",
        "fontFamily": "ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial",
        "padding": "16px",
        "boxSizing": "border-box",
    },
    children=[
        # CSS injection
        html.Div(
            dcc.Markdown(f"<style>{GLOBAL_CSS}</style>", dangerously_allow_html=True),
            style={"display": "none"},
        ),

        # Store selection so it doesn't snap back
        dcc.Store(id="sel_countries", data=[]),

        # Header + Controls
        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "1.2fr 1fr 1fr 1fr",
                "gap": "12px",
                "alignItems": "center",
            },
            children=[
                html.Div(
                    children=[
                        html.Div("Global Development Explorer", style={"fontSize": "22px", "fontWeight": "900"}),
                        html.Div(
                            "Lasso-select countries in the scatter → updates map, parallel coordinates, distribution, and KPIs.",
                            style={"fontSize": "12px", "color": "#475569", "marginTop": "3px"},
                        ),
                        html.Button(
                            "Clear selection",
                            id="clear_sel",
                            n_clicks=0,
                            style={
                                "marginTop": "8px",
                                "padding": "8px 10px",
                                "borderRadius": "12px",
                                "border": "1px solid #e5e7eb",
                                "background": "rgba(255,255,255,0.75)",
                                "cursor": "pointer",
                                "fontWeight": "700",
                                "fontSize": "12px",
                                "color": "#0f172a",
                            },
                        ),
                    ]
                ),

                card(
                    "Year",
                    dcc.Slider(
                        id="year",
                        min=int(min(years)),
                        max=int(max(years)),
                        step=None,
                        value=int(max(years)),
                        marks={int(y): str(y) for y in years[::2]},
                        tooltip={"always_visible": False},
                    ),
                    subtitle="Choose a snapshot year",
                ),

                card(
                    "Continent",
                    dcc.Dropdown(
                        id="continent",
                        options=[{"label": c, "value": c} for c in continents],
                        value=[],  # empty = All (handled in callback)
                        multi=True,
                        placeholder="All (no filter)",
                        style={"zIndex": 9999},
                    ),
                    subtitle="Filter visible countries",
                ),

                card(
                    "Complexity Control",
                    dcc.Slider(
                        id="topn",
                        min=30,
                        max=160,
                        step=10,
                        value=110,
                        marks=None,
                        tooltip={"always_visible": False},
                    ),
                    subtitle="Top-N by population (reduces clutter)",
                ),
            ],
        ),

        # KPIs
        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(4, 1fr)",
                "gap": "12px",
                "marginTop": "12px",
            },
            children=[
                card("Selection size", html.Div(id="kpi_n", style={"fontSize": "15px", "fontWeight": "800"})),
                card("Mean life expectancy", html.Div(id="kpi_life", style={"fontSize": "15px", "fontWeight": "800"})),
                card("Median GDP/cap", html.Div(id="kpi_gdp", style={"fontSize": "15px", "fontWeight": "800"})),
                card("Population covered", html.Div(id="kpi_pop", style={"fontSize": "15px", "fontWeight": "800"})),
            ],
        ),

        # Main Grid (fixed chart heights => stable)
        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "1.35fr 1fr",
                "gridTemplateRows": "auto auto",
                "gap": "12px",
                "marginTop": "12px",
            },
            children=[
                card(
                    "Scatter (primary interaction)",
                    dcc.Graph(
                        id="scatter",
                        style={"height": f"{H_SCATTER}px"},
                        config={"displayModeBar": False},
                    ),
                    subtitle="GDP per capita (log) vs Life expectancy — lasso to select",
                ),
                card(
                    "Map (selection-aware)",
                    dcc.Graph(
                        id="map",
                        style={"height": f"{H_MAP}px"},
                        config={"displayModeBar": False},
                    ),
                    subtitle="Selection reflected geographically",
                ),
                card(
                    "Parallel coordinates (multivariate)",
                    dcc.Graph(
                        id="parcoords",
                        style={"height": f"{H_PC}px"},
                        config={"displayModeBar": False},
                    ),
                    subtitle="Compare variables simultaneously",
                ),
                card(
                    "Distribution (selection-aware)",
                    dcc.Graph(
                        id="dist",
                        style={"height": f"{H_DIST}px"},
                        config={"displayModeBar": False},
                    ),
                    subtitle="GDP/cap histogram for the current selection",
                ),
            ],
        ),
    ],
)

# =========================================================
# Callback 1: Store lasso selection (prevents snap-back)
# =========================================================
@app.callback(
    Output("sel_countries", "data"),
    Input("scatter", "selectedData"),
    Input("clear_sel", "n_clicks"),
    Input("year", "value"),
    Input("continent", "value"),
    Input("topn", "value"),
    State("sel_countries", "data"),
)
def store_selection(selectedData, n_clear, year, conts, topn, stored):
    # Dash-version safe trigger id
    trig = dash.callback_context.triggered[0]["prop_id"].split(".")[0] if dash.callback_context.triggered else None

    # Clear button clears selection
    if trig == "clear_sel":
        return []

    # Changing filters clears selection (simpler + avoids stale selection)
    if trig in ("year", "continent", "topn"):
        return []

    # Only update store when there IS a selection.
    # IMPORTANT: if Plotly temporarily sends selectedData=None during rerender,
    # we keep the previous store (so it won't snap back).
    if selectedData and selectedData.get("points"):
        countries = []
        for p in selectedData["points"]:
            cd = p.get("customdata")
            if cd and len(cd) > 0:
                countries.append(cd[0])
            else:
                ht = p.get("hovertext")
                if ht:
                    countries.append(ht)

        # unique preserve order
        seen = set()
        uniq = []
        for c in countries:
            if c not in seen:
                seen.add(c)
                uniq.append(c)
        return uniq

    return stored  # keep previous selection if selectedData is empty/None

# =========================================================
# Callback 2: Render charts using stored selection
# =========================================================
@app.callback(
    Output("scatter", "figure"),
    Output("map", "figure"),
    Output("parcoords", "figure"),
    Output("dist", "figure"),
    Output("kpi_n", "children"),
    Output("kpi_life", "children"),
    Output("kpi_gdp", "children"),
    Output("kpi_pop", "children"),
    Input("year", "value"),
    Input("continent", "value"),
    Input("topn", "value"),
    Input("sel_countries", "data"),
)
def render(year, conts, topn, sel_countries):
    if year is None:
        year = int(max(years))
    if not topn:
        topn = 110
    if not conts:
        conts = continents

    d = df[(df["year"] == int(year)) & (df["continent"].isin(conts))].copy()
    d = d.sort_values("pop", ascending=False).head(int(topn)).reset_index(drop=True)

    if sel_countries:
        d_sel = d[d["country"].isin(sel_countries)].copy()
    else:
        d_sel = d

    # Indices for selectedpoints (so highlight persists)
    selectedpoints = d.index[d["country"].isin(sel_countries)].tolist() if sel_countries else None

    # Scatter
    fig_scatter = px.scatter(
        d,
        x="gdp_per_cap",
        y="life_exp",
        size="pop_m",
        color="continent",
        hover_name="country",
        custom_data=["country"],  # so selectedData includes country reliably
        hover_data={"pop_m": ":.1f", "gdp_per_cap": ":,.0f", "life_exp": ":.1f"},
        log_x=True,
        template="plotly_white",
    )
    fig_scatter.update_layout(
        height=H_SCATTER,
        margin=dict(l=10, r=10, t=10, b=10),
        dragmode="lasso",
        xaxis_title="GDP per capita (log scale)",
        yaxis_title="Life expectancy",
        legend_title_text="Continent",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        # helps keep UI stable across updates
        uirevision=f"{year}-{topn}-{'|'.join(sorted(conts))}",
    )
    fig_scatter.update_traces(
        selectedpoints=selectedpoints,
        selected=dict(marker=dict(opacity=1.0)),
        unselected=dict(marker=dict(opacity=0.20)),
    )

    # Map
    fig_map = px.scatter_geo(
        d_sel,
        locations="iso_alpha",
        hover_name="country",
        size="pop_m",
        color="continent",
        projection="natural earth",
        template="plotly_white",
    )
    fig_map.update_layout(
        height=H_MAP,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        geo=dict(bgcolor="rgba(0,0,0,0)"),
    )

    # Parallel coords
    pc_cols = ["gdp_per_cap", "life_exp", "pop_m"]
    fig_pc = px.parallel_coordinates(
        d_sel[pc_cols].dropna(),
        color="life_exp",
        template="plotly_white",
        labels={"gdp_per_cap": "GDP/cap", "life_exp": "LifeExp", "pop_m": "Pop(M)"},
    )
    fig_pc.update_layout(
        height=H_PC,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    # Distribution
    fig_dist = px.histogram(d_sel, x="gdp_per_cap", nbins=24, template="plotly_white")
    fig_dist.update_layout(
        height=H_DIST,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="GDP per capita",
        yaxis_title="Count",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    # KPIs
    n = len(d_sel)
    mean_life = float(d_sel["life_exp"].mean()) if n else 0.0
    med_gdp = float(d_sel["gdp_per_cap"].median()) if n else 0.0
    pop_cov = float(d_sel["pop"].sum()) / 1e6 if n else 0.0

    return (
        fig_scatter,
        fig_map,
        fig_pc,
        fig_dist,
        f"{n} countries",
        f"{mean_life:.2f} years",
        f"${med_gdp:,.0f}",
        f"{pop_cov:.0f}M people",
    )

if __name__ == "__main__":
    # IMPORTANT: debug=False avoids dev-tools resize/hotreload side effects
    app.run(debug=False, port=8060)
