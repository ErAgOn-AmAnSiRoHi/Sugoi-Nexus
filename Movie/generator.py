import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
import pickle
from tqdm import tqdm

class MovieEmbeddingsGenerator:
    def __init__(self, 
                 csv_path='movie_dataset.csv', 
                #  csv_path='small_movie_dataset.csv', 
                 model_name="sentence-transformers/all-MiniLM-L6-v2",
                 batch_size=32):
        # Load dataset
        self.df = pd.read_csv(csv_path)
        
        # Setup model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        
        # Use GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
        self.batch_size = batch_size
        print('Device: ',self.device)
        
    def prepare_text(self, row):
        """Combine relevant text features for embedding"""
        text_features = [
            str(row['title']),
            str(row['overview']),
            str(row['genres']),
            str(row['keywords'])
        ]
        return ' '.join(text_features)
    
    def generate_embeddings(self):
        """Generate embeddings in batches with progress tracking"""
        # Prepare text
        texts = self.df.apply(self.prepare_text, axis=1).tolist()
        titles = self.df['title'].tolist()
        
        # Initialize storage for embeddings
        all_embeddings = []
        
        # Process in batches with tqdm progress bar
        with tqdm(total=len(texts), desc="Generating embeddings", unit="text") as pbar:
            for i in range(0, len(texts), self.batch_size):
                batch_texts = texts[i:i+self.batch_size]
                
                # Tokenize batch
                inputs = self.tokenizer(
                    batch_texts, 
                    return_tensors="pt", 
                    padding=True, 
                    truncation=True, 
                    max_length=512
                ).to(self.device)
                
                # Generate embeddings
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    batch_embeddings = outputs.pooler_output.cpu().numpy()
                
                all_embeddings.append(batch_embeddings)
                
                # Update progress bar
                pbar.update(len(batch_texts))
        
        # Combine all embeddings
        embeddings = np.vstack(all_embeddings)
        
        return embeddings, titles
    
    def save_embeddings(self, embeddings, titles, filename='final_movie_embeddings.pkl'):
        """Save embeddings and titles to pickle file"""
        with open(filename, 'wb') as f:
            pickle.dump((embeddings, titles), f)
        print(f"Embeddings saved to {filename}")

def main():
    generator = MovieEmbeddingsGenerator()
    embeddings, titles = generator.generate_embeddings()
    generator.save_embeddings(embeddings, titles)

if __name__ == '__main__':
    main()
