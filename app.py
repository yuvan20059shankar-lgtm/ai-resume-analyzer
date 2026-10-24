"""
AI Resume Analyzer & Job Recommendation System
Built with Streamlit, Scikit-Learn, PyPDF, Python-Docx, and Plotly.
Featuring Dynamic Multi-Theme Engine with Unique Designer Palettes.
"""

import io
import json
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Import modular components
from resume_parser import parse_resume
from text_cleaner import clean_text, extract_metadata_contacts
from skill_extractor import SkillExtractor, resolve_data_path
from job_matcher import JobMatcher, resolve_job_data_path
from roadmap_generator import generate_learning_roadmap, roadmap_to_markdown

# Page configuration
st.set_page_config(
    page_title="TalentLens AI | Resume Analyzer & Job Matcher",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Curated Designer Color Palettes (Default: Executive Emerald & Modern Teal)
THEMES = {
    "🌿 Executive Emerald (Modern Teal & Obsidian #0e1117)": {
        "name": "Executive Emerald",
        "primary": "#10B981",
        "primary_rgb": "16, 185, 129",
        "accent": "#34D399",
        "accent_rgb": "52, 211, 153",
        "cyan_glow": "#2DD4BF",
        "bg_color": "#0E1117",
        "bg_gradient": "radial-gradient(circle at 10% 20%, #111A16 0%, #0E1117 90.2%)",
        "hero_gradient": "linear-gradient(135deg, rgba(16, 185, 129, 0.22) 0%, rgba(5, 150, 105, 0.16) 50%, rgba(45, 212, 191, 0.06) 100%)",
        "card_bg": "rgba(22, 27, 34, 0.7)",
        "card_border": "rgba(16, 185, 129, 0.16)",
        "card_hover_border": "rgba(52, 211, 153, 0.5)",
        "card_hover_shadow": "rgba(16, 185, 129, 0.25)",
        "tag_bg": "rgba(16, 185, 129, 0.2)",
        "tag_color": "#A7F3D0",
        "tag_border": "rgba(16, 185, 129, 0.45)",
        "radar_fill": "rgba(16, 185, 129, 0.22)",
        "radar_line": "#10B981",
        "bar_highlight": "#10B981",
    },
    "🌌 Cyber Obsidian (Electric Indigo & Violet Glow)": {
        "name": "Cyber Obsidian",
        "primary": "#6366F1",
        "primary_rgb": "99, 102, 241",
        "accent": "#A855F7",
        "accent_rgb": "168, 85, 247",
        "cyan_glow": "#06B6D4",
        "bg_color": "#0E1117",
        "bg_gradient": "radial-gradient(circle at 10% 20%, #151828 0%, #0E1117 90.2%)",
        "hero_gradient": "linear-gradient(135deg, rgba(99, 102, 241, 0.25) 0%, rgba(168, 85, 247, 0.18) 50%, rgba(6, 182, 212, 0.06) 100%)",
        "card_bg": "rgba(22, 27, 34, 0.7)",
        "card_border": "rgba(99, 102, 241, 0.16)",
        "card_hover_border": "rgba(99, 102, 241, 0.45)",
        "card_hover_shadow": "rgba(99, 102, 241, 0.22)",
        "tag_bg": "rgba(99, 102, 241, 0.22)",
        "tag_color": "#C7D2FE",
        "tag_border": "rgba(99, 102, 241, 0.45)",
        "radar_fill": "rgba(99, 102, 241, 0.22)",
        "radar_line": "#818CF8",
        "bar_highlight": "#818CF8",
    },
    "🌅 Sunset Mirage (Neon Coral & Warm Amber)": {
        "name": "Sunset Mirage",
        "primary": "#FF5E7E",
        "primary_rgb": "255, 94, 126",
        "accent": "#F59E0B",
        "accent_rgb": "245, 158, 11",
        "cyan_glow": "#A855F7",
        "bg_color": "#0E1117",
        "bg_gradient": "radial-gradient(circle at 10% 20%, #20131B 0%, #0E1117 90.2%)",
        "hero_gradient": "linear-gradient(135deg, rgba(255, 94, 126, 0.25) 0%, rgba(168, 85, 247, 0.18) 50%, rgba(245, 158, 11, 0.06) 100%)",
        "card_bg": "rgba(22, 27, 34, 0.7)",
        "card_border": "rgba(255, 94, 126, 0.16)",
        "card_hover_border": "rgba(255, 94, 126, 0.5)",
        "card_hover_shadow": "rgba(255, 94, 126, 0.25)",
        "tag_bg": "rgba(255, 94, 126, 0.22)",
        "tag_color": "#FECDD3",
        "tag_border": "rgba(255, 94, 126, 0.45)",
        "radar_fill": "rgba(255, 94, 126, 0.22)",
        "radar_line": "#FB7185",
        "bar_highlight": "#FF5E7E",
    },
    "❄️ Arctic Titanium (Glacier Cyan & Frost Navy)": {
        "name": "Arctic Titanium",
        "primary": "#38BDF8",
        "primary_rgb": "56, 189, 248",
        "accent": "#818CF8",
        "accent_rgb": "129, 140, 248",
        "cyan_glow": "#2DD4BF",
        "bg_color": "#0E1117",
        "bg_gradient": "radial-gradient(circle at 10% 20%, #101E2E 0%, #0E1117 90.2%)",
        "hero_gradient": "linear-gradient(135deg, rgba(56, 189, 248, 0.25) 0%, rgba(99, 102, 241, 0.18) 50%, rgba(45, 212, 191, 0.06) 100%)",
        "card_bg": "rgba(22, 27, 34, 0.7)",
        "card_border": "rgba(56, 189, 248, 0.16)",
        "card_hover_border": "rgba(56, 189, 248, 0.5)",
        "card_hover_shadow": "rgba(56, 189, 248, 0.25)",
        "tag_bg": "rgba(56, 189, 248, 0.22)",
        "tag_color": "#BAE6FD",
        "tag_border": "rgba(56, 189, 248, 0.45)",
        "radar_fill": "rgba(56, 189, 248, 0.22)",
        "radar_line": "#38BDF8",
        "bar_highlight": "#38BDF8",
    },
    "👑 Luxe Sovereign (Imperial Gold & Obsidian Royale)": {
        "name": "Luxe Sovereign",
        "primary": "#F59E0B",
        "primary_rgb": "245, 158, 11",
        "accent": "#D97706",
        "accent_rgb": "217, 119, 6",
        "cyan_glow": "#10B981",
        "bg_color": "#0E1117",
        "bg_gradient": "radial-gradient(circle at 10% 20%, #1F1910 0%, #0E1117 90.2%)",
        "hero_gradient": "linear-gradient(135deg, rgba(245, 158, 11, 0.25) 0%, rgba(217, 119, 6, 0.18) 50%, rgba(251, 191, 36, 0.06) 100%)",
        "card_bg": "rgba(22, 27, 34, 0.7)",
        "card_border": "rgba(245, 158, 11, 0.16)",
        "card_hover_border": "rgba(245, 158, 11, 0.5)",
        "card_hover_shadow": "rgba(245, 158, 11, 0.25)",
        "tag_bg": "rgba(245, 158, 11, 0.22)",
        "tag_color": "#FDE68A",
        "tag_border": "rgba(245, 158, 11, 0.45)",
        "radar_fill": "rgba(245, 158, 11, 0.22)",
        "radar_line": "#FBBF24",
        "bar_highlight": "#F59E0B",
    },
}


def generate_custom_css(t: dict) -> str:
    """Generates dynamic CSS tokens based on active theme."""
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    /* Clean Dark Mode Base (#0e1117) with Subtle Gradient */
    .stApp {{
        background: {t["bg_gradient"]};
        color: #F3F4F6;
    }}

    /* Sidebar Background */
    [data-testid="stSidebar"] {{
        background-color: #0E1117 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }}

    /* Glassmorphism Card Container */
    .glass-card {{
        background: {t["card_bg"]};
        border: 1px solid {t["card_border"]};
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.42);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    .glass-card:hover {{
        border-color: {t["card_hover_border"]};
        transform: translateY(-2px);
        box-shadow: 0 12px 40px 0 {t["card_hover_shadow"]};
    }}

    /* Metric card styling */
    .metric-box {{
        background: linear-gradient(135deg, rgba(22, 27, 34, 0.85) 0%, rgba(14, 17, 23, 0.95) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 18px 20px;
        text-align: left;
        position: relative;
        overflow: hidden;
    }}

    .metric-box::after {{
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 60px;
        height: 60px;
        background: radial-gradient(circle, rgba({t["primary_rgb"]}, 0.25) 0%, transparent 70%);
    }}

    .metric-title {{
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94A3B8;
        margin-bottom: 6px;
    }}

    .metric-value {{
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #FFFFFF 0%, #E2E8F0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    .metric-sub {{
        font-size: 0.78rem;
        color: #64748B;
        margin-top: 4px;
    }}

    /* Primary Buttons & Download Buttons - Executive Emerald Accent */
    div.stButton > button:first-child,
    div.stDownloadButton > button:first-child {{
        background: linear-gradient(135deg, {t["primary"]} 0%, rgba({t["primary_rgb"]}, 0.85) 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid {t["accent"]} !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 8px 18px !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 4px 14px 0 rgba({t["primary_rgb"]}, 0.3) !important;
    }}

    div.stButton > button:first-child:hover,
    div.stDownloadButton > button:first-child:hover {{
        background: linear-gradient(135deg, {t["accent"]} 0%, {t["primary"]} 100%) !important;
        border-color: {t["accent"]} !important;
        box-shadow: 0 6px 20px 0 rgba({t["primary_rgb"]}, 0.45) !important;
        transform: translateY(-1px) !important;
    }}

    /* Streamlit Tab Active Highlight */
    button[data-baseweb="tab"][aria-selected="true"] {{
        border-bottom-color: {t["primary"]} !important;
        color: {t["accent"]} !important;
    }}

    /* File uploader hover border */
    [data-testid="stFileUploader"] section {{
        border-color: rgba({t["primary_rgb"]}, 0.25) !important;
        background-color: rgba(22, 27, 34, 0.4) !important;
    }}
    [data-testid="stFileUploader"] section:hover {{
        border-color: {t["primary"]} !important;
    }}

    /* Badges for skills */
    .skill-badge {{
        display: inline-flex;
        align-items: center;
        padding: 5px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 3px 4px;
        letter-spacing: 0.02em;
        transition: all 0.2s ease;
    }}

    .skill-badge.programming {{
        background: rgba(16, 185, 129, 0.12);
        color: #A7F3D0;
        border: 1px solid rgba(16, 185, 129, 0.35);
    }}

    .skill-badge.databases {{
        background: rgba(45, 212, 191, 0.12);
        color: #99F6E4;
        border: 1px solid rgba(45, 212, 191, 0.35);
    }}

    .skill-badge.ml {{
        background: rgba(52, 211, 153, 0.15);
        color: #6EE7B7;
        border: 1px solid rgba(52, 211, 153, 0.38);
    }}

    .skill-badge.cloud {{
        background: rgba(14, 165, 233, 0.12);
        color: #BAE6FD;
        border: 1px solid rgba(14, 165, 233, 0.35);
    }}

    .skill-badge.tools {{
        background: rgba(20, 184, 166, 0.12);
        color: #5EEAD4;
        border: 1px solid rgba(20, 184, 166, 0.35);
    }}

    .skill-badge.matched {{
        background: rgba(16, 185, 129, 0.22);
        color: #6EE7B7;
        border: 1px solid rgba(16, 185, 129, 0.5);
    }}

    .skill-badge.missing {{
        background: rgba(239, 68, 68, 0.15);
        color: #FCA5A5;
        border: 1px solid rgba(239, 68, 68, 0.35);
    }}

    /* Timeline Week Card */
    .week-card {{
        background: rgba(22, 27, 34, 0.7);
        border-left: 4px solid {t["primary"]};
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 0 12px 12px 0;
        padding: 18px 20px;
        margin-bottom: 16px;
    }}

    .hero-banner {{
        background: {t["hero_gradient"]};
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 20px;
        padding: 32px 36px;
        margin-bottom: 28px;
        position: relative;
        overflow: hidden;
    }}

    /* Custom scrollbars */
    ::-webkit-scrollbar {{
        width: 6px;
        height: 6px;
    }}
    ::-webkit-scrollbar-track {{
        background: #0E1117;
    }}
    ::-webkit-scrollbar-thumb {{
        background: rgba({t["primary_rgb"]}, 0.45);
        border-radius: 3px;
    }}
    </style>
    """


# Sample Resumes for Instant 1-Click Demonstration
SAMPLE_RESUMES = {
    "Select a preloaded resume...": "",
    "Machine Learning Engineer (Alex Turner)": """Alex Turner
Email: alex.turner.ml@example.com | Phone: (555) 349-8201
GitHub: github.com/alexturner-ml | LinkedIn: linkedin.com/in/alexturner-ai
San Francisco, CA

PROFESSIONAL SUMMARY
Machine Learning Engineer with 4+ years of hands-on experience designing, training, and deploying deep learning pipelines and production ML services. Proven track record building computer vision and NLP solutions, optimizing PyTorch models for edge execution, and orchestrating containers with Docker.

TECHNICAL SKILLS
• Programming: Python, C++, SQL, Bash
• Machine Learning & DL: PyTorch, TensorFlow, Scikit-Learn, Pandas, NumPy, XGBoost, OpenCV, Computer Vision, Deep Learning
• Cloud & DevOps: Docker, Git, Linux, AWS (EC2, S3), MLflow
• Methodologies: CI/CD, A/B Testing, Model Quantization, Feature Engineering

PROFESSIONAL EXPERIENCE
Senior Machine Learning Engineer | NeuralScale Technologies (2022 – Present)
• Architected real-time object detection models using PyTorch and OpenCV, reducing latency by 42% on edge hardware with C++ inference bindings.
• Built automated feature engineering pipelines using Pandas, NumPy, and Scikit-Learn for 15M daily tabular events.
• Implemented model registry and experiment tracking across 80+ iterations using MLflow and Docker containers on AWS.

Machine Learning Developer | DataVibe Analytics (2020 – 2022)
• Developed predictive gradient-boosted decision trees using XGBoost and Scikit-Learn to detect customer churn.
• Maintained relational databases using PostgreSQL and wrote high-performance SQL queries for training data extraction.
• Collaborated via Git workflows and built interactive model monitoring dashboards using Streamlit.

EDUCATION
B.S. in Computer Science | University of California, Berkeley (2020)
""",
    "Data Analyst (Sarah Chen)": """Sarah Chen
Email: sarah.chen.analytics@example.com | Phone: (555) 782-9910
LinkedIn: linkedin.com/in/sarahchen-data | GitHub: github.com/sarahchendata
New York, NY

PROFESSIONAL SUMMARY
Results-driven Data Analyst with 3+ years of experience transforming complex business datasets into intuitive dashboards and strategic insights. Expert in SQL, Python data wrangling (Pandas, NumPy), Power BI, and Tableau.

TECHNICAL EXPERTISE
• Core Skills: SQL, Python, Power BI, Tableau, Pandas, NumPy, PostgreSQL, Excel
• Databases & Data Warehousing: PostgreSQL, MySQL, Snowflake, Relational Modeling
• Tools & Techniques: Git, Statistical Analysis, Exploratory Data Analysis (EDA), KPI Reporting, A/B Testing

EXPERIENCE
Lead Data Analyst | Horizon Retail Group (2022 – Present)
• Developed 12 enterprise Power BI and Tableau dashboards tracking $85M in quarterly GMV with automated SQL refresh schedules.
• Extracted and cleaned multi-table transactional records from PostgreSQL and Snowflake using Python and Pandas.
• Conducted cohort retention analyses and A/B test evaluations leading to a 14% lift in seasonal campaign conversion.

Business Intelligence Analyst | MetroFin Services (2021 – 2022)
• Authored 50+ optimized SQL queries for financial reconciliation, reducing report generation run-time from 4 hours to 15 minutes.
• Designed executive summary presentations and automated KPI tracking using Tableau and Excel.
• Documented data schemas, dictionary mappings, and version-controlled scripts with Git.

EDUCATION
B.S. in Statistics & Economics | New York University (2021)
""",
    "AI & NLP Engineer (Dr. Marcus Vance)": """Dr. Marcus Vance
Email: marcus.vance@example.org | Phone: (555) 412-6804
GitHub: github.com/marcusvance-ai | LinkedIn: linkedin.com/in/marcus-vance-phd
Seattle, WA

PROFESSIONAL SUMMARY
Senior AI Engineer specializing in Natural Language Processing (NLP), Large Language Models (LLMs), and Retrieval-Augmented Generation (RAG). Extensive experience fine-tuning Hugging Face Transformers, engineering LangChain agents, and serving low-latency PyTorch models.

TECHNICAL COMPETENCIES
• AI & NLP: LLMs, LangChain, Hugging Face, Transformers, PyTorch, NLP, Scikit-Learn, Deep Learning
• Languages & Databases: Python, SQL, PostgreSQL, Redis, Vector Databases (FAISS)
• Deployment & Infrastructure: Docker, Kubernetes, Git, Linux, FastAPI, Streamlit, Azure

EXPERIENCE
Staff AI Engineer | Synthetix AI Labs (2022 – Present)
• Designed an enterprise RAG assistant utilizing LangChain, Hugging Face transformers, and vector embeddings in PostgreSQL (pgvector).
• Fine-tuned open-source LLMs using PEFT/LoRA on PyTorch, decreasing domain hallucination rates by 38%.
• Containerized microservices using Docker and deployed on Kubernetes with automated CI/CD monitoring.
• Built interactive evaluation playgrounds using Streamlit for rapid red-teaming.

NLP Research Engineer | LexisData Systems (2019 – 2022)
• Developed named entity recognition (NER) and sentiment classification pipelines using Hugging Face and Scikit-Learn.
• Processed multi-gigabyte textual corpora in Python with Redis caching layers.

EDUCATION
Ph.D. in Computer Science (NLP Focus) | University of Washington (2019)
""",
}


@st.cache_resource
def load_extractors():
    """Initializes and caches the SkillExtractor and JobMatcher instances."""
    skill_extractor = SkillExtractor(resolve_data_path("skill_dictionary.csv"))
    job_matcher = JobMatcher(resolve_job_data_path("job_roles.csv"))
    return skill_extractor, job_matcher


def render_header(t: dict):
    """Renders the top branding hero banner customized to active theme."""
    st.markdown(
        f"""
        <div class="hero-banner">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
                <div>
                    <span style="background: {t['tag_bg']}; color: {t['tag_color']}; padding: 4px 12px; border-radius: 999px; font-size: 0.8rem; font-weight: 700; border: 1px solid {t['tag_border']};">
                        ⚡ NEXT-GEN TALENT INTELLIGENCE
                    </span>
                    <h1 style="font-size: 2.6rem; font-weight: 800; margin: 12px 0 6px 0; letter-spacing: -0.03em; color: #FFFFFF;">
                        AI Resume Analyzer & Job Recommender
                    </h1>
                    <p style="color: #94A3B8; font-size: 1.05rem; margin: 0; max-width: 720px; line-height: 1.5;">
                        Upload your PDF or DOCX resume to extract technical skills via controlled vocabulary, compute TF-IDF cosine role match rankings, identify skill gaps, and generate a personalized 4-week learning roadmap.
                    </p>
                </div>
                <div style="text-align: right;">
                    <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 12px 18px; text-align: center;">
                        <span style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; font-weight: 600;">Theme: {t['name']}</span>
                        <div style="color: {t['primary']}; font-weight: 700; font-size: 0.95rem; display: flex; align-items: center; justify-content: center; gap: 6px; margin-top: 2px;">
                            <span style="display: inline-block; width: 8px; height: 8px; background: {t['primary']}; border-radius: 50%; box-shadow: 0 0 10px {t['primary']};"></span>
                            TF-IDF & NLP Ready
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def create_gauge_chart(score: float, title: str, t: dict) -> go.Figure:
    """Generates a modern circular gauge chart with theme styling."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "%", "font": {"size": 38, "family": "Plus Jakarta Sans", "color": "#FFFFFF"}},
            title={"text": title, "font": {"size": 16, "family": "Plus Jakarta Sans", "color": "#94A3B8"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#475569"},
                "bar": {"color": t["primary"], "thickness": 0.28},
                "bgcolor": "rgba(30, 41, 59, 0.5)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 40], "color": "rgba(239, 68, 68, 0.25)"},
                    {"range": [40, 70], "color": "rgba(245, 158, 11, 0.25)"},
                    {"range": [70, 100], "color": f"rgba({t['primary_rgb']}, 0.3)"},
                ],
                "threshold": {
                    "line": {"color": t["accent"], "width": 4},
                    "thickness": 0.75,
                    "value": score,
                },
            },
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=25, r=25, t=40, b=20),
        height=220,
    )
    return fig


def create_rankings_bar_chart(df_rankings: pd.DataFrame, target_role: str, t: dict) -> go.Figure:
    """Creates an interactive horizontal bar chart ranking job matches."""
    df_sorted = df_rankings.sort_values(by="match_percentage", ascending=True)

    # Highlight target role with theme accent
    colors = [
        t["bar_highlight"] if role.lower() == target_role.lower() else "rgba(148, 163, 184, 0.35)"
        for role in df_sorted["role"]
    ]

    fig = go.Figure(
        go.Bar(
            x=df_sorted["match_percentage"],
            y=df_sorted["role"],
            orientation="h",
            marker=dict(
                color=colors,
                line=dict(color="rgba(255, 255, 255, 0.2)", width=1),
                cornerradius=6,
            ),
            text=[f"{val}%" for val in df_sorted["match_percentage"]],
            textposition="outside",
            textfont=dict(color="#CBD5E1", size=12, family="Plus Jakarta Sans"),
            hovertemplate="<b>%{y}</b><br>Overall Match: %{x}%<br>TF-IDF Score: %{customdata[0]}%<br>Skill Coverage: %{customdata[1]}%<extra></extra>",
            customdata=df_sorted[["tfidf_percentage", "skill_coverage_percentage"]].values,
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=40, t=20, b=20),
        height=320,
        xaxis=dict(
            range=[0, 110],
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.06)",
            title="Composite Match Percentage (%)",
            title_font=dict(color="#94A3B8", size=12),
            tickfont=dict(color="#94A3B8"),
        ),
        yaxis=dict(
            tickfont=dict(color="#FFFFFF", size=12, family="Plus Jakarta Sans"),
        ),
    )
    return fig


def create_radar_chart(category_counts: dict, t: dict) -> go.Figure:
    """Creates a radar chart showing candidate skill category distribution."""
    categories = ["programming", "databases", "ml", "cloud", "tools"]
    display_labels = ["Programming", "Databases", "Machine Learning", "Cloud & DevOps", "Tools & BI"]
    values = [category_counts.get(c, 0) for c in categories]

    # Close the radar loop
    radar_labels = display_labels + [display_labels[0]]
    radar_values = values + [values[0]]

    fig = go.Figure(
        data=go.Scatterpolar(
            r=radar_values,
            theta=radar_labels,
            fill="toself",
            fillcolor=t["radar_fill"],
            line=dict(color=t["radar_line"], width=2),
            marker=dict(size=7, color=t["accent"]),
        )
    )

    max_val = max(values) if values and max(values) > 0 else 5

    fig.update_layout(
        polar=dict(
            bgcolor="rgba(15, 23, 42, 0.5)",
            radialaxis=dict(
                visible=True,
                range=[0, max_val + 1],
                showline=False,
                tickfont=dict(color="#64748B", size=10),
                gridcolor="rgba(255, 255, 255, 0.08)",
            ),
            angularaxis=dict(
                tickfont=dict(color="#CBD5E1", size=11, family="Plus Jakarta Sans"),
                gridcolor="rgba(255, 255, 255, 0.08)",
            ),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=35, r=35, t=25, b=25),
        height=280,
    )
    return fig


def main():
    skill_extractor, job_matcher = load_extractors()
    all_job_roles = job_matcher.get_all_roles()

    # Sidebar Controls
    with st.sidebar:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
                <span style="font-size: 1.8rem;">⚡</span>
                <div>
                    <h3 style="margin: 0; font-size: 1.2rem; font-weight: 800; color: #FFFFFF;">TalentLens</h3>
                    <p style="margin: 0; font-size: 0.75rem; color: #94A3B8;">Intelligent Career Matcher</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### 🎨 Custom Visual Theme")
        theme_name = st.selectbox(
            "Select unique color palette:",
            options=list(THEMES.keys()),
            index=0,
            help="Instantly transforms the dashboard with rich custom gradients, card glows, and chart palettes.",
        )
        active_theme = THEMES[theme_name]

        st.markdown("---")
        st.markdown("#### 🎯 Target Role Selection")
        target_role = st.selectbox(
            "Select your dream target role:",
            options=all_job_roles,
            index=0 if "Machine Learning Engineer" not in all_job_roles else all_job_roles.index("Machine Learning Engineer"),
            help="Your resume will be evaluated specifically against this role's benchmarks.",
        )

        role_info = job_matcher.get_role_details(target_role)
        if role_info:
            with st.expander("ℹ️ Role Profile & Requirements", expanded=False):
                st.caption(f"**Field:** {role_info['category']}")
                st.caption(f"**Experience Level:** {role_info['experience_level']}")
                st.caption(f"**Summary:** {role_info['summary']}")
                st.write("**Core Required Skills:**")
                st.write(", ".join(role_info["required_skills"]))

        st.markdown("---")
        st.markdown("#### ⚡ Quick Demo (Sample Resumes)")
        sample_choice = st.selectbox(
            "Load pre-configured resume:",
            options=list(SAMPLE_RESUMES.keys()),
            index=0,
            help="Choose a pre-filled candidate profile to test without uploading a file.",
        )

        st.markdown("---")
        st.caption(f"Active Theme: **{active_theme['name']}**")
        st.caption("Developed with Streamlit & Scikit-Learn | v1.0.0")

    # Inject dynamic custom CSS for selected theme
    st.markdown(generate_custom_css(active_theme), unsafe_allow_html=True)

    render_header(active_theme)

    # Resume Input Section
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📄 Step 1: Upload or Select Candidate Resume")

    col_upload, col_preview = st.columns([1.2, 0.8])

    uploaded_file = None
    resume_raw_text = ""
    source_filename = ""

    with col_upload:
        uploaded_file = st.file_uploader(
            "Upload Resume Document (PDF or DOCX):",
            type=["pdf", "docx", "txt"],
            help="Upload your latest resume. PDF and DOCX formats are fully supported with formatting/table extraction.",
        )

    # Resolve text source: Uploaded file takes precedence, then sample selector
    if uploaded_file is not None:
        source_filename = uploaded_file.name
        with st.spinner("Extracting text and structure from file..."):
            parse_res = parse_resume(uploaded_file, filename=uploaded_file.name)
            if parse_res["success"]:
                resume_raw_text = parse_res["text"]
                st.success(
                    f"✅ Successfully parsed **{uploaded_file.name}** "
                    f"({parse_res['file_type']}, {parse_res['page_count']} page(s), {parse_res['word_count']} words)"
                )
            else:
                if parse_res.get("is_scanned"):
                    st.warning(
                        f"⚠️ **Scanned or Image-Based PDF Detected in `{uploaded_file.name}`**\n\n"
                        f"{parse_res.get('suggestion')}"
                    )
                else:
                    st.error(f"❌ **Notice:** {parse_res.get('error')}\n\n{parse_res.get('suggestion', '')}")

                # Provide seamless fallback input without crashing or breaking the app
                fallback_text = st.text_area(
                    "📋 Paste your resume text directly below to analyze:",
                    height=180,
                    placeholder="Paste resume text (e.g. Summary, Skills, Experience, Education)...",
                    help="Copy text from your source document or Word file and paste here to continue.",
                )
                if fallback_text.strip():
                    resume_raw_text = fallback_text.strip()
                    st.info(f"✨ Analyzing pasted resume text ({len(resume_raw_text.split())} words).")
                else:
                    st.markdown("</div>", unsafe_allow_html=True)
                    return
    elif sample_choice and sample_choice != "Select a preloaded resume...":
        source_filename = sample_choice
        resume_raw_text = SAMPLE_RESUMES[sample_choice]
        st.info(f"✨ Loaded pre-configured sample profile: **{sample_choice}**")
    else:
        # Default placeholder to guide the user
        st.warning("👈 Please upload a PDF/DOCX resume file above, or select a sample resume from the left sidebar to proceed.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # Extract contact info metadata
    contact_info = extract_metadata_contacts(resume_raw_text)

    with col_preview:
        with st.expander("🔍 Candidate Contact & Text Preview", expanded=False):
            if contact_info["emails"]:
                st.write(f"📧 **Email:** {', '.join(contact_info['emails'])}")
            if contact_info["phones"]:
                st.write(f"📞 **Phone:** {', '.join(contact_info['phones'])}")
            if contact_info["links"]:
                st.write(f"🔗 **Links:** {', '.join(contact_info['links'])}")
            st.text_area("Extracted Text Preview", resume_raw_text[:800] + ("..." if len(resume_raw_text) > 800 else ""), height=150)

    st.markdown('</div>', unsafe_allow_html=True)

    # Process and Clean Text
    cleaned_resume_text = clean_text(resume_raw_text)

    # Extract Skills
    extraction_result = skill_extractor.extract_skills(cleaned_resume_text)
    extracted_skills = extraction_result["matched_skills"]
    skills_by_cat = extraction_result["skills_by_category"]
    cat_counts = extraction_result["category_counts"]

    # Match against Job Roles using TF-IDF and Skill Overlap
    match_result = job_matcher.match_resume(
        resume_text=cleaned_resume_text,
        extracted_skills=extracted_skills,
        target_role=target_role,
    )

    target_match = match_result["target_role_match"]
    top_role = match_result["top_role"]
    df_rankings = match_result["df_rankings"]

    # KPI Top Metric Cards
    target_score = target_match["match_percentage"] if target_match else 0.0
    matched_count = len(target_match["matched_skills"]) if target_match else 0
    missing_count = len(target_match["missing_skills"]) if target_match else 0
    top_role_name = top_role["role"] if top_role else "N/A"
    top_role_score = top_role["match_percentage"] if top_role else 0

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-title">Target Role Match</div>
                <div class="metric-value">{target_score}%</div>
                <div class="metric-sub">{target_role}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-title">Extracted Skills</div>
                <div class="metric-value">{extraction_result['total_found']}</div>
                <div class="metric-sub">Across 5 domains</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-title">Target Skills Matched</div>
                <div class="metric-value">{matched_count} <span style="font-size: 1rem; color:#64748B;">/ {matched_count + missing_count}</span></div>
                <div class="metric-sub">{missing_count} skill gaps identified</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-title">Top Recommended Role</div>
                <div class="metric-value" style="font-size: 1.45rem; line-height: 2.2rem;">{top_role_name}</div>
                <div class="metric-sub">{top_role_score}% match score</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # Visual Analytics & Match Dashboards
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Step 2: Role Fit & Match Score Analytics")

    col_gauge, col_bar, col_radar = st.columns([1, 1.6, 1.1])

    with col_gauge:
        st.markdown(f"**Target Role Gauge ({target_role})**")
        fig_gauge = create_gauge_chart(target_score, title=target_role, t=active_theme)
        st.plotly_chart(fig_gauge, use_container_width=True)
        if target_match:
            st.caption(
                f"TF-IDF Semantic Score: **{target_match['tfidf_percentage']}%** | "
                f"Required Skill Coverage: **{target_match['skill_coverage_percentage']}%**"
            )

    with col_bar:
        st.markdown("**All Job Roles Ranked by Match Score**")
        fig_bar = create_rankings_bar_chart(df_rankings, target_role, t=active_theme)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_radar:
        st.markdown("**Skill Category Distribution**")
        fig_radar = create_radar_chart(cat_counts, t=active_theme)
        st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Extracted Technical Skills Display Grouped by Category
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🛠️ Step 3: Extracted Technical Skills (Controlled Vocabulary)")
    st.caption("Identified using strict boundary matching and alias normalization from your resume text.")

    tabs = st.tabs([
        f"All Skills ({extraction_result['total_found']})",
        f"Programming ({len(skills_by_cat.get('programming', []))})",
        f"Databases ({len(skills_by_cat.get('databases', []))})",
        f"Machine Learning ({len(skills_by_cat.get('ml', []))})",
        f"Cloud & DevOps ({len(skills_by_cat.get('cloud', []))})",
        f"Tools & BI ({len(skills_by_cat.get('tools', []))})",
    ])

    with tabs[0]:
        if extracted_skills:
            badges_html = " ".join([
                f'<span class="skill-badge {item["category"]}">{item["skill"]} <small style="opacity:0.7;">({item["count"]})</small></span>'
                for item in extraction_result["skill_details"]
            ])
            st.markdown(badges_html, unsafe_allow_html=True)
        else:
            st.info("No matching skills found in the controlled vocabulary. Consider adding technical terms.")

    category_mapping = {
        1: ("programming", "programming"),
        2: ("databases", "databases"),
        3: ("ml", "ml"),
        4: ("cloud", "cloud"),
        5: ("tools", "tools"),
    }

    for tab_idx, (cat_key, badge_class) in category_mapping.items():
        with tabs[tab_idx]:
            cat_skills = skills_by_cat.get(cat_key, [])
            if cat_skills:
                badges = " ".join([
                    f'<span class="skill-badge {badge_class}">{s} <small style="opacity:0.7;">({extraction_result["skill_counts"].get(s, 1)})</small></span>'
                    for s in cat_skills
                ])
                st.markdown(badges, unsafe_allow_html=True)
            else:
                st.write(f"*No skills detected under {cat_key}.*")

    st.markdown('</div>', unsafe_allow_html=True)

    # Skill-Gap Analysis for Target Role
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f"### 🎯 Step 4: Skill-Gap Analysis for **{target_role}**")

    if target_match:
        matched_req = target_match["matched_skills"]
        missing_req = target_match["missing_skills"]
        opt_matched = target_match.get("matched_optional_skills", [])

        gap_col1, gap_col2 = st.columns(2)

        with gap_col1:
            st.markdown(
                f"""
                <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 18px;">
                    <h4 style="color: #6EE7B7; margin-top: 0; display: flex; align-items: center; gap: 8px;">
                        <span>✅</span> Matched Required Skills ({len(matched_req)})
                    </h4>
                    <p style="font-size: 0.85rem; color: #94A3B8;">Skills detected on your resume that directly satisfy role requirements:</p>
                """,
                unsafe_allow_html=True,
            )
            if matched_req:
                m_badges = " ".join([f'<span class="skill-badge matched">✓ {s}</span>' for s in matched_req])
                st.markdown(m_badges, unsafe_allow_html=True)
            else:
                st.write("*None of the required skills were detected.*")
            st.markdown("</div>", unsafe_allow_html=True)

        with gap_col2:
            st.markdown(
                f"""
                <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 12px; padding: 18px;">
                    <h4 style="color: #FCA5A5; margin-top: 0; display: flex; align-items: center; gap: 8px;">
                        <span>⚠️</span> Missing Skill Gaps ({len(missing_req)})
                    </h4>
                    <p style="font-size: 0.85rem; color: #94A3B8;">High-priority skills required for this role not found on your resume:</p>
                """,
                unsafe_allow_html=True,
            )
            if missing_req:
                miss_badges = " ".join([f'<span class="skill-badge missing">✗ {s}</span>' for s in missing_req])
                st.markdown(miss_badges, unsafe_allow_html=True)
            else:
                st.markdown('<p style="color: #86EFAC; font-weight:600;">🎉 Amazing! You have satisfied all core required skills for this position!</p>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        if opt_matched:
            st.markdown(
                f"<div style='margin-top: 12px; font-size: 0.85rem; color: #CBD5E1;'>"
                f"⭐ <b>Bonus Desirable Skills Matched:</b> " +
                ", ".join([f"<code>{s}</code>" for s in opt_matched]) +
                "</div>",
                unsafe_allow_html=True,
            )

    st.markdown('</div>', unsafe_allow_html=True)

    # 4-Week Dynamic Learning Roadmap
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f"### 🗺️ Step 5: Customized 4-Week Learning Roadmap")

    roadmap_data = generate_learning_roadmap(
        target_role=target_role,
        extracted_skills=extracted_skills,
        required_skills=target_match["required_skills"] if target_match else [],
        optional_skills=target_match.get("optional_skills", []) if target_match else [],
    )

    st.info(f"💡 {roadmap_data['summary']}")

    for week in roadmap_data["weeks"]:
        with st.expander(
            f"📅 Week {week['week_number']}: {week['theme']} ({len(week['target_skills'])} Target Skill{'s' if len(week['target_skills']) > 1 else ''})",
            expanded=True if week["week_number"] == 1 else False,
        ):
            st.markdown(f"**Target Skills to Master:** {', '.join([f'`{s}`' for s in week['target_skills']])}")
            
            c_left, c_right = st.columns([1.2, 1])
            with c_left:
                st.markdown("##### 🎯 Focus Areas & Topics")
                for item in week["focus_areas"]:
                    st.markdown(f"- {item}")
                
                st.markdown("##### ⚡ Practical Action Items")
                for action in week["action_items"]:
                    st.markdown(f"- [ ] {action}")

            with c_right:
                st.markdown("##### 📚 Recommended Resources")
                for res in week["recommended_resources"]:
                    st.markdown(f"- {res}")
                
                st.markdown(
                    f"""
                    <div style="background: rgba({active_theme['primary_rgb']}, 0.1); border-left: 3px solid {active_theme['primary']}; padding: 10px 14px; border-radius: 4px; margin-top: 12px;">
                        <span style="font-size: 0.8rem; font-weight: 700; color: {active_theme['tag_color']}; text-transform: uppercase;">Weekly Milestone</span>
                        <div style="font-size: 0.9rem; color: #FFFFFF; margin-top: 4px;">{week['milestone']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # Roadmap Export Button
    markdown_roadmap = roadmap_to_markdown(roadmap_data)
    st.download_button(
        label="📥 Download 4-Week Roadmap as Markdown (.md)",
        data=markdown_roadmap,
        file_name=f"roadmap_{target_role.lower().replace(' ', '_')}.md",
        mime="text/markdown",
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # Step 6: Full Candidate Evaluation Report
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📋 Step 6: Export Full Candidate Evaluation Report")

    full_report = {
        "candidate_source": source_filename,
        "contact_info": contact_info,
        "target_role": target_role,
        "match_percentage": target_score,
        "extracted_skills": extracted_skills,
        "skills_by_category": skills_by_cat,
        "top_recommended_role": top_role["role"] if top_role else "N/A",
        "top_match_score": top_role["match_percentage"] if top_role else 0,
        "all_role_rankings": [
            {
                "role": r["role"],
                "match_percentage": r["match_percentage"],
                "tfidf_percentage": r["tfidf_percentage"],
                "skill_coverage_percentage": r["skill_coverage_percentage"],
                "missing_skills": r["missing_skills"],
            }
            for r in match_result["rankings"]
        ],
    }

    report_col1, report_col2 = st.columns(2)
    with report_col1:
        st.download_button(
            label="💾 Download Evaluation Summary (JSON)",
            data=json.dumps(full_report, indent=2),
            file_name="candidate_evaluation_report.json",
            mime="application/json",
        )
    with report_col2:
        st.download_button(
            label="📄 Download Full Career Plan (Markdown)",
            data=markdown_roadmap,
            file_name="candidate_career_plan.md",
            mime="text/markdown",
        )

    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
