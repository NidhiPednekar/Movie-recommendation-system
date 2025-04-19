import pickle
import streamlit as st
import requests
import pandas as pd

# Set page configuration
st.set_page_config(
    page_title="Movie Recommender System",
    layout="wide"
)

# Custom CSS with darker text that will be visible on any background
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
    /* Main styling */
    body {
        color: #333;
        background-color: #f5f5f5;
    }
    .movie-container {
        padding: 20px;
        background-color: #fff;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .movie-poster {
        width: 100%;
        height: auto;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .movie-title {
        font-weight: bold;
        font-size: 1.2rem;
        margin-top: 10px;
        color: #1a1a1a;
    }
    .movie-info {
        background-color: #2c3e50;
        color: #ffffff;
        padding: 6px 12px;
        border-radius: 4px;
        display: inline-block;
        margin-right: 5px;
        margin-bottom: 5px;
        font-weight: 500;
    }
    .movie-detail-label {
        font-weight: bold;
        color: #2c3e50;
    }
    .genre-badge {
        background-color: #3498db;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        margin-right: 5px;
        display: inline-block;
    }
    .overview-section {
        margin-top: 15px;
        color: #333;
    }
    .overview-title {
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 5px;
    }
    .overview-content {
        line-height: 1.5;
    }
    .rec-movie-card {
        background-color: #fff;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    .rec-movie-title {
        font-weight: bold;
        font-size: 1rem;
        color: #1a1a1a;
        margin: 10px 0;
        height: 2.4rem;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

def fetch_movie_details(movie_id):
    """Fetch detailed information about a movie"""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    response = requests.get(url)
    data = response.json()
    
    # Get credits to find cast and crew
    credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    credits_response = requests.get(credits_url)
    credits_data = credits_response.json()
    
    # Extract director
    directors = [crew['name'] for crew in credits_data.get('crew', []) if crew['job'] == 'Director']
    director = directors[0] if directors else "Unknown"
    
    # Extract top cast
    cast = [actor['name'] for actor in credits_data.get('cast', [])[:5]]
    
    details = {
        'title': data.get('title'),
        'poster_path': f"https://image.tmdb.org/t/p/w500{data.get('poster_path')}" if data.get('poster_path') else None,
        'release_date': data.get('release_date', '').split('-')[0] if data.get('release_date') else "Unknown",
        'rating': round(data.get('vote_average', 0), 1),
        'runtime': data.get('runtime'),
        'genres': [genre['name'] for genre in data.get('genres', [])],
        'overview': data.get('overview'),
        'director': director,
        'cast': cast
    }
    
    return details

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path')
    if poster_path:
        full_path = f"https://image.tmdb.org/t/p/w500{poster_path}"
        return full_path
    return "https://via.placeholder.com/500x750?text=No+Image+Available"

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_movie_ids = []
    
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].id
        recommended_movie_ids.append(movie_id)
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
    
    return recommended_movie_names, recommended_movie_posters, recommended_movie_ids

# App header
st.title('Movie Recommender System')

# Load movie data
movies = pickle.load(open('model/movie_list.pkl', 'rb'))
similarity = pickle.load(open('model/similarity.pkl', 'rb'))

# Create movie selection dropdown
movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

# Get selected movie details
selected_movie_id = movies[movies['title'] == selected_movie].id.values[0]
selected_movie_details = fetch_movie_details(selected_movie_id)

# Display selected movie details
st.header('Selected Movie')

# Create a container for better styling
with st.container():
    cols = st.columns([1, 2])
    
    with cols[0]:
        st.image(selected_movie_details['poster_path'] or 'https://via.placeholder.com/250x375?text=No+Image')
    
    with cols[1]:
        st.subheader(f"{selected_movie_details['title']} ({selected_movie_details['release_date']})")
        
        # Movie info with styled badges
        st.markdown(f"""
        <div>
            <div class="movie-info">Rating: {selected_movie_details['rating']}/10 ⭐</div>
            <div class="movie-info">Runtime: {selected_movie_details['runtime']} minutes</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"<p><span class='movie-detail-label'>Director:</span> {selected_movie_details['director']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p><span class='movie-detail-label'>Cast:</span> {', '.join(selected_movie_details['cast'])}</p>", unsafe_allow_html=True)
        
        # Genres as badges
        genres_html = ""
        for genre in selected_movie_details['genres']:
            genres_html += f'<div class="genre-badge">{genre}</div>'
        
        st.markdown(f"<div><span class='movie-detail-label'>Genres:</span> {genres_html}</div>", unsafe_allow_html=True)
        
        # Overview section
        st.markdown("""
        <div class="overview-section">
            <div class="overview-title">Overview</div>
            <div class="overview-content">
        """, unsafe_allow_html=True)
        
        st.markdown(f"{selected_movie_details['overview']}", unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)

# Get and display recommendations when button is clicked
if st.button('Show Recommendations'):
    with st.spinner('Getting recommendations...'):
        recommended_movie_names, recommended_movie_posters, recommended_movie_ids = recommend(selected_movie)
        
        st.header('Recommended Movies')
        
        # Create columns for recommendations
        cols = st.columns(5)
        
        for i, col in enumerate(cols):
            with col:
                # Get details for the recommended movie
                rec_details = fetch_movie_details(recommended_movie_ids[i])
                
                # Display movie card with styling
                st.markdown(f"""
                <div class="rec-movie-card">
                    <img src="{recommended_movie_posters[i]}" style="width:100%; border-radius:8px;">
                    <div class="rec-movie-title">{recommended_movie_names[i]}</div>
                    <div>
                        <span class="movie-detail-label">Rating:</span> {rec_details['rating']}/10 ⭐<br>
                        <span class="movie-detail-label">Year:</span> {rec_details['release_date']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Use expander for additional details
                with st.expander("View Details"):
                    st.markdown(f"<p><strong>Runtime:</strong> {rec_details['runtime']} minutes</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Director:</strong> {rec_details['director']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Cast:</strong> {', '.join(rec_details['cast'])}</p>", unsafe_allow_html=True)
                    st.markdown("<p><strong>Overview</strong></p>", unsafe_allow_html=True)
                    st.markdown(f"<p>{rec_details['overview']}</p>", unsafe_allow_html=True)