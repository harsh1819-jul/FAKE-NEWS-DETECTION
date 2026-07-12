import streamlit as st
import os
import sys
import platform
import pandas as pd
from utils.ui_components import load_css, render_footer
from services.logger import logger

# Initialize style and logs
load_css()
logger.info("Rendering Settings page.")

st.markdown('<div class="page-title">⚙ Platform Configuration & Settings</div>', unsafe_allow_html=True)

# Helper function to compute directory statistics
def get_directory_stats(dir_name):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_path = os.path.join(root_dir, dir_name)
    
    if not os.path.exists(target_path):
        return {"Status": "🔴 Missing", "Files": 0, "Size (KB)": 0.0}
    
    file_count = 0
    total_size = 0
    for root, _, files in os.walk(target_path):
        for f in files:
            file_count += 1
            try:
                total_size += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
                
    return {
        "Status": "🟢 Active",
        "Files": file_count,
        "Size (KB)": round(total_size / 1024.0, 2)
    }

# Create Tabs
tab_info, tab_structure, tab_theme = st.tabs([
    "📊 System Status & Information",
    "📁 Project Structure",
    "🎨 Design System"
])

with tab_info:
    col_info_left, col_info_right = st.columns(2)
    
    with col_info_left:
        st.markdown(
            """
            <div class="glass-card accent-border-primary" style="height: 100%;">
                <h3 class="card-title">ℹ Application Information</h3>
                <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <td style="padding: 10px 0; font-weight: 600; color: #38BDF8;">Name</td>
                        <td style="padding: 10px 0; color: #F8FAFC; text-align: right;">TruthLens</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <td style="padding: 10px 0; font-weight: 600; color: #38BDF8;">Version</td>
                        <td style="padding: 10px 0; color: #F8FAFC; text-align: right;">1.0.0-Beta (Phase 1)</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <td style="padding: 10px 0; font-weight: 600; color: #38BDF8;">Build Stage</td>
                        <td style="padding: 10px 0; color: #F8FAFC; text-align: right;">Project Foundation</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <td style="padding: 10px 0; font-weight: 600; color: #38BDF8;">Environment</td>
                        <td style="padding: 10px 0; color: #F8FAFC; text-align: right;">Local Workstation</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px 0; font-weight: 600; color: #38BDF8;">Target Architecture</td>
                        <td style="padding: 10px 0; color: #F8FAFC; text-align: right;">Modular Pipeline</td>
                    </tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col_info_right:
        st.markdown(
            """
            <div class="glass-card accent-border-success" style="height: 100%;">
                <h3 class="card-title">🖥 System Status</h3>
                <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <td style="padding: 10px 0; font-weight: 600; color: #22C55E;">OS Platform</td>
                        <td style="padding: 10px 0; color: #F8FAFC; text-align: right;">""" + str(platform.system()) + " " + str(platform.release()) + """</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <td style="padding: 10px 0; font-weight: 600; color: #22C55E;">Python Version</td>
                        <td style="padding: 10px 0; color: #F8FAFC; text-align: right;">""" + str(sys.version.split()[0]) + """</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <td style="padding: 10px 0; font-weight: 600; color: #22C55E;">Streamlit Version</td>
                        <td style="padding: 10px 0; color: #F8FAFC; text-align: right;">""" + str(st.__version__) + """</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <td style="padding: 10px 0; font-weight: 600; color: #22C55E;">Process ID</td>
                        <td style="padding: 10px 0; color: #F8FAFC; text-align: right;">""" + str(os.getpid()) + """</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px 0; font-weight: 600; color: #22C55E;">Platform Port</td>
                        <td style="padding: 10px 0; color: #F8FAFC; text-align: right;">8501 (Default)</td>
                    </tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Directory usage table
    st.markdown('<h3 class="section-heading">Directory Diagnostics</h3>', unsafe_allow_html=True)
    
    directories = ["database", "uploads", "cleaned_data", "models", "reports", "logs"]
    dir_data = []
    
    for folder in directories:
        stats = get_directory_stats(folder)
        dir_data.append({
            "Directory": f"{folder}/",
            "System Status": stats["Status"],
            "Files Cached": stats["Files"],
            "Disk Space Usage": f"{stats['Size (KB)']} KB"
        })
        
    df_dirs = pd.DataFrame(dir_data)
    st.dataframe(df_dirs, use_container_width=True, hide_index=True)
    
    st.markdown(
        """
        <div class="glass-card accent-border-primary" style="margin-top: 25px;">
            <h3 class="card-title">📝 Developer Notes</h3>
            <p class="body-text">
                TruthLens has been built following a clean architectural design. Separation of concerns is 
                maintained across layers: presentation (Streamlit views), utilities (shared UI components), 
                and services (rotating logger). The SQLite database and machine learning models are sandboxed 
                within local file scopes.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with tab_structure:
    st.markdown(
        """
        <div class="glass-card accent-border-primary">
            <h3 class="card-title">📁 Project Structure Overview</h3>
            <p class="body-text" style="margin-bottom: 20px;">
                Below is the file tree representing the current workspace directory for TruthLens. Each folder 
                houses modular units isolating computational processing from the UI presentation layer.
            </p>
            <pre style="background: rgba(15, 23, 42, 0.6); color: #38BDF8; font-family: 'Courier New', monospace; 
                       font-size: 15px; padding: 20px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); 
                       line-height: 1.4; overflow-x: auto;">
TruthLens/
├── .streamlit/
│   └── config.toml          # Custom theme variables
├── assets/
│   ├── logo.svg             # SVG Vector Logo
│   └── style.css            # Custom CSS definitions
├── cleaned_data/            # Cleaned data files (Phase 2)
├── database/                # SQLite datasets (Phase 2)
├── logs/                    # Rotating log files
│   └── truthlens.log        # Core execution log
├── models/                  # Serialized Scikit-Learn models (Phase 2)
├── pages/                   # Multi-page application views
│   ├── home.py              # Platform home page
│   ├── upload.py            # Dataset upload preview
│   ├── preparation.py       # Data cleaning preview
│   ├── dashboard.py         # Statistical analysis preview
│   ├── training.py          # Classifier training preview
│   ├── detect.py            # Article detection preview
│   ├── reports_page.py      # PDF report generator preview
│   └── settings.py          # System config (This View)
├── reports/                 # Output PDF storage (Phase 2)
├── services/                # Backend processing logs
│   └── logger.py            # Logging setup
├── tests/                   # Test modules
├── uploads/                 # Raw dataset uploads (Phase 2)
├── utils/                   # Shared presentation logic
│   └── ui_components.py     # Custom cards, headers, footers
├── app.py                   # Global system entrypoint
├── README.md                # Platform documentation
└── requirements.txt         # Project libraries list
            </pre>
        </div>
        """,
        unsafe_allow_html=True
    )

with tab_theme:
    st.markdown(
        """
        <div class="glass-card accent-border-primary">
            <h3 class="card-title">🎨 Theme &amp; Typography Tokens</h3>
            <p class="body-text" style="margin-bottom: 20px; color: #4B5563;">
                TruthLens utilizes a premium, print-inspired light-mode Flat Design system. Color selections are graphic and high-contrast, rejecting depth gradients and blurs.
            </p>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin-bottom: 30px;">
                <div style="background: #FFFFFF; border: 2px solid #E5E7EB; border-radius: 8px; padding: 15px; text-align: center;">
                    <div style="width: 30px; height: 30px; background: #FFFFFF; margin: 0 auto 10px; border-radius: 50%; border: 2px solid #E5E7EB;"></div>
                    <div style="font-weight: 700; font-size: 15px; color: #111827;">Background</div>
                    <div style="font-size: 13px; color: #6B7280;">#FFFFFF</div>
                </div>
                <div style="background: #FFFFFF; border: 2px solid #E5E7EB; border-radius: 8px; padding: 15px; text-align: center;">
                    <div style="width: 30px; height: 30px; background: #F3F4F6; margin: 0 auto 10px; border-radius: 50%; border: 2px solid #E5E7EB;"></div>
                    <div style="font-weight: 700; font-size: 15px; color: #111827;">Cards / Muted</div>
                    <div style="font-size: 13px; color: #6B7280;">#F3F4F6</div>
                </div>
                <div style="background: #FFFFFF; border: 2px solid #E5E7EB; border-radius: 8px; padding: 15px; text-align: center;">
                    <div style="width: 30px; height: 30px; background: #3B82F6; margin: 0 auto 10px; border-radius: 50%;"></div>
                    <div style="font-weight: 700; font-size: 15px; color: #111827;">Primary</div>
                    <div style="font-size: 13px; color: #6B7280;">#3B82F6</div>
                </div>
                <div style="background: #FFFFFF; border: 2px solid #E5E7EB; border-radius: 8px; padding: 15px; text-align: center;">
                    <div style="width: 30px; height: 30px; background: #10B981; margin: 0 auto 10px; border-radius: 50%;"></div>
                    <div style="font-weight: 700; font-size: 15px; color: #111827;">Secondary / Success</div>
                    <div style="font-size: 13px; color: #6B7280;">#10B981</div>
                </div>
                <div style="background: #FFFFFF; border: 2px solid #E5E7EB; border-radius: 8px; padding: 15px; text-align: center;">
                    <div style="width: 30px; height: 30px; background: #F59E0B; margin: 0 auto 10px; border-radius: 50%;"></div>
                    <div style="font-weight: 700; font-size: 15px; color: #111827;">Warning / Accent</div>
                    <div style="font-size: 13px; color: #6B7280;">#F59E0B</div>
                </div>
                <div style="background: #FFFFFF; border: 2px solid #E5E7EB; border-radius: 8px; padding: 15px; text-align: center;">
                    <div style="width: 30px; height: 30px; background: #EF4444; margin: 0 auto 10px; border-radius: 50%;"></div>
                    <div style="font-weight: 700; font-size: 15px; color: #111827;">Danger</div>
                    <div style="font-size: 13px; color: #6B7280;">#EF4444</div>
                </div>
            </div>
            
            <h4 class="card-title" style="margin-top: 20px;">Typography Hierarchy</h4>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="border-bottom: 3px solid #E5E7EB; text-align: left;">
                        <th style="padding: 10px; color: #3B82F6; font-family: 'Outfit', sans-serif;">Element</th>
                        <th style="padding: 10px; color: #3B82F6; font-family: 'Outfit', sans-serif;">Font Family</th>
                        <th style="padding: 10px; color: #3B82F6; font-family: 'Outfit', sans-serif;">Font Size</th>
                        <th style="padding: 10px; color: #3B82F6; font-family: 'Outfit', sans-serif;">Weight</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom: 1px solid #E5E7EB;">
                        <td style="padding: 10px; color: #111827;">Hero Title</td>
                        <td style="padding: 10px; font-style: italic; color: #4B5563;">Outfit</td>
                        <td style="padding: 10px; font-weight: 700; color: #111827;">48px</td>
                        <td style="padding: 10px; color: #4B5563;">800 (Extra Bold)</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #E5E7EB;">
                        <td style="padding: 10px; color: #111827;">Page Title</td>
                        <td style="padding: 10px; font-style: italic; color: #4B5563;">Outfit</td>
                        <td style="padding: 10px; font-weight: 700; color: #111827;">32px</td>
                        <td style="padding: 10px; color: #4B5563;">800 (Extra Bold)</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #E5E7EB;">
                        <td style="padding: 10px; color: #111827;">Section Heading</td>
                        <td style="padding: 10px; font-style: italic; color: #4B5563;">Outfit</td>
                        <td style="padding: 10px; font-weight: 700; color: #111827;">24px</td>
                        <td style="padding: 10px; color: #4B5563;">700 (Bold)</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #E5E7EB;">
                        <td style="padding: 10px; color: #111827;">Card Title</td>
                        <td style="padding: 10px; font-style: italic; color: #4B5563;">Outfit</td>
                        <td style="padding: 10px; font-weight: 700; color: #111827;">20px</td>
                        <td style="padding: 10px; color: #4B5563;">700 (Bold)</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #E5E7EB;">
                        <td style="padding: 10px; color: #111827;">Body Text</td>
                        <td style="padding: 10px; font-style: italic; color: #4B5563;">Outfit</td>
                        <td style="padding: 10px; font-weight: 700; color: #111827;">17px</td>
                        <td style="padding: 10px; color: #4B5563;">400 (Regular)</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #E5E7EB;">
                        <td style="padding: 10px; color: #111827;">Button Text</td>
                        <td style="padding: 10px; font-style: italic; color: #4B5563;">Outfit</td>
                        <td style="padding: 10px; font-weight: 700; color: #111827;">16px</td>
                        <td style="padding: 10px; color: #4B5563;">600 (Semi Bold)</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; color: #111827;">Sidebar Text</td>
                        <td style="padding: 10px; font-style: italic; color: #4B5563;">Outfit</td>
                        <td style="padding: 10px; font-weight: 700; color: #111827;">16px</td>
                        <td style="padding: 10px; color: #4B5563;">600 (Semi Bold)</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True
    )

render_footer()
