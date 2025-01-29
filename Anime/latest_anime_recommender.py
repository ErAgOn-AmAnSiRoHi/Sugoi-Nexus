from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer, util
import pandas as pd
import numpy as np
import torch
import json
from flask_cors import CORS


# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load data and embeddings
df = pd.read_csv('anime-dataset-2023.csv')
with open('latest_anime_embeddings_combined.json', 'r') as f:
    anime_embeddings = json.load(f)

# Load the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Ensure all embeddings are converted to torch.float32
anime_embeddings = {int(k): torch.tensor(v, dtype=torch.float32) for k, v in anime_embeddings.items()}

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    query = data.get('query')
    
    # Generate embedding for the input query using combined context
    query_embedding = model.encode(query)
    query_embedding = torch.tensor(query_embedding, dtype=torch.float32)  # Convert to torch.float32
    
    # Calculate cosine similarity between query and all anime embeddings
    similarities = []
    for anime_id, embedding in anime_embeddings.items():
        similarity = util.cos_sim(query_embedding, embedding).item()
        similarities.append((anime_id, similarity))
    
    # Sort anime based on similarity score
    similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
    
    # Fetch top recommendations
    top_anime_ids = [anime_id for anime_id, _ in similarities[:10]]
    recommended_anime = df[df['anime_id'].isin(top_anime_ids)][['Name']].to_dict(orient='records')
    
    # Return the names of recommended anime
    return jsonify(recommended_anime)

if __name__ == '__main__':
    app.run(debug=True)

