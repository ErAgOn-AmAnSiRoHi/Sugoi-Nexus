1. Run a http server in the parent directory using python:
	> python -m http.server 8000
	
2. Now, you can access the website on the localhost address:
	> http://localhost:8000/
	
3. You will land on the index page. Click on **ENTER** to explore the world of recommendations.

4. Now, you will be redirected to the homepage of the website. There you will be able to see an image gallery containing movie posters. You may interact with it by moving the mouse pointer over it, as it has a parallax effect in place which moves the poster tiles accordingly.
	**NOTE:** The posters are fetched using TMDB API which most probably won't work in India (due to some government policy restrictions). So you are advised to use a VPN.
	
**NOTE:** Generate embeddings (as there was limited space available, we have removed embedding files from the zip folder) using the embedding generator scripts for each category individually.

5. Click on "Explore {Category}" button for the respective category you want to explore. Now, in the background, run the respective recommender script (the reason why this process wasn't automated in the final draft of the project is that there were issues with the flask-cors and endpoints, and so we had to drop the plan of automating the execution of respective recommender scripts in a terminal using python:
	> python3 {category-specific}recommender.py
	
	But before running the script make sure you have flask and flask-cors installed. If not, install it using pip:
		> pip install flask flask-cors

6. Once the flask server is booted up, you may enter the Title of the {Category} media you want to generate recommendations for and click "Search".

7. The recommendations will be shown on the secondary display (of the 3d mini pc setup rendered in the canvas). You may click an individual recommendation */clickable* to get more detailed information about that title including a movie poster, genres, a synopsis as well as a direct link for the YouTube Trailer of that title */clickable*.
