import streamlit as st
import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
import plotly.express as px
from utils.ui_components import load_css, render_footer
from services.logger import logger
import services.db_service as db

load_css()
logger.info("Rendering Model Training page.")

st.markdown('<div class="page-title">🤖 Model Training Studio</div>', unsafe_allow_html=True)

# Select dataset
datasets_df = db.get_datasets()

if len(datasets_df) == 0:
    st.info("No datasets found in the database. Please go to 'Upload Dataset' to ingest news first.")
else:
    ds_options = {row["name"]: row["id"] for _, row in datasets_df.iterrows()}
    selected_ds_name = st.selectbox("Select Dataset for Training", options=list(ds_options.keys()))
    selected_ds_id = ds_options[selected_ds_name]
    
    # Query articles
    articles_df = db.get_articles(selected_ds_id)
    cleaned_df = articles_df[articles_df["clean_text"].notna() & (articles_df["clean_text"] != "")]
    
    if len(cleaned_df) == 0:
        st.warning(
            "⚠️ Preprocessed data not found for this dataset! You must pre-process the text "
            "before training a classifier. Go to 'Data Preparation' to clean the text first."
        )
    else:
        st.markdown(f"**Ingested Corpus Size:** `{len(cleaned_df)}` preprocessed articles ready.")
        
        # 1. Feature Extraction Settings
        st.markdown('<h3 class="section-heading">1. Feature Extraction (Text Vectorization)</h3>', unsafe_allow_html=True)
        col_vec1, col_vec2, col_vec3 = st.columns(3)
        
        with col_vec1:
            vec_type = st.selectbox("Vectorizer Type", ["TF-IDF Vectorizer", "Count Vectorizer"])
        with col_vec2:
            ngram_select = st.selectbox("N-Gram Range", ["Unigrams Only (1, 1)", "Unigrams & Bigrams (1, 2)", "Bigrams Only (2, 2)"])
            # Map selection to tuple
            if ngram_select == "Unigrams Only (1, 1)":
                ngram_range = (1, 1)
            elif ngram_select == "Unigrams & Bigrams (1, 2)":
                ngram_range = (1, 2)
            else:
                ngram_range = (2, 2)
        with col_vec3:
            max_features = st.slider("Max Vocabulary Features", min_value=100, max_value=5000, value=1000, step=100)

        # 2. Algorithm Configuration
        st.markdown('<h3 class="section-heading">2. Classifier Algorithm Settings</h3>', unsafe_allow_html=True)
        
        col_alg1, col_alg2 = st.columns([1, 2])
        
        with col_alg1:
            algorithm = st.selectbox("Algorithm", ["Logistic Regression", "Multinomial Naive Bayes", "Random Forest"])
            
        with col_alg2:
            # Render parameters based on selection
            if algorithm == "Logistic Regression":
                c_val = st.slider("Regularization Strength (C)", min_value=0.01, max_value=10.0, value=1.0, step=0.05,
                                  help="Smaller values specify stronger regularization.")
                penalty = "l2" # Standard
            elif algorithm == "Multinomial Naive Bayes":
                alpha = st.slider("Smoothing Parameter (Alpha)", min_value=0.1, max_value=2.0, value=1.0, step=0.1,
                                  help="Laplace/Lidstone smoothing parameter.")
            else:
                n_est = st.slider("Number of Trees", min_value=10, max_value=150, value=50, step=10)
                max_depth = st.slider("Max Tree Depth", min_value=3, max_value=20, value=10)

        # Train Config
        st.markdown('<h3 class="section-heading">3. Training Control</h3>', unsafe_allow_html=True)
        
        test_pct = st.slider("Test Set Split Ratio (%)", min_value=10, max_value=50, value=20, step=5)
        model_name = st.text_input("Enter Model Version Name", value=f"truthlens_{selected_ds_name.lower()}_{algorithm.lower().replace(' ', '_')}")

        if st.button("Fit & Evaluate Model", use_container_width=True):
            try:
                with st.spinner("Splitting data and vectorizing text..."):
                    # Split data
                    texts = cleaned_df["clean_text"].tolist()
                    labels = cleaned_df["label"].tolist()
                    
                    # Convert labels to binary if string
                    y = np.array(labels)
                    
                    X_train_text, X_test_text, y_train, y_test = train_test_split(
                        texts, y, test_size=(test_pct / 100.0), random_state=42, stratify=y
                    )
                    
                    # Vectorize
                    if vec_type == "TF-IDF Vectorizer":
                        vectorizer = TfidfVectorizer(ngram_range=ngram_range, max_features=max_features)
                    else:
                        vectorizer = CountVectorizer(ngram_range=ngram_range, max_features=max_features)
                        
                    X_train = vectorizer.fit_transform(X_train_text)
                    X_test = vectorizer.transform(X_test_text)
                    
                with st.spinner("Fitting classifier model..."):
                    # Select and fit
                    if algorithm == "Logistic Regression":
                        clf = LogisticRegression(C=c_val, penalty=penalty, max_iter=1000, random_state=42)
                    elif algorithm == "Multinomial Naive Bayes":
                        clf = MultinomialNB(alpha=alpha)
                    else:
                        clf = RandomForestClassifier(n_estimators=n_est, max_depth=max_depth, random_state=42)
                        
                    clf.fit(X_train, y_train)
                    
                # Predictions
                y_pred = clf.predict(X_test)
                
                # Metrics
                acc = accuracy_score(y_test, y_pred)
                prec = precision_score(y_test, y_pred, pos_label="Real", average='binary')
                rec = recall_score(y_test, y_pred, pos_label="Real", average='binary')
                f1 = f1_score(y_test, y_pred, pos_label="Real", average='binary')
                
                # Render results
                st.success("🎉 Model trained successfully!")
                
                st.markdown('<h3 class="section-heading">Evaluation Metrics</h3>', unsafe_allow_html=True)
                
                col_met1, col_met2, col_met3, col_met4 = st.columns(4)
                with col_met1:
                    st.metric("Test Accuracy", f"{acc:.2%}")
                with col_met2:
                    st.metric("Precision (Real)", f"{prec:.2%}")
                with col_met3:
                    st.metric("Recall (Real)", f"{rec:.2%}")
                with col_met4:
                    st.metric("F1-Score (Real)", f"{f1:.2%}")
                    
                # Classification Report details
                st.markdown("**Classification Summary:**")
                report_dict = classification_report(y_test, y_pred, output_dict=True)
                df_rep = pd.DataFrame(report_dict).transpose()
                st.dataframe(df_rep.style.format(precision=4), use_container_width=True)
                
                # Confusion Matrix Heatmap using Plotly
                st.markdown('<h3 class="section-heading">Confusion Matrix</h3>', unsafe_allow_html=True)
                cm = confusion_matrix(y_test, y_pred, labels=["Real", "Fake"])
                
                # Plotly Heatmap
                fig_cm = px.imshow(
                    cm,
                    labels=dict(x="Predicted Label", y="True Label", color="Count"),
                    x=["Real", "Fake"],
                    y=["Real", "Fake"],
                    color_continuous_scale="Blues",
                    text_auto=True,
                    title="Confusion Matrix (Real vs. Fake)"
                )
                fig_cm.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color="#F8FAFC"
                )
                st.plotly_chart(fig_cm, use_container_width=True)
                
                # Model Serialization (joblib)
                with st.spinner("Saving model artifacts to disk..."):
                    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    models_dir = os.path.join(root_dir, "models")
                    os.makedirs(models_dir, exist_ok=True)
                    
                    model_path = os.path.join(models_dir, f"{model_name}_model.joblib")
                    vectorizer_path = os.path.join(models_dir, f"{model_name}_vectorizer.joblib")
                    meta_path = os.path.join(models_dir, f"{model_name}_meta.json")
                    
                    joblib.dump(clf, model_path)
                    joblib.dump(vectorizer, vectorizer_path)
                    
                    # Metadata config
                    meta_info = {
                        "model_name": model_name,
                        "algorithm": algorithm,
                        "vectorizer_type": vec_type,
                        "ngram_range": [int(ngram_range[0]), int(ngram_range[1])],
                        "max_features": max_features,
                        "split_pct": test_pct,
                        "accuracy": float(acc),
                        "f1_score": float(f1),
                        "created_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    with open(meta_path, "w", encoding="utf-8") as f:
                        json.dump(meta_info, f, indent=4)
                        
                st.info(f"💾 Saved trained models:\n* `{os.path.basename(model_path)}` \n* `{os.path.basename(vectorizer_path)}` \n* `{os.path.basename(meta_path)}`")
                
            except Exception as e:
                st.error(f"Training failed: {str(e)}")
                logger.error(f"Error during training: {str(e)}")

render_footer()
