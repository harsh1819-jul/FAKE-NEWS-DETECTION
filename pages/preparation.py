import streamlit as st
import os
import pandas as pd
from utils.ui_components import load_css, render_footer
from services.logger import logger
import services.db_service as db
import services.nlp_service as nlp

load_css()
logger.info("Rendering Data Preparation page.")

st.markdown('<div class="page-title">🧹 Text Preprocessing & Cleaning</div>', unsafe_allow_html=True)

# Select dataset
datasets_df = db.get_datasets()

if len(datasets_df) == 0:
    st.info("No datasets found in the database. Please go to 'Upload Dataset' to ingest news first.")
else:
    # Build list of options
    ds_options = {row["name"]: row["id"] for _, row in datasets_df.iterrows()}
    selected_ds_name = st.selectbox("Select Ingested Dataset to Preprocess", options=list(ds_options.keys()))
    selected_ds_id = ds_options[selected_ds_name]
    
    # Query articles count
    articles_df = db.get_articles(selected_ds_id)
    cleaned_count = articles_df["clean_text"].notna().sum()
    
    st.markdown(
        f"**Selected Dataset:** `{selected_ds_name}` | **Total Articles:** `{len(articles_df)}` | **Already Preprocessed:** `{cleaned_count}`"
    )
    
    # Cleaning Configurations
    st.markdown('<h3 class="section-heading">NLP Cleaners Configuration</h3>', unsafe_allow_html=True)
    
    col_cfg1, col_cfg2, col_cfg3 = st.columns(3)
    
    with col_cfg1:
        remove_stopwords = st.toggle("Remove English Stopwords", value=True, help="Removes meaningless words like 'the', 'is', 'at'.")
    with col_cfg2:
        use_lemmatization = st.toggle("Apply WordNet Lemmatization", value=True, help="Reduces words to their semantic root (e.g. 'running' -> 'run').")
    with col_cfg3:
        use_stemming = st.toggle("Apply Porter Stemming", value=False, disabled=use_lemmatization, help="Cuts off word suffixes aggressively. Disabled if Lemmatization is active.")

    # Dry-run Section
    st.markdown('<h3 class="section-heading">Preprocessing Dry Run</h3>', unsafe_allow_html=True)
    
    sample_size = min(3, len(articles_df))
    sample_df = articles_df.head(sample_size)
    
    dry_run_data = []
    for idx, row in sample_df.iterrows():
        cleaned = nlp.clean_text_engine(
            row["text"], 
            use_stemming=use_stemming, 
            use_lemmatization=use_lemmatization, 
            remove_stopwords=remove_stopwords
        )
        dry_run_data.append({
            "Original Text (Truncated)": row["text"][:150] + "...",
            "Cleansed NLP Tokens": cleaned[:150] + "..." if cleaned else ""
        })
        
    df_dry = pd.DataFrame(dry_run_data)
    st.table(df_dry)

    # Bulk preprocessing trigger
    st.markdown('<h3 class="section-heading">Bulk Execution</h3>', unsafe_allow_html=True)
    st.markdown(
        """
        <p class="body-text" style="font-size: 15px; margin-bottom: 20px;">
            Run the preprocessor over the entire dataset. This will tokenize the texts and update the local database. 
            A sanitized CSV backup will also be saved to the <code>cleaned_data/</code> folder.
        </p>
        """,
        unsafe_allow_html=True
    )
    
    if st.button("Start Bulk Preprocessing", use_container_width=True):
        progress_text = "Processing text files..."
        my_bar = st.progress(0, text=progress_text)
        
        article_ids = []
        cleaned_texts = []
        
        total_rows = len(articles_df)
        
        for idx, row in articles_df.iterrows():
            cleaned = nlp.clean_text_engine(
                row["text"],
                use_stemming=use_stemming,
                use_lemmatization=use_lemmatization,
                remove_stopwords=remove_stopwords
            )
            article_ids.append(row["id"])
            cleaned_texts.append(cleaned)
            
            # Update progress bar occasionally
            if (idx + 1) % max(1, total_rows // 20) == 0 or idx + 1 == total_rows:
                pct = int((idx + 1) / total_rows * 100)
                my_bar.progress(pct, text=f"Processed {idx + 1} of {total_rows} articles...")
                
        # Write to Database
        with st.spinner("Writing cleaned tokens to SQLite..."):
            db.update_articles_clean_text(article_ids, cleaned_texts)
            
        # Save to cleaned_data folder as backup CSV
        with st.spinner("Writing CSV backup to cleaned_data/..."):
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cleaned_dir = os.path.join(root_dir, "cleaned_data")
            os.makedirs(cleaned_dir, exist_ok=True)
            
            backup_df = db.get_articles(selected_ds_id)
            backup_file = os.path.join(cleaned_dir, f"{selected_ds_name}_cleaned.csv")
            backup_df.to_csv(backup_file, index=False)
            
        st.success(f"🎉 Preprocessing complete! Cleaned text registered in database. Backup written to {os.path.basename(backup_file)}")
        st.rerun()

render_footer()
