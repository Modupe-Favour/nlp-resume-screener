import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from nlp_utils import (calculate_match_score, find_skill_gaps,
                        extract_top_keywords, get_score_label,
                        get_improvement_tips)

# ── App Setup ────────────────────────────────────────────────
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.FLATLY],
                suppress_callback_exceptions=True)
app.title = "NLP Resume Screener"
server = app.server

# ── Colour Palette ───────────────────────────────────────────
NAVY = "#1B3A5C"
ACCENT = "#2E75B6"

# ── Layout ───────────────────────────────────────────────────
app.layout = dbc.Container([

    # Header
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("🤖 NLP Resume Screener",
                        style={"color": "white", "marginBottom": "5px"}),
                html.P("Paste your CV and a job description to get an "
                       "instant match score and skill gap analysis.",
                       style={"color": "#C9DCEF", "fontSize": "16px"})
            ], style={"background": NAVY, "padding": "30px",
                      "borderRadius": "10px", "marginBottom": "25px"})
        ])
    ]),

    # Input Section
    dbc.Row([
        # CV Input
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    html.H5("📄 Your CV / Resume",
                            style={"color": NAVY})),
                dbc.CardBody([
                    dcc.Textarea(
                        id="cv-input",
                        placeholder="Paste your CV text here...",
                        style={"width": "100%", "height": "300px",
                               "fontSize": "13px", "padding": "10px",
                               "border": f"1px solid {ACCENT}",
                               "borderRadius": "5px"}
                    )
                ])
            ], style={"marginBottom": "20px"})
        ], width=6),

        # Job Description Input
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    html.H5("💼 Job Description",
                            style={"color": NAVY})),
                dbc.CardBody([
                    dcc.Textarea(
                        id="job-input",
                        placeholder="Paste the job description here...",
                        style={"width": "100%", "height": "300px",
                               "fontSize": "13px", "padding": "10px",
                               "border": f"1px solid {ACCENT}",
                               "borderRadius": "5px"}
                    )
                ])
            ], style={"marginBottom": "20px"})
        ], width=6)
    ]),

    # Analyse Button
    dbc.Row([
        dbc.Col([
            dbc.Button("🔍 Analyse My CV",
                       id="analyse-btn",
                       color="primary",
                       size="lg",
                       style={"width": "100%",
                              "background": NAVY,
                              "border": "none",
                              "fontSize": "18px",
                              "padding": "15px"})
        ])
    ], style={"marginBottom": "30px"}),

    # Load Sample Button
    dbc.Row([
        dbc.Col([
            dbc.Button("📂 Load Sample Data",
                       id="sample-btn",
                       color="secondary",
                       outline=True,
                       size="sm",
                       style={"width": "100%"})
        ])
    ], style={"marginBottom": "30px"}),

    # Results Section
    html.Div(id="results-section"),

], fluid=True, style={"padding": "30px",
                       "backgroundColor": "#F8FAFC"})


# ── Callback: Load Sample Data ────────────────────────────────
@app.callback(
    Output("cv-input", "value"),
    Output("job-input", "value"),
    Input("sample-btn", "n_clicks"),
    prevent_initial_call=True
)
def load_sample(n):
    try:
        with open("Data/sample_cv.txt", "r") as f:
            cv = f.read()
        with open("Data/sample_job.txt", "r") as f:
            job = f.read()
        return cv, job
    except Exception:
        return "Error loading sample files.", ""


