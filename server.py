from ctypes import cast
from distutils.file_util import move_file
from flask import Flask, redirect, render_template, request, session, url_for, current_app, jsonify, abort
import db
import tmdb
import os
import recommend
import general
from os import dup, environ as env
import requests


#auth imports
from functools import wraps
import json
from werkzeug.exceptions import HTTPException
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode

app = Flask(__name__)


#Set api
api_url=os.environ['API_KEYWORD_QUERY_URL']

api_key = os.environ['API_KEY']




@app.before_first_request
def initialize():
    db.setup()
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(405, method_not_allowed)

# set app secret key
app.secret_key = "i dunnodliufawefnluiFS"



# TODO: enable and configure properly once auth0 is setup
oauth = OAuth(app)

AUTH0_CLIENT_ID = env['auth0_client_id']
AUTH0_CLIENT_SECRET = env['auth0_client_secret']
AUTH0_DOMAIN = env['auth0_domain']

# baseUrl = 'https://infinite-inlet-24245.herokuapp.com'

auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url='https://' + AUTH0_DOMAIN,
    access_token_url='https://' + AUTH0_DOMAIN + '/oauth/token',
    authorize_url='https://' + AUTH0_DOMAIN + '/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)

###AUTH STUFF

@app.route('/callback')
def callback_handling():
    # Handles response from token endpoint
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    # Store the user information in flask session.
    session['jwt_payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture'],
        'email': userinfo['email']
    }
    db.add_new_user(userinfo['sub'], userinfo['name'], "", False, userinfo['picture'])

    if 'return_url' in session.keys():
        return redirect(session['return_url'])
    return redirect(url_for('home'))


@app.route('/login')
def login():
    # return auth0.authorize_redirect(redirect_uri="http://127.0.0.1:5000/callback")
    return auth0.authorize_redirect(redirect_uri=url_for('callback_handling', _external=True))

@app.route('/logout')
def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {'returnTo': url_for('start_page', _external=True), 'client_id': AUTH0_CLIENT_ID}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    if 'profile' not in session:
      # Redirect to Login page here
      return redirect('/login')
    return f(*args, **kwargs)

  return decorated


