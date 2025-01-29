# database_init.py
import sqlite3

def initialize_database():
    conn = sqlite3.connect('datasets.db')
    cursor = conn.cursor()
    
    # Create a table for datasets
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS datasets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            path TEXT NOT NULL,
            description TEXT
        )
    ''')
    
    # Insert a sample dataset record
    cursor.execute('''
        INSERT INTO datasets (name, path, description)
        VALUES (?, ?, ?)
    ''', ('movie_dataset.csv', 'movie_dataset.csv', 'Dataset for movie embeddings'))
    
    conn.commit()
    conn.close()
    print("Database initialized with sample dataset.")

if __name__ == '__main__':
    initialize_database()
