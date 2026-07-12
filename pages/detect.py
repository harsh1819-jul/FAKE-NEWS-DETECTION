import streamlit as st
import os
import joblib
import json
import re
import urllib.request
from utils.ui_components import load_css, render_footer
from services.logger import logger
import services.nlp_service as nlp

load_css()
logger.info("Rendering Detect News page.")

st.markdown('<div class="page-title">📰 Real-Time News Verification</div>', unsafe_allow_html=True)

# Find trained models
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
models_dir = os.path.join(root_dir, "models")
os.makedirs(models_dir, exist_ok=True)

model_files = [f for f in os.listdir(models_dir) if f.endswith("_model.joblib")]

if len(model_files) == 0:
    st.info("No trained models found. Please navigate to 'Model Training' and train a model first.")
else:
    # Model selector
    model_options = {f.replace("_model.joblib", ""): f for f in model_files}
    selected_model_name = st.selectbox("Select Active Prediction Model", options=list(model_options.keys()))
    
    # Load model and matching vectorizer
    model_path = os.path.join(models_dir, model_options[selected_model_name])
    vectorizer_path = os.path.join(models_dir, model_options[selected_model_name].replace("_model.joblib", "_vectorizer.joblib"))
    meta_path = os.path.join(models_dir, model_options[selected_model_name].replace("_model.joblib", "_meta.json"))
    
    try:
        clf = joblib.load(model_path)
        vectorizer = joblib.load(vectorizer_path)
        
        # Load meta if exists
        meta_info = {}
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                meta_info = json.load(f)
                
        st.markdown(
            f"**Model Type:** `{meta_info.get('algorithm', 'Unknown')}` | **Training Accuracy:** `{meta_info.get('accuracy', 0.0):.2%}` | **Features:** `{meta_info.get('max_features', 'Unknown')}`"
        )
        
        # URL scraper helper
        def extract_text_from_url(url):
            try:
                # Add headers to avoid bot blocks
                req = urllib.request.Request(
                    url, 
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                )
                with urllib.request.urlopen(req, timeout=5) as response:
                    html = response.read().decode('utf-8', errors='ignore')
                    
                # Simple regex-based HTML text extractor to avoid extra dependencies
                # Remove script and style tags
                html = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', html)
                html = re.sub(r'<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>', '', html)
                # Remove tags, keep text
                text = re.sub(r'<[^>]+>', ' ', html)
                # Clean up whitespaces
                text = re.sub(r'\s+', ' ', text).strip()
                return text[:2000] # Return first 2000 chars
            except Exception as e:
                logger.error(f"URL extraction failed: {str(e)}")
                return None

        # Input choices
        st.markdown('<h3 class="section-heading">Input Article Content</h3>', unsafe_allow_html=True)
        
        input_mode = st.radio("Input Method:", ["Paste Text Article", "Verify Live Web URL"], horizontal=True)
        
        input_text = ""
        
        if input_mode == "Verify Live Web URL":
            url_input = st.text_input("Enter News Article URL:")
            if st.button("Fetch Article Content") and url_input:
                with st.spinner("Scraping webpage text..."):
                    extracted = extract_text_from_url(url_input)
                    if extracted:
                        st.success("Webpage text fetched successfully!")
                        st.session_state["scraped_news_text"] = extracted
                    else:
                        st.error("Failed to parse website. Please paste the article text manually.")
            
            # Show fetched content if cached
            input_text = st.text_area(
                "Fetched Text Review:", 
                value=st.session_state.get("scraped_news_text", ""), 
                height=200
            )
        else:
            input_text = st.text_area("Paste Article Text Here:", height=250)

        # Predict action
        if st.button("Analyze & Verify Authenticity", use_container_width=True) and input_text.strip():
            # Process text
            cleaned_text = nlp.clean_text_engine(
                input_text,
                use_stemming=False,
                use_lemmatization=True,
                remove_stopwords=True
            )
            
            # Predict
            vec_input = vectorizer.transform([cleaned_text])
            prediction = clf.predict(vec_input)[0]
            
            # Check probabilities
            if hasattr(clf, "predict_proba"):
                probs = clf.predict_proba(vec_input)[0]
                classes = clf.classes_
                prob_map = dict(zip(classes, probs))
                real_prob = prob_map.get("Real", 0.0)
                fake_prob = prob_map.get("Fake", 0.0)
            else:
                # Deciders for RF if predict_proba is missing
                real_prob = 1.0 if prediction == "Real" else 0.0
                fake_prob = 1.0 if prediction == "Fake" else 0.0
                
            # Log audit
            logger.info(f"Article prediction: {prediction} (Real: {real_prob:.2f}, Fake: {fake_prob:.2f})")
            
            # Render predictions
            st.markdown('<h3 class="section-heading">Authentication Assessment</h3>', unsafe_allow_html=True)
            
            if prediction == "Real":
                st.markdown(
                    f"""
                    <div style="background: #D1FAE5; border: 2px solid #10B981; border-radius: 8px; padding: 20px; margin-bottom: 25px;">
                        <span style="font-size: 24px; font-weight: 800; color: #10B981; font-family:'Outfit',sans-serif;">✔ VERIFIED REAL NEWS</span>
                        <p class="body-text" style="margin-top: 8px; color: #111827;">
                            This article exhibits linguistic patterns matching high-quality, reputable reporting. 
                            Confidence rating: <b>{real_prob:.2%}</b>.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div style="background: #FEE2E2; border: 2px solid #EF4444; border-radius: 8px; padding: 20px; margin-bottom: 25px;">
                        <span style="font-size: 24px; font-weight: 800; color: #EF4444; font-family:'Outfit',sans-serif;">🚨 DETECTED FAKE / BIASED NEWS</span>
                        <p class="body-text" style="margin-top: 8px; color: #111827;">
                            This article exhibits sensationalized framing, hyperbole, or vocabulary linked to misinformation. 
                            Confidence rating: <b>{fake_prob:.2%}</b>.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
            # Confidence indicators
            col_gauge1, col_gauge2 = st.columns(2)
            with col_gauge1:
                st.write("**Real News Confidence Probability**")
                st.progress(real_prob)
            with col_gauge2:
                st.write("**Fake News Bias Probability**")
                st.progress(fake_prob)
                
            # 4. Explainable AI Vocabulary highlighting
            st.markdown('<h3 class="section-heading">Explainable AI (Linguistic Token Weightings)</h3>', unsafe_allow_html=True)
            st.markdown(
                """
                <p class="body-text" style="font-size: 15px; margin-bottom: 20px;">
                    Below, key vocabulary terms from the article are colorized according to their influence on the model. 
                    <span style="color: #10B981; font-weight:700;">Green</span> words push the rating toward "Real" facts, while 
                    <span style="color: #EF4444; font-weight:700;">Red</span> words indicate biases or clickbait.
                </p>
                """,
                unsafe_allow_html=True
            )
            
            # Extract coefficients if Logistic Regression or Naive Bayes
            word_weights = {}
            if hasattr(clf, "coef_") and hasattr(vectorizer, "get_feature_names_out"):
                try:
                    features = vectorizer.get_feature_names_out()
                    # Naive Bayes has feature_log_prob_
                    if hasattr(clf, "feature_log_prob_"):
                        # Difference in log probs gives log odds ratio
                        coefs = clf.feature_log_prob_[0] - clf.feature_log_prob_[1]
                    else:
                        coefs = clf.coef_[0]
                        
                    for term, weight in zip(features, coefs):
                        word_weights[term] = weight
                except Exception as e:
                    logger.warning(f"Failed to extract model coefficients: {str(e)}")

            # Highlight text
            # Tokenize original words but preserve formatting/case
            words_in_text = re.findall(r'\b\w+\b|\s+|[^\w\s]', input_text)
            
            highlighted_spans = []
            for w in words_in_text:
                if re.match(r'^\w+$', w):
                    # Clean word to lookup in coefficients
                    # Must match same cleaning: lowercase and lemmatized
                    clean_w = w.lower()
                    try:
                        from nltk.stem import WordNetLemmatizer
                        clean_w = WordNetLemmatizer().lemmatize(clean_w)
                    except Exception:
                        pass
                        
                    # Lookup weight
                    weight = word_weights.get(clean_w, 0.0)
                    
                    # Adjust sign based on label mapping
                    is_real_class_1 = clf.classes_[1] == "Real"
                    if not is_real_class_1:
                        weight = -weight
                        
                    # Threshold for highlighting
                    if weight > 0.4:  # Pushing towards Real
                        highlighted_spans.append(
                            f'<span style="background-color: rgba(16, 185, 129, 0.15); border: 1.5px solid #10B981; border-radius: 4px; padding: 1px 3px; color: #111827; font-weight: 700;">{w}</span>'
                        )
                    elif weight < -0.4: # Pushing towards Fake
                        highlighted_spans.append(
                            f'<span style="background-color: rgba(239, 68, 68, 0.15); border: 1.5px solid #EF4444; border-radius: 4px; padding: 1px 3px; color: #111827; font-weight: 700;">{w}</span>'
                        )
                    else:
                        highlighted_spans.append(w)
                else:
                    highlighted_spans.append(w)
                    
            html_content = "".join(highlighted_spans)
            st.markdown(
                f"""
                <div style="background: #F3F4F6; border: 2px solid #E5E7EB; 
                            border-radius: 8px; padding: 20px; font-family: 'Outfit', sans-serif; font-size: 17px; 
                            line-height: 1.8; color: #111827; max-height: 400px; overflow-y: auto;">
                    {html_content}
                </div>
                """,
                unsafe_allow_html=True
            )
            
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        logger.error(f"Prediction execution error: {str(e)}")

render_footer()
