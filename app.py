import streamlit as st
import os
from services.logger import logger
from utils.ui_components import load_css

# st.set_page_config must be called as the very first streamlit command.
st.set_page_config(
    page_title="TruthLens - Fake News Detection & Analytics Platform",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load global CSS custom rules
load_css()

# Configure logger info
logger.info("TruthLens platform initialized.")

# Define pages for multi-page routing
home_page = st.Page("pages/home.py", title="Home", icon="🏠", default=True)
upload_page = st.Page("pages/upload.py", title="Upload Dataset", icon="📂")
prep_page = st.Page("pages/preparation.py", title="Data Preparation", icon="🧹")
dashboard_page = st.Page("pages/dashboard.py", title="Dashboard", icon="📊")
training_page = st.Page("pages/training.py", title="Model Training", icon="🤖")
detect_page = st.Page("pages/detect.py", title="Detect News", icon="📰")
reports_page = st.Page("pages/reports_page.py", title="Reports", icon="📑")
settings_page = st.Page("pages/settings.py", title="Settings", icon="⚙")

# Build navigation
navigation_list = [
    home_page,
    upload_page,
    prep_page,
    dashboard_page,
    training_page,
    detect_page,
    reports_page,
    settings_page
]

pg = st.navigation(navigation_list)

# Load sidebar logo
logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.svg")
if os.path.exists(logo_path):
    st.logo(logo_path, icon_image=logo_path)

# Execute page routing
pg.run()
