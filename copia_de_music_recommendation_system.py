# -*- coding: utf-8 -*-
"""Copia de music-recommendation-system.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/13EaRqQKeiU5siiDf21PoIANjvTBupt1g

# **Sistemas de Recomendación**

Sistema de Recomendación Musical utilizando un Conjunto de Datos de canciones de Spotify.

# **Importar Librerias**
"""

# Commented out IPython magic to ensure Python compatibility.
import os
import numpy as np
import pandas as pd

import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt
# %matplotlib inline

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.metrics import euclidean_distances
from scipy.spatial.distance import cdist

import warnings
warnings.filterwarnings("ignore")

"""# **Importar Datos**"""

data = pd.read_csv("data.csv")
genre = pd.read_csv('data_by_genres.csv')
year = pd.read_csv('data_by_year.csv')

print(data.info())

data

print(genre.info())

genre

print(year.info())

year

"""# **Análisis Exploratorio de Datos (EDA)**"""

data['year'] = pd.to_datetime(data['year'], format='%Y')
data['release_date'] = pd.to_datetime(data['release_date'])
year['year'] = pd.to_datetime(year['year'], format='%Y')

# combine for usability
datasets = [("data", data), ("genre", genre), ("year", year)]

for name, df in datasets:
    print(f"Missing Values in: {name}")
    print("-"*30)
    print(df.isnull().sum())
    print()

# no hay valores nulos en ninguno de los datasets

for name, df in datasets:
    print(f"Duplicates in the dataset: {name}")
    print("-"*30)
    print(df.duplicated(keep=False).sum())
    print()

# no hay valores duplicados en ninguno de los datasets

for name, df in datasets:
    # valores unicos
    print(f"Unique Values in: {name}")
    print("-"*30)
    print(df.nunique())
    print()

import matplotlib.pyplot as plt

# Selecciona solo las columnas numéricas del DataFrame (excluyendo 'mode')
numeric_data = data.select_dtypes(include=['number']).drop(columns=['mode', 'explicit'])

num_cols = 4
num_rows = (len(numeric_data.columns) + num_cols - 1) // num_cols

fig, axes = plt.subplots(num_rows, num_cols, figsize=(14, 2*num_rows))
axes = axes.flatten()

for i, column in enumerate(numeric_data.columns):
    sns.boxplot(x=numeric_data[column], ax=axes[i])
    axes[i].set_title(f'Boxplot de {column}')

plt.tight_layout()
plt.show()

"""Todas las caracteristicas de una canción se mantienen en el rango de 0 a 1, por lo que no se considerará los valores por fuera de los 'bigotes' de la caja como **outliers**"""

data[data['duration_ms']>4000000]
# no se los considera outliers, la duracion tiene sentido

"""**Correlacion con la variable 'popularity'**"""

import seaborn as sns
import matplotlib.pyplot as plt

# Selecciona las características y la variable objetivo
feature_names = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence','duration_ms','explicit','key','mode']
selected_columns = feature_names + ['popularity']
subset_data = data[selected_columns]

# Calcula la matriz de correlación
correlation_matrix = subset_data.corr()

# Crea un mapa de calor utilizando seaborn
plt.figure(figsize=(14, 7))
sns.heatmap(correlation_matrix, annot=True, cmap='YlGnBu', fmt=".2f", annot_kws = {'size': 9})
plt.title('Matriz de Correlación')
plt.show()

from yellowbrick.target import FeatureCorrelation

feature_names = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence','duration_ms','explicit','key','mode']
X, y = data[feature_names], data['popularity']

features = np.array(feature_names)
visualizer = FeatureCorrelation(labels=features)

plt.rcParams['figure.figsize']=(8, 8)
visualizer.fit(X, y)
visualizer.show()

"""# **Música a lo largo del Tiempo**

Utilizando los datos agrupados por año, podemos comprender cómo ha cambiado el sonido general de la música desde 1921 hasta 2020.
"""

