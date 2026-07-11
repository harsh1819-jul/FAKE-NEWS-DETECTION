import streamlit as st
import os
from services.logger import logger

def load_css():
    """
    Reads the style.css file and injects it into the Streamlit application.
    """
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        css_path = os.path.join(root_dir, "assets", "style.css")
        if os.path.exists(css_path):
            with open(css_path, "r", encoding="utf-8") as f:
                css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
            logger.info("Custom CSS styling loaded successfully.")
        else:
            logger.warning(f"CSS file not found at {css_path}")
    except Exception as e:
        logger.error(f"Error loading CSS: {str(e)}")

@st.cache_data
def get_svg_logo_content():
    """
    Reads assets/logo.svg and returns the raw string content. Cached for performance.
    """
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(root_dir, "assets", "logo.svg")
        if os.path.exists(logo_path):
            with open(logo_path, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        logger.error(f"Error loading SVG logo: {str(e)}")
    return ""

def render_logo(width_percent=60):
    """
    Renders the custom SVG logo directly on the page/sidebar using st.image.
    """
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(root_dir, "assets", "logo.svg")
        if os.path.exists(logo_path):
            st.image(logo_path, width=180)
            logger.info("SVG logo rendered using st.image.")
        else:
            logger.warning(f"Logo path not found: {logo_path}")
    except Exception as e:
        logger.error(f"Error rendering SVG logo: {str(e)}")

def render_footer():
    """
    Renders the unified platform footer.
    """
    footer_html = """
    <div class="footer-text">
        © 2026 TruthLens Platform. Analyze • Detect • Explain. Built for Premium Portfolio Showcase.
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

def render_phase2_preview(page_title, description, icon, features, workflow_steps):
    """
    Renders a premium, interactive preview page for features slated for Phase 2.
    
    Args:
        page_title (str): Title of the page
        description (str): Short description of the feature
        icon (str): Emoji icon representing the page
        features (list): List of strings representing planned features
        workflow_steps (list): List of strings representing steps in the pipeline
    """
    load_css()
    
    # Page Header Card
    st.markdown(
        f"""
        <div class="page-title">{icon} {page_title}</div>
        <div class="glass-card accent-border-primary" style="margin-bottom: 30px;">
            <p class="body-text" style="font-size: 19px; color: #F8FAFC; margin-bottom: 0;">
                {description}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            """
            <div class="glass-card accent-border-success" style="height: 100%;">
                <h3 class="card-title">
                    <span style="color: #22C55E;">✔</span> Core Modules & Capabilities
                </h3>
                <ul class="body-text" style="margin-left: 20px; padding-left: 0;">
            """,
            unsafe_allow_html=True
        )
        for feature in features:
            st.markdown(f'<li class="body-text" style="margin-bottom: 8px;">{feature}</li>', unsafe_allow_html=True)
        st.markdown("</ul></div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown(
            """
            <div class="glass-card accent-border-warning" style="height: 100%;">
                <h3 class="card-title">
                    <span style="color: #F59E0B;">⚙</span> Processing Pipeline
                </h3>
                <div style="margin-top: 15px;">
            """,
            unsafe_allow_html=True
        )
        for idx, step in enumerate(workflow_steps, 1):
            st.markdown(
                f"""
                <div style="display: flex; align-items: flex-start; margin-bottom: 12px; gap: 12px;">
                    <div style="background: rgba(245, 158, 11, 0.1); color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.2); 
                                border-radius: 50%; width: 26px; height: 26px; display: flex; align-items: center; 
                                justify-content: center; font-size: 13px; font-weight: 700; flex-shrink: 0;">
                        {idx}
                    </div>
                    <div class="body-text" style="margin-top: 2px;">{step}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown("</div></div>", unsafe_allow_html=True)
        
    # Technical Architecture Callout
    st.markdown(
        """
        <div style="background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.15); 
                    border-radius: 12px; padding: 20px; margin-top: 30px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
            <div style="color: #38BDF8; font-weight: 700; font-size: 18px; margin-bottom: 6px; font-family: 'Poppins', sans-serif;">
                🔒 Phase 2 Architecture Ready
            </div>
            <div class="body-text" style="font-size: 16px;">
                The backend service interfaces and schema templates have been established. Natural Language Processing (NLP), 
                tokenizers, and machine learning model loaders will be integrated seamlessly during the Phase 2 update.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    render_footer()
