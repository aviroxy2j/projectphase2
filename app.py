import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Load CSV files from the directory
ratings_file = 'ratings.csv'
movies_file = 'movies.csv'

# Load datasets
ratings = pd.read_csv(ratings_file)
movies = pd.read_csv(movies_file)

# Convert timestamp to datetime
ratings['timestamp'] = pd.to_datetime(ratings['timestamp'], unit='s')

# Streamlit App Title
st.title("Interactive MovieLens Dataset Explorer")

# Sidebar Filters
st.sidebar.header("Filters")

# Convert min_date and max_date to datetime.date
min_date = ratings['timestamp'].min().date()
max_date = ratings['timestamp'].max().date()

# Sidebar Date Range Slider
date_range = st.sidebar.slider(
    "Select Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date)
)

# Filter by Rating Range
min_rating = float(ratings['rating'].min())
max_rating = float(ratings['rating'].max())
rating_range = st.sidebar.slider("Select Rating Range", min_rating, max_rating, (min_rating, max_rating))

# Filter by Genre
movies['genres'] = movies['genres'].fillna('(no genres listed)').str.split('|')
unique_genres = set(movies['genres'].explode())
selected_genre = st.sidebar.multiselect("Select Genre(s)", unique_genres, default=list(unique_genres))

# Apply Filters
filtered_ratings = ratings[
    (ratings['timestamp'].dt.date >= date_range[0]) & 
    (ratings['timestamp'].dt.date <= date_range[1]) & 
    (ratings['rating'] >= rating_range[0]) & 
    (ratings['rating'] <= rating_range[1])
]
filtered_movies = movies[movies['genres'].apply(lambda x: any(genre in x for genre in selected_genre))]

# Merge filtered data
filtered_data = pd.merge(filtered_ratings, filtered_movies, on='movieId')

# Dataset Overview
st.header("Filtered Dataset Overview")
st.write(f"Total Ratings: {len(filtered_data)}")
st.write(f"Total Users: {filtered_data['userId'].nunique()}")
st.write(f"Total Movies: {filtered_data['movieId'].nunique()}")

# Visualization Options
st.header("Interactive Visualizations")
viz_option = st.selectbox("Choose a Visualization", [
    "Ratings Distribution",
    "Popularity of Genres",
    "Ratings Over Time",
    "Ratings per User",
    "Ratings per Movie"
])

# Ratings Distribution (Interactive)
if viz_option == "Ratings Distribution":
    fig = px.histogram(
        filtered_data,
        x="rating",
        nbins=10,
        title="Distribution of Ratings",
        labels={"rating": "Rating", "count": "Frequency"},
        color_discrete_sequence=["#4CAF50"]
    )
    fig.update_layout(
        title_font_size=18,
        xaxis_title="Rating (1 to 5 stars)",
        yaxis_title="Frequency",
        bargap=0.2
    )
    st.plotly_chart(fig)

# Popularity of Genres
elif viz_option == "Popularity of Genres":
    genre_counts = filtered_movies['genres'].explode().value_counts()
    fig = px.bar(
        genre_counts,
        x=genre_counts.values,
        y=genre_counts.index,
        orientation='h',
        title="Most Popular Genres",
        labels={"x": "Number of Movies", "y": "Genres"},
        color_discrete_sequence=["#337AB7"]
    )
    st.plotly_chart(fig)

# Ratings Over Time
elif viz_option == "Ratings Over Time":
    ratings_by_month = filtered_data.groupby(filtered_data['timestamp'].dt.to_period('M'))['rating'].count().reset_index()
    ratings_by_month.columns = ['Month', 'Count']
    fig = px.line(
        ratings_by_month,
        x='Month',
        y='Count',
        title="Ratings Over Time",
        labels={"Month": "Time (Monthly)", "Count": "Number of Ratings"},
        line_shape='linear'
    )
    fig.update_layout(
        title_font_size=18,
        xaxis_title="Time (Monthly)",
        yaxis_title="Number of Ratings",
        hovermode="x unified"
    )
    st.plotly_chart(fig)

# Ratings per User
elif viz_option == "Ratings per User":
    user_activity = filtered_data['userId'].value_counts()
    fig = px.histogram(
        user_activity,
        x=user_activity.values,
        nbins=50,
        title="Ratings per User",
        labels={"x": "Number of Ratings", "y": "Frequency of Users"},
        color_discrete_sequence=["#FFA07A"]
    )
    st.plotly_chart(fig)

# Ratings per Movie
elif viz_option == "Ratings per Movie":
    movie_activity = filtered_data['movieId'].value_counts()
    fig = px.histogram(
        movie_activity,
        x=movie_activity.values,
        nbins=50,
        title="Ratings per Movie",
        labels={"x": "Number of Ratings", "y": "Frequency of Movies"},
        color_discrete_sequence=["#6A5ACD"]
    )
    st.plotly_chart(fig)
