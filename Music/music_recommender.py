import pickle
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, request, jsonify
from flask_cors import CORS

# Load the saved embeddings and metadata
with open('music_embeddings.pkl', 'rb') as f:
    data = pickle.load(f)
    embeddings = data['embeddings']
    metadata = data['metadata']

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Function to recommend songs based on cosine similarity
def recommend_songs(song_name, top_n=5):
    # Find index of the requested song
    song_index = next((i for i, song in enumerate(metadata) if song['track_name'].lower() == song_name.lower()), None)
    
    if song_index is None:
        return []

    # Calculate cosine similarity
    song_vector = embeddings[song_index].reshape(1, -1)
    similarities = cosine_similarity(song_vector, embeddings).flatten()
    
    # Get indices of the most similar songs (excluding the song itself)
    similar_indices = similarities.argsort()[-top_n-1:-1][::-1]
    
    # Retrieve recommended songs
    recommendations = [
        {
            'track_name': metadata[i]['track_name'],
            'artist_name': metadata[i]['artist_name'],
            'genre': metadata[i]['genre'],
            'release_date': metadata[i]['release_date']
        }
        for i in similar_indices
    ]
    return recommendations

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        # Get the song name from the request
        data = request.get_json()
        song_name = data.get('query', '')

        if not song_name:
            return jsonify({'error': 'No song name provided'}), 400

        # Get recommendations
        recommendations = recommend_songs(song_name)

        if not recommendations:
            return jsonify({'error': 'Song not found in the dataset'}), 404

        # Return the recommendations as JSON
        return jsonify(recommendations)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
