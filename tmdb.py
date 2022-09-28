from flask import current_app
import requests
import os

#Set api
api_url=os.environ['API_KEYWORD_QUERY_URL']

api_key = os.environ['API_KEY']

# API helper function takes in a str movie id and 
# queries by the ID to return jsonified movie info
def query_by_movie_id(movieID):
    query_url = "https://api.themoviedb.org/3/movie/"+movieID+api_key
    response = (requests.request("GET",query_url)).json()
    try:
        if response['success'] == False: # no media found
            return None
    except: 
        return response

# API helper function takes in a str tv id and 
# queries by the ID to return jsonified tv info
def query_by_tv_id(tvID):
    query_url = "https://api.themoviedb.org/3/tv/"+tvID+api_key+"&append_to_response=external_ids"
    response = (requests.request("GET",query_url)).json()
    try:
        if response['success'] == False: # no media found
            return None
    except: 
        return response


# Returns 5 most popular cast members by movie_id
def query_cast_info_by_movie_id(movieID, numCast):
    query_url = "https://api.themoviedb.org/3/movie/" + movieID + "/credits" + api_key
    response = (requests.request("GET",query_url)).json()
    sorted_response = sorted(response["cast"], key=lambda d: d['popularity'], reverse=True)
    return sorted_response[:numCast]

# Returns 5 most popular cast members by tv_id
def query_cast_info_by_tv_id(tvID, numCast):
    query_url = "https://api.themoviedb.org/3/tv/" + tvID + "/credits" + api_key
    response = (requests.request("GET",query_url)).json()
    sorted_response = sorted(response["cast"], key=lambda d: d['popularity'], reverse=True)
    return sorted_response[:numCast]