data['decade'] = (data['release_date'].dt.year // 10) * 10
data = data.drop('release_date', axis=1)

decade_counts = data['decade'].value_counts().sort_index()

# Create a bar chart for songs per decade
fig = px.bar(x=decade_counts.index, y=decade_counts.values, labels={'x': 'Decada', 'y': 'Cantidad Canciones'},  title='Cantidad de canciones por Decada')
fig.update_layout(xaxis_type='category')
fig.show()

fig = px.line(year, x='year', y='popularity', title='Popularity a través de los Años')
fig.show()

fig = px.line(year, x='year', y='danceability', title='Danceability a través de los Años')
fig.show()

import plotly.graph_objects as go

fig = go.Figure()

fig.add_trace(go.Scatter(x=year['year'], y=year['danceability'], mode='lines', name='Danceability'))
fig.add_trace(go.Scatter(x=year['year'], y=year['energy'], mode='lines', name='Energy'))

fig.update_layout(title='Danceability y Energy a través de los Años', xaxis_title='Año', yaxis_title='Valor')
fig.show()

fig = go.Figure()

fig.add_trace(go.Scatter(x=year['year'], y=year['energy'], mode='lines', name='Energy'))
fig.add_trace(go.Scatter(x=year['year'], y=year['acousticness'], mode='lines', name='Acousticness'))

fig.update_layout(title='Energy y Acousticness a través de los Años', xaxis_title='Año', yaxis_title='Valor')
fig.show()

sound_features = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'valence']
fig = px.line(year, x='year', y=sound_features)
fig.show()

"""# **Características de Diferentes Géneros**

Este conjunto de datos contiene las características de audio de diferentes canciones, junto con las características de audio de diferentes géneros. Podemos utilizar esta información para comparar diferentes géneros y comprender sus diferencias únicas en el sonido.
"""

top10_genres = genre.nlargest(10, 'popularity')
fig = px.bar(top10_genres, x='genres', y=['valence', 'energy', 'danceability', 'acousticness'], barmode='group')
fig.show()

import plotly.express as px

top10 = genre.nlargest(10, 'popularity')

combined_df = pd.concat([
    top10.melt(id_vars=['genres'], value_vars=['danceability'], var_name='feature', value_name='value'),
    top10.melt(id_vars=['genres'], value_vars=['energy'], var_name='feature', value_name='value'),
    top10.melt(id_vars=['genres'], value_vars=['acousticness'], var_name='feature', value_name='value'),
    top10.melt(id_vars=['genres'], value_vars=['instrumentalness'], var_name='feature', value_name='value')
])

# Crea los subgráficos
fig = px.bar(combined_df, x='genres', y='value', color='genres', facet_col='feature', facet_col_wrap=1,
             labels={'value': 'Valor', 'genres': 'Género'},
             title='Análisis de los 10 Géneros Más Populares')

fig.update_layout(height=1000, width=1000)
fig.show()

"""# **Características de las Canciones**

"""

top_songs = data.nlargest(10, 'popularity')

fig = px.bar(top_songs, x='popularity', y='name', orientation='h',  title='Top Songs by Popularity')
fig.show()

from wordcloud import WordCloud

song_popularity = data[['name', 'popularity']].set_index('name').to_dict()['popularity']
song_popularity = sorted(song_popularity.items(), key=lambda x: x[1], reverse=True)

wordcloud = WordCloud(width=1600, height=800, max_words=50, background_color='white').generate_from_frequencies(dict(song_popularity))
plt.figure(figsize=(10, 8))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()

"""# **Clusters con K-Media (Genres y Songs)**

Usamos el algoritmo de K-Means para dividir los géneros de este conjunto de datos en diez clústeres basados en las características, o variables, numéricas de audio de cada género.
"""

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

cluster_pipeline = Pipeline([('scaler', StandardScaler()), ('kmeans', KMeans(n_clusters=5))])
X = genre.select_dtypes(np.number)
cluster_pipeline.fit(X)
genre['cluster'] = cluster_pipeline.predict(X)

# Visualizing the Clusters with t-SNE

from sklearn.manifold import TSNE

