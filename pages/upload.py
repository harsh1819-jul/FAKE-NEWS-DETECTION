import streamlit as st
import pandas as pd
from utils.ui_components import load_css, render_footer
from services.logger import logger
import services.db_service as db

load_css()
logger.info("Rendering Upload Dataset page.")

st.markdown('<div class="page-title">📂 Upload Dataset & Ingest Feeds</div>', unsafe_allow_html=True)

# Main container split
col_upload, col_sample = st.columns([3, 2])

with col_upload:
    st.markdown(
        """
        <div class="glass-card accent-border-primary">
            <h3 class="card-title">📁 Import Local Dataset File</h3>
            <p class="body-text" style="font-size: 15px;">
                Upload your news database in CSV, Excel, or JSON format. Once uploaded, map the text fields to configure the ingestion engine.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    uploaded_file = st.file_uploader(
        "Choose file...", 
        type=["csv", "xlsx", "xls", "json"], 
        label_visibility="collapsed"
    )

with col_sample:
    st.markdown(
        """
        <div class="glass-card accent-border-warning" style="height: 100%;">
            <h3 class="card-title">💡 Instant Portfolio Testing</h3>
            <p class="body-text" style="font-size: 15px;">
                Don't have a dataset? Populate the system with 200 synthetic articles containing distinct vocabularies for real and fake news.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Render button beneath card
    if st.button("Load Portfolio Sample Dataset", use_container_width=True):
        try:
            with st.spinner("Generating sample articles..."):
                sample_df = db.generate_portfolio_sample_dataset()
                # Check if sample already uploaded
                existing = db.get_datasets()
                sample_name = "TruthLens_Synthetic_Sample_v1"
                
                if sample_name in existing["name"].values:
                    st.warning("Sample dataset already exists in the database.")
                else:
                    db.add_dataset(
                        name=sample_name,
                        df=sample_df,
                        title_col="title",
                        text_col="text",
                        label_col="label",
                        source_col="source"
                    )
                    st.success("🎉 Success! Sample news dataset (200 records) ingested successfully.")
                    st.rerun()
        except Exception as e:
            st.error(f"Error loading sample: {str(e)}")

# Process uploaded file
if uploaded_file is not None:
    st.markdown("---")
    st.markdown('<h3 class="section-heading">Validate & Map Schema</h3>', unsafe_allow_html=True)
    
    try:
        # Load file in Pandas
        file_name = uploaded_file.name
        if file_name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif file_name.endswith(".json"):
            df = pd.read_json(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        st.markdown(f"**Loaded File:** `{file_name}` | **Total Rows:** `{len(df)}` | **Columns:** `{len(df.columns)}`")
        
        # Helper to find best column match by keyword patterns
        def find_col_match(columns, patterns, default_index):
            for i, col in enumerate(columns):
                col_lower = str(col).lower()
                if any(pat in col_lower for pat in patterns):
                    return i
            return min(default_index, len(columns) - 1) if len(columns) > 0 else 0

        title_idx = find_col_match(df.columns, ["title", "headline", "name"], 0)
        text_idx = find_col_match(df.columns, ["text", "body", "content", "article"], min(1, len(df.columns) - 1))
        label_idx = find_col_match(df.columns, ["label", "class", "target", "truth", "category", "fake", "real"], min(2, len(df.columns) - 1))
        source_idx = find_col_match(df.columns, ["source", "pub", "site"], -1)

        source_options = ["None"] + list(df.columns)
        source_default_idx = source_idx + 1 if source_idx != -1 else 0

        # Ingestion form
        with st.form("ingest_form"):
            col_map1, col_map2, col_map3 = st.columns(3)
            
            with col_map1:
                title_col = st.selectbox("Article Title Column", options=df.columns, index=title_idx)
            with col_map2:
                text_col = st.selectbox("Article Body Text Column", options=df.columns, index=text_idx)
            with col_map3:
                label_col = st.selectbox("Article Label/Truth Column", options=df.columns, index=label_idx)
                
            source_col = st.selectbox("Source/Publisher Column (Optional)", options=source_options, index=source_default_idx)
            dataset_custom_name = st.text_input("Ingest Dataset Name", value=file_name.split('.')[0] + "_Ingested")
            
            # Check for duplicate column mappings
            has_duplicates = len(set([title_col, text_col, label_col])) < 3
            
            if has_duplicates:
                st.warning("⚠️ Please map distinct columns for Title, Body Text, and Label/Truth to preview and ingest the dataset.")
                submit_ingest = st.form_submit_button("Start Database Ingestion", use_container_width=True, disabled=True)
            else:
                # Preview sample rows
                st.write("Preview Top 3 Records:")
                st.dataframe(df[[title_col, text_col, label_col]].head(3), use_container_width=True)
                
                submit_ingest = st.form_submit_button("Start Database Ingestion", use_container_width=True)
                
                if submit_ingest:
                    if not dataset_custom_name.strip():
                        st.error("Please provide a name for the ingested dataset.")
                    else:
                        src_mapped = None if source_col == "None" else source_col
                        db.add_dataset(
                            name=dataset_custom_name.strip(),
                            df=df,
                            title_col=title_col,
                            text_col=text_col,
                            label_col=label_col,
                            source_col=src_mapped
                        )
                        st.success(f"Successfully ingested dataset '{dataset_custom_name}' with {len(df)} rows!")
                        st.rerun()
                        
    except Exception as e:
        st.error(f"Error parsing file: {str(e)}")

# Active datasets section
st.markdown("---")
st.markdown('<h3 class="section-heading">Database Catalog</h3>', unsafe_allow_html=True)

datasets_df = db.get_datasets()

if len(datasets_df) == 0:
    st.info("The local database is currently empty. Upload a dataset or load the portfolio sample above.")
else:
    for idx, row in datasets_df.iterrows():
        with st.container():
            st.markdown(
                f"""
                <div class="glass-card accent-border-primary" style="margin-bottom:12px; padding:18px !important;">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                        <div>
                            <span style="font-size:18px; font-weight:800; color:#3B82F6; font-family:'Outfit', sans-serif;">{row['name']}</span>
                            <br>
                            <span style="font-size:13px; color:#6B7280;">Ingested on: {row['uploaded_at']}</span>
                        </div>
                        <div style="text-align:right;">
                            <span style="font-size:16px; font-weight:700; color:#111827; font-family:'Outfit', sans-serif;">{row['row_count']} Articles</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            # Row delete action
            if st.button("Delete Dataset", key=f"del_ds_{row['id']}"):
                try:
                    db.delete_dataset(row['id'])
                    st.success(f"Dataset '{row['name']}' deleted.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error deleting dataset: {str(e)}")

render_footer()