# *** replaces isLoggedIn = 'profile' in session ***
# args are positional arguments and kwargs are keyword arguments (dictionary)
# isLoggedIn in kwargs gets passed to the isLoggedIn specified in the parameter list of the wrapped function
def logged_in(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        
        kwargs['loggedInInfo'] = {}

        if 'profile' not in session:
            kwargs['loggedInInfo']['isLoggedIn'] = False
            kwargs['loggedInInfo']['profilePicture'] = None
            kwargs['loggedInInfo']['username'] = None
            kwargs['loggedInInfo']['email'] = None
            # current_app.logger.info(kwargs['isLoggedIn'])
        else:
            kwargs['loggedInInfo']['isLoggedIn'] = True
            kwargs['loggedInInfo']['profilePicture'] = session['profile']['picture']
            kwargs['loggedInInfo']['username'] = session['profile']['name']
            kwargs['loggedInInfo']['email'] = session['profile']['email']
            # kwargs['curUserId'] = session['profile']['user_id']
            # current_app.logger.info(kwargs['isLoggedIn'])
        return f(*args, **kwargs)
    return decorated


# PAGES


@app.route('/', methods=['GET'])
def start_page():
    return redirect(url_for('welcome'))

@app.route('/welcome')
@logged_in
def welcome(loggedInInfo):
    # current_app.logger.info(isLoggedIn)
    return render_template('welcome.html', \
        isLoggedIn=loggedInInfo['isLoggedIn'], profilePicture=loggedInInfo['profilePicture'], email=loggedInInfo['email'])

@app.route('/home', methods=['GET'])
@logged_in
def home(loggedInInfo):
    most_popular_2d = db.get_most_popular_media()
    # [['323660', '99861'], ['9320', '99861', '2473', '299536'], ['24428', '299534']
    watched_info=[]
    watching_info=[]
    will_watch_info=[]
    for i in range(len(most_popular_2d[0])):
        info={}

        media = db.get_media_by_id(most_popular_2d[0][i])
        info["title"] = media[0]["media_title"]
        info["poster"] =  media[0]["media_poster_path"]
        info["link"] = '/mediaInfo/' +  media[0]["media_type"] + '/' + most_popular_2d[0][i]

        watched_info.append(info)        

    for i in range(len(most_popular_2d[1])):
        info={}
        media = db.get_media_by_id(most_popular_2d[1][i])
        info["title"] = media[0]["media_title"]
        info["poster"] =  media[0]["media_poster_path"]
        info["link"] = '/mediaInfo/' +  media[0]["media_type"] + '/' + most_popular_2d[1][i]
        
        watching_info.append(info)

    for i in range(len(most_popular_2d[2])):
        info={}
        media = db.get_media_by_id(most_popular_2d[2][i])
        info["title"] = media[0]["media_title"]
        info["poster"] =  media[0]["media_poster_path"]
        info["link"] = '/mediaInfo/' +  media[0]["media_type"] + '/' + most_popular_2d[2][i]

        will_watch_info.append(info)
    return render_template('homepage.html', watched_info=watched_info, watching_info=watching_info, will_watch_info=will_watch_info, \
        isLoggedIn=loggedInInfo['isLoggedIn'], profilePicture=loggedInInfo['profilePicture'], email=loggedInInfo['email'])


@app.route('/community', methods=['GET'])
@logged_in
def community(loggedInInfo):
    is_watched = True 
    is_watching = True 
    is_will_watch = True
    if(loggedInInfo['isLoggedIn'] == True):
        user_id = str(session['profile']['user_id'])
        watched_score, watching_score, will_watch_score = recommend.get_score_list(user_id)
        watched_users = recommend.get_user_info(watched_score)
        if(len(watched_users) == 0):
            watched_users = recommend.get_top5_watched_users()
            is_watched = False
        watching_users = recommend.get_user_info(watching_score)
        if(len(watching_users) == 0):
            watching_users  = recommend.get_top5_watching_users()
            is_watching = False
        will_watch_users = recommend.get_user_info(will_watch_score)
        if(len(will_watch_users) == 0):
            will_watch_users = recommend.get_top5_will_watch_users()
            is_will_watch = False
        for dic in will_watch_users:
            if dic['info']['user_id'] == user_id:
                will_watch_users.remove(dic)
        for dic in watching_users:
            if dic['info']['user_id'] == user_id:
                watching_users.remove(dic)
        for dic in watched_users:
            if dic['info']['user_id'] == user_id:
                watched_users.remove(dic)
    else:
        is_watched = False
        is_watching = False
        is_will_watch = False
        watched_users, watching_users, will_watch_users = recommend.get_top5_users()
    return render_template('community.html', \
        isLoggedIn=loggedInInfo['isLoggedIn'], profilePicture=loggedInInfo['profilePicture'], email=loggedInInfo['email'],  
        watched_users = watched_users, watching_users = watching_users, will_watch_users = will_watch_users,
        is_watched = is_watched, is_watching = is_watching, is_will_watch = is_will_watch)


@app.route('/search', methods=['GET'])
@logged_in
def search(loggedInInfo):
    session['return_url'] = request.url
    current_app.logger.info(session['return_url'])
    search_type = request.args["search_options"]
    search_query = request.args["search_query"]
    if search_type == "media" :
        api_query = api_url +search_query
        response = (requests.request("GET", api_query)).json()
        res_ids = [str(media['id']) for media in response['results']]
        if (loggedInInfo['isLoggedIn']):
            addedLists = db.is_media_list_in_user(res_ids, session['profile']['user_id'])
        else:
            addedLists = db.is_media_list_in_user(res_ids, "-1")
        current_app.logger.info(addedLists)
        return render_template('search.html', searchQuery= search_query, motionPictures = response["results"], \
            isLoggedIn=loggedInInfo['isLoggedIn'], profilePicture=loggedInInfo['profilePicture'], email=loggedInInfo['email'],
            addedLists = addedLists)
    else:
            
        pattern_match_search = '%'+ search_query + '%'
        if (loggedInInfo['isLoggedIn']):
            users = db.get_user(pattern_match_search, session['profile']['user_id'], True)
            followees = db.get_followee_ids_by_user_id(session['profile']['user_id'])
            for user in users:
                if (user['user_id'] in followees):
                    user['is_followed'] = True
                else:
                    user['is_followed'] = False
        else:
            users = db.get_user(pattern_match_search, None, False)

        return render_template('userSearch.html', searchQuery= search_query, users=users, \
            isLoggedIn=loggedInInfo['isLoggedIn'], profilePicture=loggedInInfo['profilePicture'], email=loggedInInfo['email'])


# Check if media is in db then add to specified list
@app.route('/addToList', methods=['POST'])
@requires_auth
def addToList():
    media_id = request.form['mediaID']
    media_type = request.form['media_type']
    media_title = request.form['media_title']
    media_poster_path = request.form['media_poster']

    if(db.is_media_in_db(media_id) == False):
        db.add_new_media(media_id, media_type,media_title,media_poster_path)
    
    # Check if media is already in a watchlist
    dupe_add = db.is_media_in_user(media_id, session['profile']['user_id'])
    current_app.logger.info(dupe_add)
    if(dupe_add[0]):
        db.update_list_db(session['profile']['user_id'], media_id, dupe_add[1], request.form['listType'])
        return redirect(session['return_url'])

    if request.form['listType'] == "watching":
        db.add_item_to_watching(session['profile']['user_id'], media_id)
    elif request.form['listType'] == "watched":
        db.add_item_to_watched(session['profile']['user_id'], media_id)
    else: # 'will_watch'
        db.add_item_to_will_watch(session['profile']['user_id'], media_id)
    return redirect(session['return_url'])


@app.route('/profile', methods=['GET'])
@logged_in
@requires_auth
def profile(loggedInInfo):
    watched = db.get_user_media_for_list(str(session['profile']['user_id']), "watched")
    watched_info = []
    for i in range(len(watched)):
        info = {}
        
        media = db.get_media_by_id(watched[i])
        info['id'] = watched[i]
        info["title"] = media[0]["media_title"]
        info["poster"] =  media[0]["media_poster_path"]
        info["link"] = '/mediaInfo/' +  media[0]["media_type"] + '/' + watched[i]

        watched_info.append(info)

    watching = db.get_user_media_for_list(str(session['profile']['user_id']), "watching")
    watching_info = []
    for i in range(len(watching)):
        info = {}

        media = db.get_media_by_id(watching[i])
        info['id'] = watching[i]
        info["title"] = media[0]["media_title"]
        info["poster"] =  media[0]["media_poster_path"]
        info["link"] = '/mediaInfo/' +  media[0]["media_type"] + '/' + watching[i]

        watching_info.append(info)
    
    will_watch = db.get_user_media_for_list(str(session['profile']['user_id']), "will_watch")
    will_watch_info = []
    for i in range(len(will_watch)):
        info = {}

        media = db.get_media_by_id(will_watch[i])
        info['id'] = will_watch[i]
        info["title"] = media[0]["media_title"]
        info["poster"] =  media[0]["media_poster_path"]
        info["link"] = '/mediaInfo/' +  media[0]["media_type"] + '/' + will_watch[i]

        will_watch_info.append(info)

    user_profile = db.get_user_by_id(str(session['profile']['user_id']))

    return render_template('profile.html', watched_info=watched_info, watching_info=watching_info, will_watch_info=will_watch_info, \
        isLoggedIn=loggedInInfo['isLoggedIn'], profilePicture=loggedInInfo['profilePicture'], email=loggedInInfo['email'], user_profile = user_profile)

@app.route('/mediaInfo/<string:media_type>/<string:media_id>', methods=['GET'])
@logged_in
def mediaInfo(media_type, media_id, loggedInInfo):
    session['return_url'] = request.url
    mediaData = None
    if (media_type == "movie"):
        mediaData = tmdb.query_by_movie_id(media_id)
    elif (media_type == "tv"):
        mediaData = tmdb.query_by_tv_id(media_id)
        
    if (mediaData == None):
            abort(404, description="Media ID: " + media_id + ",Media Type:" + media_type + " not found")
    mediaData.update({"media_type": media_type})

    if (media_type == "movie"):
        castData = tmdb.query_cast_info_by_movie_id(media_id, 6)
    elif (media_type == "tv"):
        castData = tmdb.query_cast_info_by_tv_id(media_id, 6)
    
    watchlistCounts = db.get_watchlist_count_by_media_id(media_id)

    
    # Show related users, check if media is already in one of user's watchlists
    if (loggedInInfo['isLoggedIn']):
        users_id = db.get_users_by_media(media_id, session['profile']['user_id'], True)
        added = db.is_media_in_user(media_id, session['profile']['user_id'])
        if (added[0]):
            if (added[1] == 'will_watch'):
                addedList = "Want to Watch"
            elif (added[1] == 'watching'):
                addedList = "Watching"
            elif (added[1] == 'watched'):
                addedList = "Watched"
        else:
            addedList = 'null'
    else:
        users_id = db.get_users_by_media(media_id, None, False)
        addedList = 'null'
        
    watched_users = []
    for user in users_id[:4]:
        # if (user["user_id"] == session['profile']['user_id']):
        #     continue
        user_info={}
        result = db.get_user_by_id(user["user_id"])
        user_info["info"] = result[0]
        user_info["link"] = '/user/' + result[0]["user_id"]
        watched_users.append(user_info)
        current_app.logger.info(result)

    return render_template('mediaInfo.html', mediaData = mediaData, castData = castData, watchlistCounts = watchlistCounts, \
        isLoggedIn=loggedInInfo['isLoggedIn'], profilePicture=loggedInInfo['profilePicture'], email=loggedInInfo['email'], watched_users = watched_users,
        addedList = addedList)

@app.errorhandler(404)
@logged_in
def page_not_found(e, loggedInInfo):
    return render_template('/error/404.html', errorStr=e, isLoggedIn=loggedInInfo['isLoggedIn'], profilePicture=loggedInInfo['profilePicture'], email=loggedInInfo['email']), 404

@app.errorhandler(405)
@logged_in
def method_not_allowed(e, loggedInInfo):
    return render_template('/error/405.html', errorStr=e, isLoggedIn=loggedInInfo['isLoggedIn'], profilePicture=loggedInInfo['profilePicture'], email=loggedInInfo['email']), 405


@app.route('/update_list', methods=['POST'])
@requires_auth
def update_list():
    user = str(session['profile']['user_id'])
    id = request.form['media_id']
    start = request.form['start']
    end = request.form['end']
    db.update_list_db(user, id, start, end)
    return redirect(url_for('profile'))

@app.route('/remove_from_list', methods=['POST'])
@requires_auth
def remove_from_list():
    user = str(session['profile']['user_id'])
    id = request.form['mediaID']
    if (request.form['addedList'] == "Want to Watch"):
        start = "will_watch"
    else:
        start = request.form['addedList'].lower()
    current_app.logger.info("attempting to delete " + id + " from " + start)
    end = "delete"
    db.update_list_db(user, id, start, end)
    return redirect(session['return_url'])


@app.route('/update_bio', methods=['POST'])
@requires_auth
def update_bio():
    bio_text=request.form.get('bio')
    user_id = str(session['profile']['user_id'])
    db.update_bio(user_id, bio_text)
    return redirect(url_for('profile'))


@app.route('/user/<string:user_id>', methods=['GET'])
@logged_in
def publicProfile(user_id, loggedInInfo):
    if (len(db.get_user_by_id(user_id)) == 0):
            abort(404, description="User ID: " + user_id + " not found")

    if (not loggedInInfo['isLoggedIn'] or session['profile']['user_id'] != user_id): #if user is not logged in or if user is not accessing their own user page
        session['return_url'] = request.url

        watched = db.get_user_media_for_list(str(user_id), "watched")
        watched_info = []
        for i in range(len(watched)):
            info = {}

            media = db.get_media_by_id(watched[i])
            info['id'] = watched[i]
            info["title"] = media[0]["media_title"]
            info["poster"] =  media[0]["media_poster_path"]
            info["link"] = '/mediaInfo/' +  media[0]["media_type"] + '/' + watched[i]

            watched_info.append(info)

        watching = db.get_user_media_for_list(str(user_id), "watching")
        watching_info = []
        for i in range(len(watching)):
            info = {}

            media = db.get_media_by_id(watching[i])
            info['id'] = watching[i]
            info["title"] = media[0]["media_title"]
            info["poster"] =  media[0]["media_poster_path"]
            info["link"] = '/mediaInfo/' +  media[0]["media_type"] + '/' + watching[i]

            watching_info.append(info)

        will_watch = db.get_user_media_for_list(str(user_id), "will_watch")
        will_watch_info = []
        for i in range(len(will_watch)):
            info = {}

            media = db.get_media_by_id(will_watch[i])
            info['id'] = will_watch[i]
            info["title"] = media[0]["media_title"]
            info["poster"] =  media[0]["media_poster_path"]
            info["link"] = '/mediaInfo/' +  media[0]["media_type"] + '/' + will_watch[i]

            will_watch_info.append(info)

        user_profile = db.get_user_by_id(str(user_id))

        is_followed = False
        if (loggedInInfo['isLoggedIn']):
            followees = db.get_followee_ids_by_user_id(session['profile']['user_id'])
            if (user_profile[0]['user_id'] in followees):
                is_followed = True

        return render_template('publicProfile.html', watched_info=watched_info, watching_info=watching_info, will_watch_info=will_watch_info, \
            isLoggedIn=loggedInInfo['isLoggedIn'], profilePicture=loggedInInfo['profilePicture'], email=loggedInInfo['email'], user_profile=user_profile, is_followed=is_followed)

    else: #if user is trying to access their own user page, redirect to profile
        return redirect(url_for('profile'))
  
@app.route('/following')
@logged_in
@requires_auth
def following(loggedInInfo):
    session['return_url'] = request.url
    followees = db.get_followees_by_user_id_sorted_by_username(session['profile']['user_id'])
    # followees = db.get_users_by_ids(followees)

    return render_template('following.html', isLoggedIn=loggedInInfo['isLoggedIn'], profilePicture=loggedInInfo['profilePicture'], email=loggedInInfo['email'], \
        followees=followees)

@app.route('/add_new_follow', methods=['POST'])
@requires_auth
def add_new_follow():
    followee_id = request.form.get('followee')
    db.add_new_follow(session['profile']['user_id'], followee_id)
    return redirect(session['return_url'])

@app.route('/unfollow', methods=['POST'])
@requires_auth
def unfollow():
    followee_id = request.form.get('followee')
    db.unfollow(session['profile']['user_id'], followee_id)
    return redirect(session['return_url'])

# @app.route('/parent')
# def parent():
#     return render_template('parent.html')