tsne_pipeline = Pipeline([('scaler', StandardScaler()), ('tsne', TSNE(n_components=2, verbose=1))])
genre_embedding = tsne_pipeline.fit_transform(X)
projection = pd.DataFrame(columns=['x', 'y'], data=genre_embedding)
projection['genres'] = genre['genres']
projection['cluster'] = genre['cluster']

fig = px.scatter(projection, x='x', y='y', color='cluster', hover_data=['x', 'y', 'genres'])
fig.update_layout(width=1000, height=600)
fig.show()

song_cluster_pipeline = Pipeline([('scaler', StandardScaler()),
                                  ('kmeans', KMeans(n_clusters=20,
                                   verbose=False))
                                 ], verbose=False)

X = data.select_dtypes(np.number)
X = X.fillna(X.median())

number_cols = list(X.columns)
song_cluster_pipeline.fit(X)
song_cluster_labels = song_cluster_pipeline.predict(X)
data['cluster_label'] = song_cluster_labels

# Visualizing the Clusters with PCA
from sklearn.decomposition import PCA

pca_pipeline = Pipeline([('scaler', StandardScaler()), ('PCA', PCA(n_components=2))])
song_embedding = pca_pipeline.fit_transform(X)
projection = pd.DataFrame(columns=['x', 'y'], data=song_embedding)
projection['title'] = data['name']
projection['cluster'] = data['cluster_label']

fig = px.scatter(projection, x='x', y='y', color='cluster', hover_data=['x', 'y', 'title'])
fig.update_layout(width=1000, height=600)

fig.show()

wcss=[]
for i in range(1,18):
    kmeans = KMeans(i)
    kmeans.fit(X)
    wcss_iter = kmeans.inertia_
    wcss.append(wcss_iter)

number_clusters = range(1,18)
plt.plot(number_clusters,wcss)
plt.title('The Elbow title')
plt.xlabel('Number of clusters')
plt.ylabel('WCSS')

"""# **Sistemas de Recomendación**

* Basándonos en el análisis y las visualizaciones, es evidente que los géneros similares tienden a tener puntos de datos que están ubicados cerca entre sí, mientras que los tipos de canciones similares también se agrupan juntos.
* Esta observación tiene perfecto sentido. Los géneros similares sonarán de manera parecida y provendrán de períodos de tiempo similares, al igual que se puede decir lo mismo para las canciones dentro de esos géneros.

* Podemos utilizar esta idea para construir un sistema de recomendación tomando los puntos de datos de las canciones que un usuario ha escuchado y recomendando canciones correspondientes a puntos de datos cercanos.

"""

# List of numerical columns to consider for similarity calculations
data['year'] = data['year'].dt.year

number_cols = ['valence', 'year', 'acousticness', 'danceability', 'duration_ms', 'energy', 'explicit',
               'instrumentalness', 'liveness', 'loudness', 'popularity', 'speechiness', 'tempo']

