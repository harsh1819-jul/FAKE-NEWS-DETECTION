import streamlit as st
from utils.ui_components import load_css, render_logo, render_footer
from services.logger import logger

# Initialize page style
load_css()
logger.info("Rendering Home page.")

# Hero Section
st.markdown("<!-- Hero Section -->", unsafe_allow_html=True)
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown(
        """
        <h1 class="hero-title">TruthLens</h1>
        <p style="font-size: 24px; font-weight: 700; color: #3B82F6; margin-top: -15px; font-family: 'Outfit', sans-serif; letter-spacing: -0.01em;">
            Analyze &bull; Detect &bull; Explain
        </p>
        <p class="body-text" style="font-size: 18px; margin-bottom: 30px;">
            Combat misinformation with TruthLens—a professional, portfolio-grade analytics platform powered by advanced 
            NLP and machine learning. Ingest multi-format news feeds, curate linguistic corpora, evaluate classification models, 
            and predict article validity with transparent, explainable AI confidence scores.
        </p>
        """,
        unsafe_allow_html=True
    )
    
    # CTA Buttons in clean layout
    btn_col1, btn_col2 = st.columns([1, 1])
    with btn_col1:
        if st.button("Launch Platform", key="home_cta_launch", use_container_width=True):
            st.switch_page("pages/upload.py")
    with btn_col2:
        if st.button("System Configuration", key="home_cta_settings", use_container_width=True, type="secondary"):
            st.switch_page("pages/settings.py")

with col2:
    # Large logo visualization in hero area
    render_logo(width_percent=75)

