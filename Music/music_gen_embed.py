from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import numpy as np
import pickle
import pandas as pd
import re

# Load the dataset
music_df = pd.read_csv('music.csv')  # Replace with the actual file path

# Preprocess lyrics text
def preprocess_text(text):
    # Basic text cleaning: lowercase, remove punctuation and extra spaces
    text = re.sub(r'[^\w\s]', '', text.lower())
    return text

# Apply preprocessing to the lyrics column
music_df['processed_lyrics'] = music_df['lyrics'].apply(preprocess_text)

# Vectorize lyrics using TF-IDF
tfidf = TfidfVectorizer(stop_words='english', max_features=5000)  # Limit features for manageable size
lyrics_embeddings = tfidf.fit_transform(music_df['processed_lyrics'])

# Reduce the dimensionality of the lyrics embeddings with SVD (optional)
svd = TruncatedSVD(n_components=200, random_state=42)
reduced_lyrics_embeddings = svd.fit_transform(lyrics_embeddings)

# Save embeddings and additional data
with open('music_embeddings.pkl', 'wb') as f:
    pickle.dump({
        "embeddings": reduced_lyrics_embeddings,
        "metadata": music_df[['artist_name', 'track_name', 'genre', 'release_date']].to_dict(orient='records')
    }, f)

print("Embedding generation and saving completed!")