"""## Spoti"""
"""## Spotipy
* [Spotipy](https://spotipy.readthedocs.io/en/2.16.1/) es un cliente de Python para la API web de Spotify que facilita a los desarrolladores obtener datos y consultar el catálogo de canciones de Spotify. Lo instalamos usando `pip install spotipy`.
* Después de instalar Spotipy, creamos una aplicación en la [página de desarrolladores de Spotify](https://developer.spotify.com/) y guardamos el ID de cliente y clave secreta.
"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from collections import defaultdict

client_id = '4035349ceac545928cdda92296170ad5'
client_secret = '5696d44288b4451189a57125e06a98af'

auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

from collections import defaultdict
from sklearn.metrics import euclidean_distances
from scipy.spatial.distance import cdist
import difflib


# Function to retrieve song data for a given song name
def get_song_data(name, data):
    try:
        return data[data['name'].str.lower() == name].iloc[0]
    except IndexError:
        return None

# Function to calculate the mean vector of a list of songs
def get_mean_vector(song_list, data):
    song_vectors = []
    for song in song_list:
        song_data = get_song_data(song['name'], data)
        if song_data is None:
            print(f"Warning: {song['name']} does not exist in the dataset")
            return None
        song_vector = song_data[number_cols].values
        song_vectors.append(song_vector)
    song_matrix = np.array(list(song_vectors))
    return np.mean(song_matrix, axis=0)

# Function to recommend songs based on a list of seed songs
def recommend_songs(seed_songs, data, n_recommendations=10):
    metadata_cols = ['name', 'artists', 'year']
    song_center = get_mean_vector(seed_songs, data)

    # Return an empty list if song_center is missing
    if song_center is None:
        return []

    # Normalize the song center
    normalized_song_center = min_max_scaler.transform([song_center])

    # Standardize the normalized song center
    scaled_normalized_song_center = standard_scaler.transform(normalized_song_center)

    # Calculate Euclidean distances and get recommendations
    distances = cdist(scaled_normalized_song_center, scaled_normalized_data, 'euclidean')
    index = np.argsort(distances)[0]

    # Filter out seed songs and duplicates, then get the top n_recommendations
    rec_songs = []
    for i in index:
        song_name = data.iloc[i]['name']
        if song_name not in [song['name'] for song in seed_songs] and song_name not in [song['name'] for song in rec_songs]:
            rec_songs.append(data.iloc[i])
            if len(rec_songs) == n_recommendations:
                break

    return pd.DataFrame(rec_songs)[metadata_cols].to_dict(orient='records')

from sklearn.preprocessing import MinMaxScaler, StandardScaler

# Normalize the song data using Min-Max Scaler
min_max_scaler = MinMaxScaler()
normalized_data = min_max_scaler.fit_transform(data[number_cols])

# Standardize the normalized data using Standard Scaler
standard_scaler = StandardScaler()
scaled_normalized_data = standard_scaler.fit_transform(normalized_data)

# List of seed songs (replace with your own seed songs)
seed_songs = [
    {'name': 'Dynamite'},
    {'name': 'Blinding Lights'},
    {'name': 'positions'},
    {'name': 'Holy (feat. Chance The Rapper)'},
]

seed_songs = [{'name': name['name'].lower()} for name in seed_songs]

# Number of recommended songs
n_recommendations = 5

# Call the recommend_songs function
recommended_songs = recommend_songs(seed_songs, data, n_recommendations)

# Convert the recommended songs to a DataFrame
recommended_df = pd.DataFrame(recommended_songs)

# Print the recommended songs
for idx, song in enumerate(recommended_songs, start=1):
    print(f"{idx}. {song['name']} by {song['artists']} ({song['year']})")

# Create a bar plot of recommended songs by name
recommended_df['text'] = recommended_df.apply(lambda row: f"{row.name + 1}. {row['name']} by {row['artists']} ({row['year']})", axis=1)
fig = px.bar(recommended_df, y='name', x=range(n_recommendations, 0, -1), title='Recommended Songs', orientation='h', text='text')
fig.update_layout(
    xaxis_title='Recommendation Rank',
    yaxis_title='Songs',
    showlegend=False,
    uniformtext_mode='show',
    yaxis_showticklabels=False,
    height=500
)
fig.update_traces(width=1)
fig.show()

# List of seed songs (replace with your own seed songs)
seed_songs = [  {'name': 'Mr. Brightside'},
                {'name': 'Put Your Records On'},
                {'name': 'Man! I Feel Like a Woman!'},
                {'name': 'No Diggity'}
]
seed_songs = [{'name': name['name'].lower()} for name in seed_songs]

# Number of recommended songs
n_recommendations = 5

# Call the recommend_songs function
recommended_songs = recommend_songs(seed_songs, data, n_recommendations)

# Convert the recommended songs to a DataFrame
recommended_df = pd.DataFrame(recommended_songs)

# Print the recommended songs
for idx, song in enumerate(recommended_songs, start=1):
    print(f"{idx}. {song['name']} by {song['artists']} ({song['year']})")

# Create a bar plot of recommended songs by name
recommended_df['text'] = recommended_df.apply(lambda row: f"{row.name + 1}. {row['name']} by {row['artists']} ({row['year']})", axis=1)
fig = px.bar(recommended_df, y='name', x=range(n_recommendations, 0, -1), title='Recommended Songs', orientation='h', text='text')
fig.update_layout(
    xaxis_title='Recommendation Rank',
    yaxis_title='Songs',
    showlegend=False,
    uniformtext_mode='show',
    yaxis_showticklabels=False,
    height=500
)
fig.update_traces(width=1)
fig.show()

# List of seed songs (replace with your own seed songs)
seed_songs = [  {'name': 'Come As You Are'},
                {'name': 'Smells Like Teen Spirit'},
                {'name': 'Lithium'},
                {'name': 'All Apologies'},
                {'name': 'Stay Away'}
]
seed_songs = [{'name': name['name'].lower()} for name in seed_songs]

# Number of recommended songs
n_recommendations = 5

# Call the recommend_songs function
recommended_songs = recommend_songs(seed_songs, data, n_recommendations)

# Convert the recommended songs to a DataFrame
recommended_df = pd.DataFrame(recommended_songs)

# Print the recommended songs
for idx, song in enumerate(recommended_songs, start=1):
    print(f"{idx}. {song['name']} by {song['artists']} ({song['year']})")

# Create a bar plot of recommended songs by name
recommended_df['text'] = recommended_df.apply(lambda row: f"{row.name + 1}. {row['name']} by {row['artists']} ({row['year']})", axis=1)
fig = px.bar(recommended_df, y='name', x=range(n_recommendations, 0, -1), title='Recommended Songs', orientation='h', text='text')
fig.update_layout(
    xaxis_title='Recommendation Rank',
    yaxis_title='Songs',
    showlegend=False,
    uniformtext_mode='show',
    yaxis_showticklabels=False,
    height=500
)
fig.update_traces(width=1)
fig.show()

# List of seed songs (replace with your own seed songs)
seed_songs = [  {'name': 'Relación - Remix'},
                {'name': 'Se Te Nota (with Guaynaa)'},
                {'name': 'La Curiosidad'},
                {'name': 'La Nota'},
                {'name': 'Hawái'},
                {'name': 'Traicionera'},
]
seed_songs = [{'name': name['name'].lower()} for name in seed_songs]

# Number of recommended songs
n_recommendations = 5

# Call the recommend_songs function
recommended_songs = recommend_songs(seed_songs, data, n_recommendations)

# Convert the recommended songs to a DataFrame
recommended_df = pd.DataFrame(recommended_songs)

# Print the recommended songs
for idx, song in enumerate(recommended_songs, start=1):
    print(f"{idx}. {song['name']} by {song['artists']} ({song['year']})")

# Create a bar plot of recommended songs by name
recommended_df['text'] = recommended_df.apply(lambda row: f"{row.name + 1}. {row['name']} by {row['artists']} ({row['year']})", axis=1)
fig = px.bar(recommended_df, y='name', x=range(n_recommendations, 0, -1), title='Recommended Songs', orientation='h', text='text')
fig.update_layout(
    xaxis_title='Recommendation Rank',
    yaxis_title='Songs',
    showlegend=False,
    uniformtext_mode='show',
    yaxis_showticklabels=False,
    height=500
)
fig.update_traces(width=1)
fig.show()

"""## Euclidean"""

