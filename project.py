#importing the required libraries
import numpy as np
import pandas as pd
import pickle
#import matrix_factorization_utilities
import scipy.sparse as sp
from scipy.sparse.linalg import svds
from flask import Flask, render_template, request, redirect, url_for
from IPython.display import HTML

def best_movies_by_genre(genre,top_n):
    movie_score = pd.read_csv('movie_score.csv')
    return pd.DataFrame(movie_score.loc[(movie_score[genre]==1)].sort_values(['weighted_score'],ascending=False)[['title','count','mean','weighted_score']][:top_n])

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/genres")
def genres():
    return render_template('genres.html')

@app.route("/genre", methods = ['GET','POST'])
def genre():
    if request.method == 'POST':
      result = request.form
      print(result['Genre'])
      print(type(result['Genre']))
      df = best_movies_by_genre(result['Genre'],10)
      df.reset_index(inplace=True)
      df = df.drop(labels='index', axis=1)
      html = HTML(df.to_html(classes='table table-striped'))
      dummy = {}
      dummy[0] = html
      return render_template('genre.html',result = dummy, gename = {1:result['Genre']})
    else:
        return render_template('index.html')
    
if __name__ == "__main__":
    app.run(debug=True)

'''
def init():
    movie_score = pd.read_csv('movie_score.csv')
    ratings_movies = pd.read_csv('ratings_movies.csv')
    movie_content_df_temp = pd.read_csv('mv_cnt_tmp.csv')
    a_file = open("indicies.pkl", "rb")
    inds = pickle.load(a_file)
    a_file.close()
    print(inds['Skyfall (2012)'])
    rev_ind = {}
    for key,val in inds.items():
        rev_ind[val] = key
    from numpy import load
    data_dict = load('cosine.npz')
    cosine_sim = data_dict['arr_0']
    #ratings_movies.head()'''

#movie_score.head()

# Gives the best movies according to genre based on weighted score which is calculated using IMDB formula


# best_movies_by_genre('Musical',10)  

# Gets the other top 10 movies which are watched by the people who saw this particular movie

def get_other_movies(movie_name):
    ratings_movies = pd.read_csv('ratings_movies.csv')
    #get all users who watched a specific movie
    df_movie_users_series = ratings_movies.loc[ratings_movies['title']==movie_name]['userId']
    #convert to a data frame
    df_movie_users = pd.DataFrame(df_movie_users_series,columns=['userId'])
    #get a list of all other movies watched by these users
    other_movies = pd.merge(df_movie_users,ratings_movies,on='userId')
    #get a list of the most commonly watched movies by these other user
    other_users_watched = pd.DataFrame(other_movies.groupby('title')['userId'].count()).sort_values('userId',ascending=False)
    other_users_watched['perc_who_watched'] = round(other_users_watched['userId']*100/other_users_watched['userId'][0],1)
    return other_users_watched[1:11]

# get_other_movies('Gone Girl (2014)')



# Directly getting top 10 movies based on content similarity
# cosine_sim

def get_similar_movies_based_on_content(movie_name) :
    movie_content_df_temp = pd.read_csv('mv_cnt_tmp.csv')
    a_file = open("indicies.pkl", "rb")
    inds = pickle.load(a_file)
    a_file.close()
    print(inds['Skyfall (2012)'])
    rev_ind = {}
    for key,val in inds.items():
        rev_ind[val] = key
    from numpy import load
    data_dict = load('cosine.npz')
    cosine_sim = data_dict['arr_0']
    movie_index = inds[movie_name]
    sim_scores = list(enumerate(cosine_sim[movie_index]))
    # Sort the movies based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
   
    # Get the scores of the 10 most similar movies
    sim_scores = sim_scores[0:11]
    print(sim_scores)
    # Get the movie indices
    movie_indices = [i[0] for i in sim_scores]
    if(movie_index in movie_indices):
        movie_indices.remove(movie_index)
    print(movie_indices)
    similar_movies = pd.DataFrame(movie_content_df_temp[['title','genres']].iloc[movie_indices])
    return similar_movies[:10]