# ── Callback: Analyse CV ──────────────────────────────────────
@app.callback(
    Output("results-section", "children"),
    Input("analyse-btn", "n_clicks"),
    State("cv-input", "value"),
    State("job-input", "value"),
    prevent_initial_call=True
)
def analyse_cv(n_clicks, cv_text, job_text):
    if not cv_text or not job_text:
        return dbc.Alert("⚠️ Please paste both your CV and "
                         "a job description before analysing.",
                         color="warning")

    # --- Calculate Results ---
    score = calculate_match_score(cv_text, job_text)
    present, missing = find_skill_gaps(cv_text, job_text)
    label, color = get_score_label(score)
    tips = get_improvement_tips(missing, score)
    cv_keywords = extract_top_keywords(cv_text)
    job_keywords = extract_top_keywords(job_text)

    # --- Score Gauge Chart ---
    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": f"Match Score — {label}",
               "font": {"size": 18, "color": NAVY}},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": color},
            "steps": [
                {"range": [0, 45], "color": "#FFE5E5"},
                {"range": [45, 70], "color": "#FFF3CD"},
                {"range": [70, 100], "color": "#D4EDDA"}
            ],
            "threshold": {
                "line": {"color": NAVY, "width": 4},
                "thickness": 0.75,
                "value": score
            }
        }
    ))
    gauge.update_layout(height=300, margin=dict(t=50, b=10))

    # --- Skill Match Pie Chart ---
    pie = px.pie(
        names=["Matched Skills", "Missing Skills"],
        values=[len(present), len(missing)],
        color_discrete_sequence=["#00CC96", "#EF553B"],
        title="Skill Coverage"
    )
    pie.update_layout(height=300, margin=dict(t=50, b=10))

    # --- Skill Gap Bar Chart ---
    all_skills = ([(s, "✅ Present", "#00CC96") for s in present] +
                  [(s, "❌ Missing", "#EF553B") for s in missing])

    if all_skills:
        skills_df = pd.DataFrame(all_skills,
                                  columns=["Skill", "Status", "Color"])
        bar = px.bar(skills_df, x="Skill", color="Status",
                     color_discrete_map={"✅ Present": "#00CC96",
                                          "❌ Missing": "#EF553B"},
                     title="Skills Required by Job — Present vs Missing",
                     height=400)
        bar.update_layout(xaxis_tickangle=-45,
                           margin=dict(b=120))
    else:
        bar = go.Figure()
        bar.add_annotation(text="No tech skills detected in job description",
                           showarrow=False, font=dict(size=14))

    # --- Keywords Comparison Bar Chart ---
    cv_kw_df = cv_keywords.reset_index()
    cv_kw_df.columns = ["Keyword", "Count"]
    cv_kw_df = cv_kw_df.head(10)

    job_kw_df = job_keywords.reset_index()
    job_kw_df.columns = ["Keyword", "Count"]
    job_kw_df = job_kw_df.head(10)

    kw_fig = go.Figure()
    kw_fig.add_trace(go.Bar(name="CV Keywords",
                             x=cv_kw_df["Keyword"],
                             y=cv_kw_df["Count"],
                             marker_color=ACCENT))
    kw_fig.add_trace(go.Bar(name="Job Keywords",
                             x=job_kw_df["Keyword"],
                             y=job_kw_df["Count"],
                             marker_color="#EF553B"))
    kw_fig.update_layout(title="Top Keywords — CV vs Job Description",
                          barmode="group", height=350,
                          margin=dict(t=50, b=80))

    # --- Build Results Layout ---
    results = html.Div([

        # Score Row
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([dcc.Graph(figure=gauge)])
                ])
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([dcc.Graph(figure=pie)])
                ])
            ], width=6)
        ], style={"marginBottom": "20px"}),

        # Stats Row
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H3(f"{score}%",
                                style={"color": color,
                                       "fontSize": "48px",
                                       "fontWeight": "bold",
                                       "textAlign": "center"}),
                        html.P("Match Score",
                               style={"textAlign": "center",
                                      "color": NAVY,
                                      "fontWeight": "bold"})
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H3(f"{len(present)}",
                                style={"color": "#00CC96",
                                       "fontSize": "48px",
                                       "fontWeight": "bold",
                                       "textAlign": "center"}),
                        html.P("Skills Matched",
                               style={"textAlign": "center",
                                      "color": NAVY,
                                      "fontWeight": "bold"})
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H3(f"{len(missing)}",
                                style={"color": "#EF553B",
                                       "fontSize": "48px",
                                       "fontWeight": "bold",
                                       "textAlign": "center"}),
                        html.P("Skills Missing",
                               style={"textAlign": "center",
                                      "color": NAVY,
                                      "fontWeight": "bold"})
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H3(label.split()[0],
                                style={"color": color,
                                       "fontSize": "24px",
                                       "fontWeight": "bold",
                                       "textAlign": "center"}),
                        html.P("Overall Rating",
                               style={"textAlign": "center",
                                      "color": NAVY,
                                      "fontWeight": "bold"})
                    ])
                ])
            ], width=3),
        ], style={"marginBottom": "20px"}),

        # Skill Gap Chart
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([dcc.Graph(figure=bar)])
                ])
            ])
        ], style={"marginBottom": "20px"}),

        # Keywords Chart
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([dcc.Graph(figure=kw_fig)])
                ])
            ])
        ], style={"marginBottom": "20px"}),

        # Missing Skills List
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H5("❌ Missing Skills — Add These to Your CV",
                                style={"color": "#EF553B"})),
                    dbc.CardBody([
                        html.Div([
                            dbc.Badge(skill, color="danger",
                                      className="me-2 mb-2",
                                      style={"fontSize": "13px",
                                             "padding": "8px"})
                            for skill in missing
                        ]) if missing else
                        html.P("No missing skills detected! 🎉",
                               style={"color": "#00CC96"})
                    ])
                ])
            ], width=6),

            # Present Skills List
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H5("✅ Skills Found in Your CV",
                                style={"color": "#00CC96"})),
                    dbc.CardBody([
                        html.Div([
                            dbc.Badge(skill, color="success",
                                      className="me-2 mb-2",
                                      style={"fontSize": "13px",
                                             "padding": "8px"})
                            for skill in present
                        ]) if present else
                        html.P("No matching skills detected.",
                               style={"color": "#EF553B"})
                    ])
                ])
            ], width=6),
        ], style={"marginBottom": "20px"}),

        # Improvement Tips
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H5("💡 Personalised Improvement Tips",
                                style={"color": NAVY})),
                    dbc.CardBody([
                        html.Ul([
                            html.Li(tip,
                                    style={"marginBottom": "10px",
                                           "fontSize": "15px"})
                            for tip in tips
                        ])
                    ])
                ])
            ])
        ], style={"marginBottom": "30px"}),
    ])

    return results


# ── Run App ──────────────────────────────────────────────────
if __name__ == "__main__":
    app.run_server(debug=True)
