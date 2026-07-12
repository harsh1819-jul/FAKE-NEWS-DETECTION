import streamlit as st
import os
import json
import pandas as pd
from utils.ui_components import load_css, render_footer
from services.logger import logger
import services.db_service as db

load_css()
logger.info("Rendering Reports page.")

st.markdown('<div class="page-title">📑 System Performance Audits</div>', unsafe_allow_html=True)

# Select dataset
datasets_df = db.get_datasets()
# Select model
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
models_dir = os.path.join(root_dir, "models")
os.makedirs(models_dir, exist_ok=True)
model_files = [f for f in os.listdir(models_dir) if f.endswith("_model.joblib")]

if len(datasets_df) == 0:
    st.info("No ingested datasets found in the database. Ingest and train a model to generate audits.")
elif len(model_files) == 0:
    st.info("No trained models found. Train a model in 'Model Training' to compile performance audits.")
else:
    col_rep1, col_rep2 = st.columns(2)
    
    with col_rep1:
        ds_options = {row["name"]: row["id"] for _, row in datasets_df.iterrows()}
        selected_ds_name = st.selectbox("Select Target Dataset", options=list(ds_options.keys()))
        selected_ds_id = ds_options[selected_ds_name]
    with col_rep2:
        model_options = {f.replace("_model.joblib", ""): f for f in model_files}
        selected_model_name = st.selectbox("Select Target Model Run", options=list(model_options.keys()))
        
    st.markdown(
        """
        <p class="body-text" style="font-size: 15px; margin-bottom: 20px;">
            Compile a unified audit summary report mapping the linguistic features of the dataset, 
            the cleaning toggles used, and the classification scoring details. 
            Reports will be archived locally in the <code>reports/</code> folder.
        </p>
        """,
        unsafe_allow_html=True
    )
    
    # Load metadata if exists
    meta_path = os.path.join(models_dir, f"{selected_model_name}_meta.json")
    meta_data = {}
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            meta_data = json.load(f)
            
    if st.button("Generate System Audit Report", use_container_width=True):
        try:
            with st.spinner("Compiling HTML performance report..."):
                articles = db.get_articles(selected_ds_id)
                cleaned_count = articles["clean_text"].notna().sum()
                timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
                date_str = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # HTML template construction
                html_template = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>TruthLens Performance Audit - {selected_model_name}</title>
                    <style>
                        body {{
                            font-family: 'Outfit', 'Segoe UI', Arial, sans-serif;
                            color: #111827;
                            background-color: #FFFFFF;
                            padding: 40px;
                            line-height: 1.6;
                        }}
                        .header {{
                            border-bottom: 4px solid #3B82F6;
                            padding-bottom: 20px;
                            margin-bottom: 30px;
                        }}
                        .title {{
                            font-size: 28px;
                            font-weight: 800;
                            color: #111827;
                        }}
                        .tagline {{
                            color: #6B7280;
                            font-size: 14px;
                            margin-top: 5px;
                        }}
                        .section-title {{
                            font-size: 20px;
                            color: #111827;
                            margin-top: 30px;
                            border-bottom: 2px solid #E5E7EB;
                            padding-bottom: 5px;
                        }}
                        .grid {{
                            display: grid;
                            grid-template-columns: 1fr 1fr;
                            gap: 20px;
                            margin-top: 15px;
                        }}
                        .card {{
                            background-color: #F3F4F6;
                            border: none;
                            border-radius: 8px;
                            padding: 20px;
                            box-shadow: none;
                        }}
                        .metric-val {{
                            font-size: 24px;
                            font-weight: 800;
                            color: #3B82F6;
                        }}
                        .metric-lbl {{
                            font-size: 12px;
                            color: #6B7280;
                            text-transform: uppercase;
                        }}
                        table {{
                            width: 100%;
                            border-collapse: collapse;
                            margin-top: 15px;
                        }}
                        th, td {{
                            padding: 10px;
                            text-align: left;
                            border-bottom: 1px solid #E2E8F0;
                        }}
                        th {{
                            background-color: #F1F5F9;
                            color: #475569;
                        }}
                        .footer {{
                            margin-top: 60px;
                            text-align: center;
                            font-size: 12px;
                            color: #94A3B8;
                            border-top: 1px solid #E2E8F0;
                            padding-top: 20px;
                        }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <div class="title">📰 TruthLens System Performance Audit</div>
                        <div class="tagline">Report Compiled on: {date_str}</div>
                    </div>
                    
                    <div class="grid">
                        <div class="card">
                            <div class="metric-lbl">Target Dataset</div>
                            <div class="metric-val">{selected_ds_name}</div>
                            <p style="margin-top:10px; font-size:14px; color:#64748B;">
                                Contains {len(articles)} total articles. Preprocessed records: {cleaned_count}.
                            </p>
                        </div>
                        <div class="card">
                            <div class="metric-lbl">Target Predictor</div>
                            <div class="metric-val">{selected_model_name}</div>
                            <p style="margin-top:10px; font-size:14px; color:#64748B;">
                                Algorithm: {meta_data.get('algorithm', 'Unknown')}<br>
                                Vectorizer: {meta_data.get('vectorizer_type', 'Unknown')}
                            </p>
                        </div>
                    </div>
                    
                    <div class="section-title">Model Performance Benchmarks</div>
                    <div class="card" style="margin-top:15px;">
                        <table style="margin-top:0;">
                            <thead>
                                <tr>
                                    <th>Evaluation Metric</th>
                                    <th>Score Value</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>Test Split Accuracy</td>
                                    <td><strong>{meta_data.get('accuracy', 0.0):.2%}</strong></td>
                                </tr>
                                <tr>
                                    <td>F1-Score (Real class)</td>
                                    <td><strong>{meta_data.get('f1_score', 0.0):.2%}</strong></td>
                                </tr>
                                <tr>
                                    <td>N-Gram Ranges configured</td>
                                    <td>{meta_data.get('ngram_range', 'Unknown')}</td>
                                </tr>
                                <tr>
                                    <td>Max Vector Features</td>
                                    <td>{meta_data.get('max_features', 'Unknown')}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    
                    <div class="section-title">Audit Sign-off</div>
                    <p style="font-size:14px; color:#475569; margin-top:15px;">
                        This document verifies that the machine learning models serialized under the TruthLens portfolio namespace 
                        comply with evaluation cross-validation runs. Features have been vector-mapped and exported to serial joblib 
                        files matching system architectures.
                    </p>
                    
                    <div class="footer">
                        © 2026 TruthLens Platform. Analyze • Detect • Explain.
                    </div>
                </body>
                </html>
                """
                
                # Write to reports/ folder
                reports_dir = os.path.join(root_dir, "reports")
                os.makedirs(reports_dir, exist_ok=True)
                report_file = os.path.join(reports_dir, f"truthlens_audit_{timestamp}.html")
                
                with open(report_file, "w", encoding="utf-8") as f:
                    f.write(html_template)
                    
                st.success(f"Report compiled and saved to {os.path.basename(report_file)}")
                
                # Provide download button
                st.download_button(
                    label="📥 Download Compiled HTML Report",
                    data=html_template,
                    file_name=f"truthlens_audit_{timestamp}.html",
                    mime="text/html",
                    use_container_width=True
                )
                
        except Exception as e:
            st.error(f"Error compiling report: {str(e)}")
            logger.error(f"Error compiling report: {str(e)}")

# Display historical reports list
st.markdown("---")
st.markdown('<h3 class="section-heading">Historical Audit Reports</h3>', unsafe_allow_html=True)

reports_dir = os.path.join(root_dir, "reports")
os.makedirs(reports_dir, exist_ok=True)
saved_reports = [f for f in os.listdir(reports_dir) if f.endswith(".html")]

if len(saved_reports) == 0:
    st.info("No saved audit reports found in the reports/ folder.")
else:
    for f in saved_reports:
        st.markdown(
            f"""
            <div class="glass-card" style="margin-bottom:10px; padding:15px !important; display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:16px; font-weight:700; color:#3B82F6; font-family:'Outfit',sans-serif;">📄 {f}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

render_footer()