# Horizontal Workflow Diagram
st.markdown('<h2 class="section-heading">Platform Workflow Pipeline</h2>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="workflow-container">
        <div class="workflow-card">
            <div class="workflow-step-num">Step 01</div>
            <div class="workflow-step-name">📂 Upload Dataset</div>
        </div>
        <div class="workflow-arrow">→</div>
        <div class="workflow-card">
            <div class="workflow-step-num">Step 02</div>
            <div class="workflow-step-name">🧹 Data Prep</div>
        </div>
        <div class="workflow-arrow">→</div>
        <div class="workflow-card">
            <div class="workflow-step-num">Step 03</div>
            <div class="workflow-step-name">📊 Dashboard</div>
        </div>
        <div class="workflow-arrow">→</div>
        <div class="workflow-card">
            <div class="workflow-step-num">Step 04</div>
            <div class="workflow-step-name">🤖 Train Model</div>
        </div>
        <div class="workflow-arrow">→</div>
        <div class="workflow-card">
            <div class="workflow-step-num">Step 05</div>
            <div class="workflow-step-name">📰 Detect News</div>
        </div>
        <div class="workflow-arrow">→</div>
        <div class="workflow-card">
            <div class="workflow-step-num">Step 06</div>
            <div class="workflow-step-name">📑 Reports</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Feature Highlights Section
st.markdown('<h2 class="section-heading">Key Capabilities</h2>', unsafe_allow_html=True)
feat_col1, feat_col2, feat_col3 = st.columns(3)

with feat_col1:
    st.markdown(
        """
        <div class="glass-card accent-border-primary" style="height: 100%;">
            <h3 class="card-title">
                <span style="color: #3B82F6;">✨</span> Linguistic Processing
            </h3>
            <p class="body-text">
                Clean and structure unstructured text feeds. Tokenize sentences, remove stopwords, stem/lemmatize 
                using NLTK libraries to build high-quality vector models.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with feat_col2:
    st.markdown(
        """
        <div class="glass-card accent-border-success" style="height: 100%;">
            <h3 class="card-title">
                <span style="color: #10B981;">📈</span> Multi-Model Evaluator
            </h3>
            <p class="body-text">
                Train models including Logistic Regression, Random Forest, and Naive Bayes. Compare cross-validation 
                metrics, F1-scores, accuracy, and ROC-AUC curves.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with feat_col3:
    st.markdown(
        """
        <div class="glass-card accent-border-warning" style="height: 100%;">
            <h3 class="card-title">
                <span style="color: #F59E0B;">👁</span> Explainable Predictions
            </h3>
            <p class="body-text">
                Scan single articles or web URLs. Get a clean, color-coded probability rating alongside highlighted 
                terms contributing to the truth or bias score.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Technology Stack Section
st.markdown('<h2 class="section-heading">Technology Ecosystem</h2>', unsafe_allow_html=True)
tech_col1, tech_col2, tech_col3, tech_col4, tech_col5 = st.columns(5)

with tech_col1:
    st.markdown(
        """
        <div class="glass-card" style="text-align: center; padding: 16px !important;">
            <div style="font-size: 28px; margin-bottom: 8px;">🐍</div>
            <div style="font-weight: 600; font-size: 16px;">Python</div>
            <div style="font-size: 13px; color: #64748B;">Core Language</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with tech_col2:
    st.markdown(
        """
        <div class="glass-card" style="text-align: center; padding: 16px !important;">
            <div style="font-size: 28px; margin-bottom: 8px;">📈</div>
            <div style="font-weight: 600; font-size: 16px;">Streamlit</div>
            <div style="font-size: 13px; color: #64748B;">UX Application</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with tech_col3:
    st.markdown(
        """
        <div class="glass-card" style="text-align: center; padding: 16px !important;">
            <div style="font-size: 28px; margin-bottom: 8px;">🤖</div>
            <div style="font-weight: 600; font-size: 16px;">Scikit-Learn</div>
            <div style="font-size: 13px; color: #64748B;">Machine Learning</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with tech_col4:
    st.markdown(
        """
        <div class="glass-card" style="text-align: center; padding: 16px !important;">
            <div style="font-size: 28px; margin-bottom: 8px;">📊</div>
            <div style="font-weight: 600; font-size: 16px;">Plotly / Pandas</div>
            <div style="font-size: 13px; color: #64748B;">Data Analytics</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with tech_col5:
    st.markdown(
        """
        <div class="glass-card" style="text-align: center; padding: 16px !important;">
            <div style="font-size: 28px; margin-bottom: 8px;">🔤</div>
            <div style="font-weight: 600; font-size: 16px;">NLTK</div>
            <div style="font-size: 13px; color: #64748B;">Linguistic NLP</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Quick Navigation Section
st.markdown('<h2 class="section-heading">Quick Shortcuts</h2>', unsafe_allow_html=True)
nav_col1, nav_col2, nav_col3 = st.columns(3)

with nav_col1:
    st.markdown('<div class="glass-card" style="height: 100%;">', unsafe_allow_html=True)
    st.markdown('<h4 class="card-title">📂 Ingest Data</h4>', unsafe_allow_html=True)
    st.markdown('<p class="body-text" style="font-size:15px; margin-bottom: 20px;">Upload raw news corpora or single articles.</p>', unsafe_allow_html=True)
    if st.button("Go to Ingestion", key="nav_btn_upload", use_container_width=True):
        st.switch_page("pages/upload.py")
    st.markdown('</div>', unsafe_allow_html=True)

with nav_col2:
    st.markdown('<div class="glass-card" style="height: 100%;">', unsafe_allow_html=True)
    st.markdown('<h4 class="card-title">🤖 Model Training</h4>', unsafe_allow_html=True)
    st.markdown('<p class="body-text" style="font-size:15px; margin-bottom: 20px;">Train and evaluate classification algorithms.</p>', unsafe_allow_html=True)
    if st.button("Go to Training", key="nav_btn_training", use_container_width=True):
        st.switch_page("pages/training.py")
    st.markdown('</div>', unsafe_allow_html=True)

with nav_col3:
    st.markdown('<div class="glass-card" style="height: 100%;">', unsafe_allow_html=True)
    st.markdown('<h4 class="card-title">📰 Detect Fake News</h4>', unsafe_allow_html=True)
    st.markdown('<p class="body-text" style="font-size:15px; margin-bottom: 20px;">Verify claims and see explainable score breakdowns.</p>', unsafe_allow_html=True)
    if st.button("Go to Detection", key="nav_btn_detect", use_container_width=True):
        st.switch_page("pages/detect.py")
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
render_footer()
