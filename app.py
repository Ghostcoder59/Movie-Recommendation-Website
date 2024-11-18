import pickle
import random
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

# Function to fetch poster
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=1c98fa6b3edcd11ac5f26bf4eefed1bb&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path', '')
    if poster_path:
        return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    return "https://via.placeholder.com/150"

# Function to fetch movie trailer
def fetch_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=1c98fa6b3edcd11ac5f26bf4eefed1bb&language=en-US&append_to_response=videos"
    response = requests.get(url).json()
    videos = response.get("videos", {}).get("results", [])
    for video in videos:
        if video.get("type") == "Trailer" and video.get("site") == "YouTube":
            video_key = video.get("key")
            if video_key:
                return f"https://www.youtube.com/embed/{video_key}"
    return None

# Function to recommend movies
# Function to recommend movies (Change the range to 10 for more recommendations)
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_movie_trailers = []

    for i in distances[1:11]:  # Top 10 recommendations (adjusted from 5)
        movie_data = movies.iloc[i[0]]
        movie_id = movie_data['movie_id']
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movie_data['title'])
        recommended_movie_trailers.append(fetch_trailer(movie_id))

    return recommended_movie_names, recommended_movie_posters, recommended_movie_trailers


# Load data
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

@app.route("/", methods=["GET", "POST"])
def index():
    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_movie_trailers = []

    if request.method == "POST":
        selected_movie = request.form.get("movie")
        if selected_movie:
            recommended_movie_names, recommended_movie_posters, recommended_movie_trailers = recommend(selected_movie)
    
    # Zip the movie names, posters, and trailers together
    recommended_movies = zip(recommended_movie_names, recommended_movie_posters, recommended_movie_trailers)

    return render_template("index.html", 
                           movies=movies['title'], 
                           recommended_movies=recommended_movies)

if __name__ == "__main__":
    app.run(debug=True)