import pandas as pd
from sklearn.metrics.pairwise import euclidean_distances, paired_distances
from scipy.stats import pearsonr

# Función para calcular la similitud euclidiana entre dos canciones
def euclidean_similarity(song1, song2):
    return euclidean_distances(song1.values.reshape(1, -1), song2.values.reshape(1, -1))

def recommend_euclidean(song_name, top_n):
    # Obtener datos de la canción dada
    song_data = data[data['name'] == song_name][number_cols]

    # Calcular similitud euclidiana con respecto a todas las canciones
    distances = data[number_cols].apply(lambda x: euclidean_similarity(song_data, x), axis=1)

    # Seleccionar las canciones más similares, excluyendo la canción de entrada
    similar_songs = data.loc[distances.argsort()[1:top_n + 1]]

    # Devolver los nombres de las canciones recomendadas
    return similar_songs['name']

song_to_recommend = 'Dakiti'
euclidean_recommendations = recommend_euclidean(song_to_recommend, 5)

print(f"Recomendaciones basadas en similitud euclidiana para '{song_to_recommend}':")
print(euclidean_recommendations)

# Ejemplo de uso:
song_to_recommend = 'Blinding Lights'
euclidean_recommendations = recommend_euclidean(song_to_recommend, 5)

print(f"Recomendaciones basadas en similitud euclidiana para '{song_to_recommend}':")
print(euclidean_recommendations)

