import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
from utils.ui_components import load_css, render_footer
from services.logger import logger
import services.db_service as db

load_css()
logger.info("Rendering Dashboard page.")

st.markdown('<div class="page-title">📊 Visual Corpus Analytics</div>', unsafe_allow_html=True)

# Select dataset
datasets_df = db.get_datasets()

if len(datasets_df) == 0:
    st.info("No datasets found in the database. Please go to 'Upload Dataset' to ingest news first.")
else:
    ds_options = {row["name"]: row["id"] for _, row in datasets_df.iterrows()}
    selected_ds_name = st.selectbox("Select Ingested Dataset to Visualize", options=list(ds_options.keys()))
    selected_ds_id = ds_options[selected_ds_name]
    
    # Query articles
    articles_df = db.get_articles(selected_ds_id)
    
    # Check if preprocessed data exists
    cleaned_df = articles_df[articles_df["clean_text"].notna() & (articles_df["clean_text"] != "")]
    
    if len(cleaned_df) == 0:
        st.warning(
            "⚠️ This dataset has not been preprocessed yet! Word frequencies and length analytics are unavailable. "
            "Please go to the 'Data Preparation' page to clean the text first."
        )
        
        # Fallback basic visualization (Class distribution only)
        st.markdown('<h3 class="section-heading">Basic Metadata Ingestion</h3>', unsafe_allow_html=True)
        class_counts = articles_df["label"].value_counts().reset_index()
        class_counts.columns = ["Label", "Count"]
        
        fig_pie = px.pie(
            class_counts, 
            values="Count", 
            names="Label", 
            title="Class Balance (Raw Ingested Records)",
            color="Label",
            color_discrete_map={"Real": "#22C55E", "Fake": "#EF4444"}
        )
        fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#F8FAFC")
        st.plotly_chart(fig_pie, use_container_width=True)
        
    else:
        # 1. Summary Metrics
        st.markdown('<h3 class="section-heading">Corpus Metrics</h3>', unsafe_allow_html=True)
        
        # Calculate vocabulary
        all_words = " ".join(cleaned_df["clean_text"]).split()
        vocab_size = len(set(all_words))
        avg_words = np.mean([len(text.split()) for text in cleaned_df["clean_text"]])
        
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        
        with m_col1:
            st.metric("Total Articles Ingested", len(articles_df))
        with m_col2:
            st.metric("Cleaned & Cataloged", len(cleaned_df))
        with m_col3:
            st.metric("Unique Vocabulary Words", f"{vocab_size:,}")
        with m_col4:
            st.metric("Avg Words per Article", f"{avg_words:.1f}")
            
        # Layout columns for main charts
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            # Chart 1: Pie chart of class balance
            class_counts = cleaned_df["label"].value_counts().reset_index()
            class_counts.columns = ["Label", "Count"]
            
            fig_class = px.pie(
                class_counts,
                values="Count",
                names="Label",
                title="Class Balance (Real vs. Fake)",
                color="Label",
                color_discrete_map={"Real": "#22C55E", "Fake": "#EF4444"},
                hole=0.4
            )
            fig_class.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                font_color="#F8FAFC",
                title_font_family="Poppins"
            )
            st.plotly_chart(fig_class, use_container_width=True)
            
        with col_chart2:
            # Chart 2: Histogram of article text lengths
            cleaned_df["word_count"] = cleaned_df["text"].apply(lambda t: len(str(t).split()))
            
            fig_hist = px.histogram(
                cleaned_df,
                x="word_count",
                color="label",
                barmode="overlay",
                title="Article Word Count Distribution",
                color_discrete_map={"Real": "#22C55E", "Fake": "#EF4444"},
                labels={"word_count": "Word Count", "label": "Article Label"}
            )
            fig_hist.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                font_color="#F8FAFC",
                title_font_family="Poppins",
                bargap=0.1
            )
            st.plotly_chart(fig_hist, use_container_width=True)
            
        # Top word counts
        st.markdown('<h3 class="section-heading">Linguistic Word Frequency Analysis</h3>', unsafe_allow_html=True)
        
        word_class_toggle = st.radio(
            "Filter Word Frequency By:",
            options=["Real Articles", "Fake Articles"],
            horizontal=True
        )
        
        # Filter texts based on selection
        target_label = "Real" if word_class_toggle == "Real Articles" else "Fake"
        label_df = cleaned_df[cleaned_df["label"] == target_label]
        
        if len(label_df) > 0:
            words = " ".join(label_df["clean_text"]).split()
            word_counts = Counter(words).most_common(15)
            
            df_words = pd.DataFrame(word_counts, columns=["Word", "Frequency"])
            
            # Plot horizontal bar chart
            bar_color = "#22C55E" if target_label == "Real" else "#EF4444"
            fig_words = px.bar(
                df_words,
                x="Frequency",
                y="Word",
                orientation="h",
                title=f"Top 15 Most Common Words in {target_label} News",
                color_discrete_sequence=[bar_color]
            )
            fig_words.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                font_color="#F8FAFC",
                title_font_family="Poppins",
                yaxis={'categoryorder':'total ascending'}
            )
            st.plotly_chart(fig_words, use_container_width=True)
        else:
            st.info(f"No articles found labeled as '{target_label}' in this dataset.")

        # Publisher analysis
        st.markdown('<h3 class="section-heading">Publisher Credibility Ingestion</h3>', unsafe_allow_html=True)
        
        # Group by source and label
        pub_df = cleaned_df.groupby(["source", "label"]).size().unstack(fill_value=0).reset_index()
        pub_df["Total"] = pub_df.get("Real", 0) + pub_df.get("Fake", 0)
        pub_df = pub_df.sort_values(by="Total", ascending=False).head(10)
        
        if len(pub_df) > 0:
            fig_pub = go.Figure()
            if "Real" in pub_df:
                fig_pub.add_trace(go.Bar(name="Real News", x=pub_df["source"], y=pub_df["Real"], marker_color="#22C55E"))
            if "Fake" in pub_df:
                fig_pub.add_trace(go.Bar(name="Fake News", x=pub_df["source"], y=pub_df["Fake"], marker_color="#EF4444"))
                
            fig_pub.update_layout(
                barmode='stack',
                title="Top 10 Active Publishers & News Classifications",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color="#F8FAFC",
                title_font_family="Poppins"
            )
            st.plotly_chart(fig_pub, use_container_width=True)
        else:
            st.info("No publisher source information found in the dataset.")

render_footer()
