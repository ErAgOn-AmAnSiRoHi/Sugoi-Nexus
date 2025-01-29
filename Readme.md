# 🎬 Movie Recommendation System

## 🚀 Getting Started

To run the project locally, follow these steps:

### 1️⃣ Start an HTTP Server
Run an HTTP server in the parent directory using Python:
```bash
python -m http.server 8000
```

### 2️⃣ Access the Website
Once the server is running, visit:
🔗 [http://localhost:8000/](http://localhost:8000/)

### 3️⃣ Navigate to the Index Page
You will land on the index page. Click on **ENTER** to explore the world of recommendations.

### 4️⃣ Experience the Homepage
- The homepage contains an interactive **image gallery** featuring movie posters.
- The posters move with a **parallax effect** as you hover over them.

📝 **NOTE:** Posters are fetched via the **TMDB API**, which may not work in India due to government restrictions. It is recommended to use a **VPN** to bypass this issue.

### 5️⃣ Generate Embeddings
The embedding files were removed due to limited storage space. You need to generate embeddings manually using the provided **embedding generator scripts** for each category.

### 6️⃣ Explore Recommendations
Click on the **Explore {Category}** button for your desired category. Then, manually run the corresponding recommender script in the terminal:
```bash
python3 {category-specific}recommender.py
```

💡 **Why isn't this automated?**
Due to **flask-cors** issues, we couldn't automate the execution of recommender scripts in the final version.

📝 **NOTE:**  Install Dependencies (If Needed)
Before running the script, ensure you have **Flask** and **Flask-CORS** installed. If not, install them using:
```bash
pip install flask flask-cors
```

### 7️⃣ Search for Recommendations
Once the Flask server is running:
1. Enter the **Title** of the {Category} media.
2. Click **Search**.

### 8️⃣ View Recommendations
Recommendations appear on the **secondary display** of the **3D mini PC setup** rendered in the canvas. Each recommendation is **clickable** and provides:
✅ A movie poster 🎭  
✅ Genres 🎞️  
✅ Synopsis 📜  
✅ A direct link to the **YouTube Trailer** 🎥 *(clickable)*  

---

🎯 Enjoy discovering new recommendations! 🍿✨

