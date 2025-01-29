import sqlite3
import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import difflib
import tmdbsimple as tmdb
from googleapiclient.discovery import build
import logging

class MovieRecommender:
    def __init__(self, 
                 db_path='datasets.db', 
                 embeddings_path='final_movie_embeddings.pkl',
                 model_name="sentence-transformers/all-MiniLM-L6-v2"):  # 1B Parameters size of embeddings is 384
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        try:
            # Fetch dataset path from the database
            self.dataset_path = self.get_dataset_path(db_path, 'movie_dataset.csv')
            
            # Load dataset
            self.df = pd.read_csv(self.dataset_path)
            
            # Ensure no NaN values
            self.df.fillna('', inplace=True)
            
            # Load pre-computed embeddings
            with open(embeddings_path, 'rb') as f:
                self.embeddings, self.titles = pickle.load(f)
            
            # Setup model and tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
            
            # Device setup
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            
            self.logger.info("MovieRecommender initialized successfully")
        
        except Exception as e:
            self.logger.error(f"Error initializing MovieRecommender: {e}")
            raise
    
    def get_dataset_path(self, db_path, dataset_name):
        """Fetch dataset path from the database"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT path FROM datasets WHERE name = ?', (dataset_name,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]
        else:
            raise ValueError(f"Dataset {dataset_name} not found in the database.")
    
    def find_closest_movie(self, input_title):
        """Find closest movie title using fuzzy matching"""
        matches = difflib.get_close_matches(input_title, self.df['title'], n=1, cutoff=0.6)
        return matches[0] if matches else None
    
    def get_movie_metadata(self, movie_title):
        """Extract comprehensive metadata for a movie"""
        movie_row = self.df[self.df['title'] == movie_title].iloc[0]
        
        # Combine all relevant metadata, replacing NaN with an empty string
        metadata = ' '.join([
            str(movie_row.get('title', '')),
            str(movie_row.get('overview', '')),
            str(movie_row.get('genres', '')),
            str(movie_row.get('keywords', '')),
            str(movie_row.get('production_companies', '')),
            str(movie_row.get('tagline', ''))
        ])
        return metadata
    
    def get_embedding(self, text):
        """Generate embedding for text"""
        inputs = self.tokenizer(
            text, 
            return_tensors="pt", 
            max_length=512, 
            truncation=True,
            padding=True
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            embedding = outputs.pooler_output.cpu().numpy()
        
        return embedding

    def recommend_movies(self, input_title, top_k=5):
        try:
            matched_title = self.find_closest_movie(input_title)
            if not matched_title:
                self.logger.warning(f"No similar movie found for input: {input_title}")
                return {"error": "No similar movie found"}
            
            movie_metadata = self.get_movie_metadata(matched_title)
            query_embedding = self.get_embedding(movie_metadata)
            similarities = cosine_similarity(query_embedding, self.embeddings)[0]
            
            top_indices = np.argsort(similarities)[::-1]
            filtered_indices = [
                idx for idx in top_indices if self.titles[idx] != matched_title
            ][:top_k]
            
            recommendations = [
                {"title": self.titles[idx], "similarity": float(similarities[idx])}
                for idx in filtered_indices
            ]
            
            return {
                "input_movie": matched_title,
                "recommendations": recommendations
            }
        except Exception as e:
            self.logger.error(f"Error in recommend_movies: {e}")
            return {"error": "An error occurred while generating recommendations"}

# TMDB API Key
# TMDB API configuration
tmdb.API_KEY = '46aaafa794c29bf2ed52a294aa3907de'

def get_movie_details(title):
    try:
        search = tmdb.Search()
        response = search.movie(query=title)
        
        if response['results']:
            movie = response['results'][0]

            # Fetch genre mappings from TMDB API
            genre_list = tmdb.Genres().movie_list()['genres']
            genre_mapping = {genre['id']: genre['name'] for genre in genre_list}

            # Convert genre IDs to genre names
            genre_ids = movie.get('genre_ids', [])
            genres = [genre_mapping.get(genre_id, 'Unknown') for genre_id in genre_ids]

            # Truncate synopsis if it's too long
            synopsis = movie.get('overview', '')[:500] + '...' if len(movie.get('overview', '')) > 500 else movie.get('overview', '')

            movie_details = {
                'title': movie.get('title', ''),
                'synopsis': synopsis,
                'genres': ', '.join(genres),
                'poster_url': f"https://image.tmdb.org/t/p/w500{movie.get('poster_path', '')}" if movie.get('poster_path') else '',
            }
            return movie_details
        return None
    except Exception as e:
        logging.error(f"Error fetching movie details for {title}: {e}")
        return None

# YouTube API configuration
YOUTUBE_API_KEY = 'AIzaSyBm19rJFnA6jrxv8IBkQLwBZubDkUKOebM'

def get_trailer_url(title):
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        request = youtube.search().list(
            part='snippet',
            q=f"{title} official trailer",
            maxResults=1,
            type='video'
        )
        response = request.execute()
        if response['items']:
            video_id = response['items'][0]['id']['videoId']
            return f"https://www.youtube.com/watch?v={video_id}"
        return None
    except Exception as e:
        logging.error(f"Error fetching trailer for {title}: {e}")
        return None

# Flask App
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

recommender = MovieRecommender()

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        data = request.json
        input_title = data.get('query', '').strip()
        
        if not input_title:
            return jsonify({'error': 'Invalid title provided'}), 400
        
        category = data.get('category', '')
        
        if category != 'movie':
            return jsonify({"error": "Invalid category"}), 400
        
        recommendations = recommender.recommend_movies(input_title)
        
        # Log the recommendation process
        app.logger.info(f"Recommendation request for: {input_title}")
        
        return jsonify(recommendations)
    
    except Exception as e:
        app.logger.error(f"Error in recommendation route: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500
    
@app.route('/movie_details', methods=['POST'])
def movie_details():
    data = request.json
    title = data.get('title', '').strip()

    if not title:
        return jsonify({"error": "No movie title provided"}), 400

    try:
        # Fetch movie metadata from TMDB
        movie_metadata = get_movie_details(title)

        if not movie_metadata:
            app.logger.warning(f"Movie details not found for: {title}")
            return jsonify({"error": "Movie details not found"}), 404

        # Fetch YouTube trailer URL
        trailer_url = get_trailer_url(title)
        
        # Log successful movie details retrieval
        app.logger.info(f"Successfully retrieved details for: {title}")
        
        return jsonify({
            "title": movie_metadata['title'],
            "synopsis": movie_metadata['synopsis'],
            "genres": movie_metadata['genres'],
            "poster_url": movie_metadata['poster_url'],
            "trailer_url": trailer_url,
        })
    except Exception as e:
        app.logger.error(f"Error fetching movie details for {title}: {e}")
        return jsonify({"error": "An error occurred while fetching movie details"}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
