import os
import sys
import unittest
import pandas as pd
import numpy as np

# Adjust path to import from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import services.db_service as db
import services.nlp_service as nlp

class TestTruthLensPipeline(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """
        Initializes the database schema for testing.
        """
        db.init_db()

    def test_01_database_operations(self):
        """
        Tests database initialization, dataset insertion, and cascading operations.
        """
        print("\n[TEST] Starting database operations validation...")
        
        # 1. Create a dummy dataframe
        data = {
            "title": ["Test article 1", "Test article 2"],
            "text": ["This is a real article body.", "This is a fake article conspiracy coverup."],
            "label": ["Real", "Fake"],
            "source": ["Test Source 1", "Test Source 2"]
        }
        df = pd.DataFrame(data)
        
        test_ds_name = "TruthLens_Test_Dataset"
        
        # Clean existing test datasets if any
        existing = db.get_datasets()
        if test_ds_name in existing["name"].values:
            ds_id = existing[existing["name"] == test_ds_name]["id"].values[0]
            db.delete_dataset(ds_id)
            
        # 2. Ingest dataset
        ds_id = db.add_dataset(
            name=test_ds_name,
            df=df,
            title_col="title",
            text_col="text",
            label_col="label",
            source_col="source"
        )
        
        self.assertIsNotNone(ds_id)
        print("[OK] Dataset registered in SQLite database.")
        
        # 3. Retrieve articles
        retrieved_df = db.get_articles(ds_id)
        self.assertEqual(len(retrieved_df), 2)
        print("[OK] Retrieved articles count matches ingested count.")
        
        # 4. Clean up test dataset
        db.delete_dataset(ds_id)
        post_del_df = db.get_datasets()
        self.assertNotIn(test_ds_name, post_del_df["name"].values)
        print("[OK] Dataset deletion and cascading check passed.")

    def test_02_nlp_processing(self):
        """
        Tests NLTK cleaning pipeline: lowercase, stopwords, punctuation, and lemmatization.
        """
        print("\n[TEST] Starting NLP preprocessor validation...")
        raw_text = "The quick brown foxes are running, and jumping over the fences!"
        
        # Standard cleaning
        cleaned = nlp.clean_text_engine(
            raw_text,
            use_stemming=False,
            use_lemmatization=True,
            remove_stopwords=True
        )
        
        # Assertions
        # Stopwords like 'the', 'are', 'and', 'over' should be removed
        # Lemmatizer: 'foxes' -> 'fox', 'running' -> 'running' (without POS tag), 'jumping' -> 'jumping'
        # Punctuation like ',' and '!' should be removed
        tokens = cleaned.split()
        self.assertNotIn("the", tokens)
        self.assertNotIn("are", tokens)
        self.assertNotIn("and", tokens)
        self.assertIn("fox", tokens)
        
        print(f"[OK] Cleaned text output: '{cleaned}'")
        print("[OK] Stopwords and punctuation filters verified.")

    def test_03_end_to_end_ml_pipeline(self):
        """
        Tests TF-IDF Vectorization, Classifier Training, serialization and predictions.
        """
        print("\n[TEST] Starting end-to-end Machine Learning validation...")
        
        # 1. Generate sample news dataframe
        df = db.generate_portfolio_sample_dataset()
        self.assertGreater(len(df), 50)
        
        # 2. Clean texts
        print("Cleaning text corpus...")
        df["cleaned_text"] = df["text"].apply(
            lambda t: nlp.clean_text_engine(t, use_stemming=False, use_lemmatization=True, remove_stopwords=True)
        )
        
        # 3. Train test split
        from sklearn.model_selection import train_test_split
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        
        X_train_text, X_test_text, y_train, y_test = train_test_split(
            df["cleaned_text"].tolist(), df["label"].tolist(), test_size=0.2, random_state=42, stratify=df["label"]
        )
        
        # 4. Vectorize
        vectorizer = TfidfVectorizer(max_features=200)
        X_train = vectorizer.fit_transform(X_train_text)
        X_test = vectorizer.transform(X_test_text)
        
        # 5. Fit model
        clf = LogisticRegression(C=1.0, random_state=42)
        clf.fit(X_train, y_train)
        
        # 6. Score
        train_acc = clf.score(X_train, y_train)
        test_acc = clf.score(X_test, y_test)
        
        self.assertGreater(test_acc, 0.8) # Generated dataset should easily score > 80% accuracy!
        print(f"[OK] Model accuracy: Train: {train_acc:.2%}, Test: {test_acc:.2%}")
        
        # 7. Check save/load
        import joblib
        import tempfile
        
        temp_dir = tempfile.gettempdir()
        temp_model = os.path.join(temp_dir, "test_truthlens_model.joblib")
        temp_vec = os.path.join(temp_dir, "test_truthlens_vectorizer.joblib")
        
        joblib.dump(clf, temp_model)
        joblib.dump(vectorizer, temp_vec)
        
        loaded_clf = joblib.load(temp_model)
        loaded_vec = joblib.load(temp_vec)
        
        # Verify prediction
        test_sample = "Astronomers discover habitable planet in nearby star system with liquid surface indicators."
        clean_sample = nlp.clean_text_engine(test_sample)
        vec_sample = loaded_vec.transform([clean_sample])
        pred = loaded_clf.predict(vec_sample)[0]
        
        self.assertEqual(pred, "Real")
        print(f"[OK] Serialization check passed. Predicts sample news correctly as '{pred}'.")
        
        # Clean up files
        if os.path.exists(temp_model):
            os.remove(temp_model)
        if os.path.exists(temp_vec):
            os.remove(temp_vec)

if __name__ == "__main__":
    unittest.main()