"""## K-Means"""

X = data[number_cols]

# Creamos un pipeline de clustering
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('kmeans', KMeans(n_clusters=10, random_state=42))
])

# Ajustamos el pipeline
pipeline.fit(X)

# Ponemos etiquetas de cluster para cada canción
data['cluster_label'] = pipeline.predict(X)

def recommend_songs(song_name, data, num_songs=5):
    if song_name not in data['name'].values:
        return "La canción no se encontró en la base de datos."

    # Encuentra el cluster de la canción dada
    song_cluster = data[data['name'] == song_name]['cluster_label'].values[0]

    # Encuentra otras canciones en el mismo cluster
    recommended_songs = data[data['cluster_label'] == song_cluster].sample(n=num_songs)

    return recommended_songs[['name', 'artists', 'cluster_label']]

# Ejemplo de uso
print(recommend_songs('Come As You Are', data))

"""## KNN Basics"""

pip install scikit-surprise

from surprise import Dataset, Reader
import pandas as pd
import numpy as np

# Generar datos de usuario y calificaciones simuladas
np.random.seed(42)
data['user_id'] = np.random.randint(0, 5000, size=len(data))  # 5000 usuarios simulados
data['rating'] = data['popularity'] / data['popularity'].max()

# Crear un DataFrame en el formato requerido
ratings_df = data[['user_id', 'id', 'rating']]

# Cargar los datos en Surprise
reader = Reader(rating_scale=(0, 1))
data_surprise = Dataset.load_from_df(ratings_df, reader)

from surprise import KNNBasic
from surprise.model_selection import train_test_split

# Dividir en conjunto de entrenamiento y prueba
trainset, testset = train_test_split(data_surprise, test_size=0.25)

# Crear y entrenar el modelo KNNBasic
algo = KNNBasic()
algo.fit(trainset)

# Hacer algunas predicciones
predictions = algo.test(testset)

from collections import defaultdict

def get_top_n(predictions, songs_data, n=5):
    # Mapear song_id a song_name
    song_id_to_name = pd.Series(songs_data.name.values, index=songs_data.id).to_dict()

    # Preparar la estructura de los top n
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, song_id_to_name.get(iid, "Nombre Desconocido"), est))

    # Ordenar y seleccionar top n
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[2], reverse=True)
        top_n[uid] = user_ratings[:n]

    return top_n

# Obtener las top N recomendaciones para cada usuario
top_n = get_top_n(predictions, data, n=5)

# Ejemplo: Mostrar las top 10 recomendaciones para el usuario 1
for song_id, song_name, rating in top_n[1]:
    print(f"Song ID: {song_id}, Song Name: {song_name}, Est. Rating: {round(rating, 4)}")

# Ejemplo: Mostrar las top 10 recomendaciones para el usuario 1
for song_id, song_name, rating in top_n[5]:
    print(f"Song ID: {song_id}, Song Name: {song_name}, Est. Rating: {round(rating, 4)}")

# Ejemplo: Mostrar las top 10 recomendaciones para el usuario 1
for song_id, song_name, rating in top_n[10]:
    print(f"Song ID: {song_id}, Song Name: {song_name}, Est. Rating: {round(rating, 4)}")

