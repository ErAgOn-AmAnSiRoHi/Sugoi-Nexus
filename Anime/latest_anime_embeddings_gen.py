import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np
import json

# Load the dataset
df = pd.read_csv('anime-dataset-2023.csv')

# Load the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Define a function to create combined context for each anime
def create_combined_context(row):
    # Use 'English name' if available, otherwise 'Name'
    name = row['English name'] if pd.notnull(row['English name']) else row['Name']
    genres = row['Genres'] if pd.notnull(row['Genres']) else ''
    synopsis = row['Synopsis'] if pd.notnull(row['Synopsis']) else ''
    
    # Combine into one context string
    return f"{name}. Genres: {genres}. Overview: {synopsis}"

# Generate embeddings
anime_embeddings = {}
for _, row in df.iterrows():
    anime_id = row['anime_id']
    context = create_combined_context(row)
    embedding = model.encode(context)
    anime_embeddings[anime_id] = embedding.tolist()

# Save the embeddings to a file
with open('latest_anime_embeddings_combined.json', 'w') as f:
    json.dump(anime_embeddings, f)

print("Embeddings generated and saved successfully!")