"""# **Deployment del modelo spotipy**

* Check the [GitHub repository](https://github.com/aliduku/Music_Recommendation_System)
* Check the [Streamlit web application](https://musicrecommendationsystem-zkaftqsquighe8wizjvcas.streamlit.app/)
* Check the [kaggle notebook](https://www.kaggle.com/aliessamali/music-recommendation-system-streamlit)
"""

pip install streamlit

import streamlit as st
from scipy.spatial.distance import cdist
import plotly.express as px

# Streamlit App
st.title('Music Recommender')
st.header('Music Recommender Prompt')

# Input para los nombres de las canciones
song_names = st.text_area("Enter song names (one per line):")

# Boton deslizante para seleccionar el número de recomendaciones que se desea obtener
n_recommendations = st.slider("Select the number of recommendations:", 5, 10, 15)

# Se convierte el input a una lista de canciones
input_song_names = song_names.strip().split('\n') if song_names else []

# Button to recommend songs
if st.button('Recommend'):

    seed_songs = [{'name': name.lower()} for name in input_song_names]

    seed_songs = [song for song in seed_songs if song['name']]

    if not seed_songs:
        st.warning("Please enter at least one song name.")
    else:
        recommended_songs = recommend_songs(seed_songs, data, n_recommendations)

        if not recommended_songs:
            st.warning("No recommendations available based on the provided songs.")
        else:
            recommended_df = pd.DataFrame(recommended_songs)

            # Bar plot para las canciones recomendadas
            recommended_df['text'] = recommended_df.apply(lambda row: f"{row.name + 1}. {row['name']} by {row['artists']} ({row['year']})", axis=1)
            fig = px.bar(recommended_df, y='name', x=range(len(recommended_df), 0, -1), title='Recommended Songs', orientation='h', color='name', text='text')
            fig.update_layout(xaxis_title='Recommendation Rank', yaxis_title='Songs', showlegend=False, uniformtext_minsize=20, uniformtext_mode='show', yaxis_showticklabels=False, height=1000, width=1000)
            fig.update_traces(width=1)
            st.plotly_chart(fig)

st.header('Music Data')

# Canciones mas populares
st.subheader('Top Songs by Popularity')
top_songs = data.nlargest(10, 'popularity')
fig_popularity = px.bar(top_songs, x='popularity', y='name', orientation='h',
                        title='Top Songs by Popularity', color='name')
fig_popularity.update_layout(showlegend=False, height=1000, width=1000)
st.plotly_chart(fig_popularity)

# Cantidad de canciones por decada
decade_counts = data['decade'].value_counts().sort_index()

# Grafico de barras de la cantidad de canciones por decada
st.subheader('Number of Songs per Decade')
fig_decades = px.bar(x=decade_counts.index, y=decade_counts.values,
                     labels={'x': 'Decade', 'y': 'Number of Songs'},
                     title='Number of Songs per Decade', color=decade_counts.values)
fig_decades.update_layout(xaxis_type='category', height=1000, width=1000)
st.plotly_chart(fig_decades)

# Histograma de la distribución de los atributos de las canciones
st.subheader('Distribution of Song Attributes')
attribute_to_plot = st.selectbox('Select an attribute to plot:', number_cols)
fig_histogram = px.histogram(data, x=attribute_to_plot, nbins=30,
                              title=f'Distribution of {attribute_to_plot}')
fig_histogram.update_layout(height=1000, width=1000)
st.plotly_chart(fig_histogram)

# Gráfico de barras de los artistas con más canciones en el dataset
st.subheader('Artists with Most Songs')
top_artists = data['artists'].str.replace("[", "").str.replace("]", "").str.replace("'", "").value_counts().head(20)
fig_top_artists = px.bar(top_artists, x=top_artists.index, y=top_artists.values, color=top_artists.index,
                         labels={'x': 'Artist', 'y': 'Number of Songs'},
                         title='Top Artists with Most Songs')
fig_top_artists.update_xaxes(categoryorder='total descending')
fig_top_artists.update_layout(height=1000, width=1000, showlegend=False)
st.plotly_chart(fig_top_artists)
