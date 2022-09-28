""" database access
docs:
* http://initd.org/psycopg/docs/
* http://initd.org/psycopg/docs/pool.html
* http://initd.org/psycopg/docs/extras.html#dictionary-like-cursor
"""

from contextlib import contextmanager
import logging
import os
from warnings import catch_warnings

from flask import current_app, g

import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor
from psycopg2 import sql

# pool variable. -- this is being used as a global will be shared across threads, not processes
# (which shoudl be good enough for a project of this scale.)
pool = None

# request this to run before first request and setup a connection pool
def setup():
    global pool
    DATABASE_URL = os.environ['DATABASE_URL']
    current_app.logger.info(f"creating db connection pool")
    pool = ThreadedConnectionPool(1, 20, dsn=DATABASE_URL, sslmode='require')


# use the contect manager annotation to let us use generator-style python
# code to create a context-manager all our own -- this makes _using_ the library easy
# even if it's more python-magic than you're used to on this end.
@contextmanager
def get_db_connection():
    try:
        connection = None
        while connection is None:
            try:
                connection = pool.getconn()
            except:
                current_app.logger.info("failed to get connection. retrying immediately.")

        yield connection
    finally:
        if connection is not None:
            pool.putconn(connection)

@contextmanager
def get_db_cursor(commit=False):
    '''use commit = true to make lasting changes. Call this function in a with statement'''
    with get_db_connection() as connection:
      cursor = connection.cursor(cursor_factory=RealDictCursor)
      try:
          yield cursor
          if commit:
              connection.commit()
      finally:
          cursor.close()


# Helper functions 

def add_item_to_watched(user_id,media_id):
    with get_db_cursor(True) as cur:
        current_app.logger.info("Adding media %s to user %s's watched list", media_id,user_id)
        try:
            cur.execute("INSERT INTO watched (user_id, media_id) values (%s,%s)", (user_id, media_id))
        except:
            current_app.logger.info("failed to insert media %s",media_id)
            

def add_item_to_watching(user_id,media_id):
    with get_db_cursor(True) as cur:
        current_app.logger.info("Adding media %s to user %s's watching list", media_id,user_id)
        try:
            cur.execute("INSERT INTO watching (user_id, media_id) values (%s,%s)", (user_id, media_id))
        except: 
            current_app.logger.info("failed to insert media %s",media_id)


def add_item_to_will_watch(user_id,media_id):
    with get_db_cursor(True) as cur:
        current_app.logger.info("Adding media %s to user %s's will watch list", media_id,user_id)
        try:
            cur.execute("INSERT INTO will_watch (user_id, media_id) values (%s,%s)", (user_id, media_id)) 
        except:
            current_app.logger.info("failed to insert media %s",media_id)

def add_new_media(media_id, media_type, media_title, media_poster_path):
    with get_db_cursor(True) as cur:
        current_app.logger.info("Adding media %s to db", (media_id, media_type, media_title, media_poster_path))
        cur.execute("INSERT INTO media (media_id, media_type, media_title, media_poster_path) values (%s,%s,%s,%s)", (media_id, media_type, media_title, media_poster_path))

def is_media_in_db(media_id):
    with get_db_cursor(False) as cur:
        cur.execute("SELECT * from media where media_id = %s;", (media_id,))
        all_media = [record for record in cur]
        if(len(all_media) == 0):
            return False
        else:
            return True

def is_media_in_user(media_id, user_id):
    with get_db_cursor(False) as cur:
        cur.execute("SELECT * from watched where media_id = %s AND user_id = %s;", (media_id, user_id))
        if (len(cur.fetchall()) > 0):
            return (True, "watched")
        cur.execute("SELECT * from watching where media_id = %s AND user_id = %s;", (media_id, user_id))
        if (len(cur.fetchall()) > 0):
            return (True, "watching")
        cur.execute("SELECT * from will_watch where media_id = %s AND user_id = %s;", (media_id, user_id))
        if (len(cur.fetchall()) > 0):
            return (True, "will_watch")
    return (False, "none")

def is_media_list_in_user(media_ids, user_id):
    res = {}
    with get_db_cursor(False) as cur:
        for media_id in media_ids:
            cur.execute("SELECT * from watched where media_id = %s AND user_id = %s;", (media_id, user_id))
            if (len(cur.fetchall()) > 0):
                res[int(media_id)] = "Watched"
            cur.execute("SELECT * from watching where media_id = %s AND user_id = %s;", (media_id, user_id))
            if (len(cur.fetchall()) > 0):
                res[int(media_id)] = "Watching"
            cur.execute("SELECT * from will_watch where media_id = %s AND user_id = %s;", (media_id, user_id))
            if (len(cur.fetchall()) > 0):
                res[int(media_id)] = "Want to Watch"
            if int(media_id) not in res.keys():
                res[int(media_id)] = "null"
    return res


def add_new_user(user_id, username, bio, public, picture):
    with get_db_cursor(True) as cur:
        current_app.logger.info("Adding user %s to db", user_id)
        try:
            cur.execute("INSERT INTO users (user_id, username, bio, public, picture) values (%s,%s,%s,%s,%s)", (user_id, username, bio, public, picture))
        except:
            current_app.logger.info("failed to insert user %s", user_id)


def get_user(username, loggedInUserID, logged_in):
    with get_db_cursor() as cur:
        current_app.logger.info("Getting users with %s username", username)
        cur.execute("SELECT * FROM users where username ILIKE %s", (username,))
        users = cur.fetchall()
        
        users_dict_list = []

        if (logged_in):
            for row in users:
                dict_row = dict(row)
                if (dict_row['user_id'] != loggedInUserID):
                    users_dict_list.append(dict_row)
                else:
                    continue

        else:
            users_dict_list = [dict(row) for row in users]
        
        return users_dict_list
    
          
def get_user_media_for_list(user_id, list_type):
    with get_db_cursor() as cur:
        current_app.logger.info("getting media for %s's %s list", user_id, list_type)
        if (list_type == "watched"):
            cur.execute("select media_id from watched where user_id = (%s)", (user_id,))
            res = cur.fetchall()
            watched = [row["media_id"] for row in res]
            return watched
        elif (list_type == "watching"):
            cur.execute("select media_id from watching where user_id = (%s)", (user_id,))
            res = cur.fetchall()
            watching = [row["media_id"] for row in res]
            return watching
        elif (list_type == "will_watch"):
            cur.execute("select media_id from will_watch where user_id = (%s)", (user_id,))
            res = cur.fetchall()
            will_watch = [row["media_id"] for row in res]
            return will_watch
        else:
            current_app.logger.info("User does not have a list called %s", list_type)

def get_watchlist_count_by_media_id(media_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT count(*) FROM watched where media_id = %s", (media_id,))
        watched = cur.fetchone()['count']
        cur.execute("SELECT count(*) FROM watching where media_id = %s", (media_id,))
        watching = cur.fetchone()['count']
        cur.execute("SELECT count(*) FROM will_watch where media_id = %s", (media_id,))
        will_watch = cur.fetchone()['count']
    return [watched, watching, will_watch]

# returns 2d list w/ top [watched media_ids, watching media_ids, will_watch media_ids]
def get_most_popular_media():
    num_media = 5
    with get_db_cursor() as cur:
        cur.execute("SELECT media_id FROM watched GROUP BY media_id ORDER BY count(user_id) desc")
        res = cur.fetchmany(num_media)
        watched = [row["media_id"] for row in res]
        
        cur.execute("SELECT media_id FROM watching GROUP BY media_id ORDER BY count(user_id) desc")
        res = cur.fetchmany(num_media)
        watching = [row["media_id"] for row in res]

        cur.execute("SELECT media_id FROM will_watch GROUP BY media_id ORDER BY count(user_id) desc")
        res = cur.fetchmany(num_media)
        will_watch = [row["media_id"] for row in res]
    return [watched, watching, will_watch]

def get_media_type_by_id(media_id):
    if (is_media_in_db(media_id)):
        with get_db_cursor() as cur:
            cur.execute("SELECT media_type FROM media WHERE media_id=%s", (media_id,))
            res = cur.fetchone()
            return res["media_type"]
    else: return None


def get_media_by_id(media_id):
    if (is_media_in_db(media_id)):
        with get_db_cursor() as cur:
            cur.execute("SELECT * FROM media WHERE media_id=%s", (media_id,))
            res = cur.fetchall()
            res = [dict(row) for row in res]
            return res
    else: return None

def update_list_db(user, media_id, start, end):
    with get_db_cursor(True) as cur:
        if start == "will_watch" and end == "watching":
            cur.execute("DELETE FROM will_watch where user_id = %s and media_id = %s", (user, media_id,))
            add_item_to_watching(user, media_id)
        elif start == "will_watch" and end == "watched":
            cur.execute("DELETE FROM will_watch where user_id = %s and media_id = %s", (user, media_id,))
            add_item_to_watched(user, media_id)


        elif start == "watching" and end == "will_watch":
            cur.execute("DELETE FROM watching where user_id = %s and media_id = %s", (user, media_id,))
            add_item_to_will_watch(user, media_id)
        elif start == "watching" and end == "watched":
            cur.execute("DELETE FROM watching where user_id = %s and media_id = %s", (user, media_id,))
            add_item_to_watched(user, media_id)


        elif start == "watched" and end == "will_watch":
            cur.execute("DELETE FROM watched where user_id = %s and media_id = %s", (user, media_id,))
            add_item_to_will_watch(user, media_id)

        elif start == "watched" and end == "watching":
            cur.execute("DELETE FROM watched where user_id = %s and media_id = %s", (user, media_id,))
            add_item_to_watching(user, media_id)

        # DELETE
        elif start == "watched" and end == "delete":
            cur.execute("DELETE FROM watched WHERE user_id = %s and media_id = %s", (user, media_id))
        elif start == "watching" and end == "delete":
            cur.execute("DELETE FROM watching WHERE user_id = %s and media_id = %s", (user, media_id))
        elif start == "will_watch" and end == "delete":
            cur.execute("DELETE FROM will_watch  WHERE user_id = %s and media_id = %s", (user, media_id))
         
        # log
        if end == "delete":
             current_app.logger.info("deleted %s from %s ", media_id, start)
        else:
            current_app.logger.info("deleted %s from %s and inserted it into %s", media_id, start, end)


     

def get_users_by_media(media_id, user_id, logged_in):
    with get_db_cursor() as cur:
        cur.execute("SELECT user_id FROM watched WHERE media_id = %s", (media_id,))
        watched_id = cur.fetchall()
        cur.execute("SELECT user_id FROM watching WHERE media_id = %s", (media_id,))
        watching_id = cur.fetchall()
        cur.execute("SELECT user_id FROM will_watch WHERE media_id = %s", (media_id,))
        will_watch_id = cur.fetchall()

        all_id = watched_id + watching_id + will_watch_id
        return_id = []
        if (logged_in):
            for user in all_id:
                if user not in return_id and user['user_id'] != user_id:
                    return_id.append(user)
        else:
            for user in all_id:
                if user not in return_id:
                    return_id.append(user)        
        # return_id = watched_id + watching_id + will_watch_id

        
        
        users_id = [dict(row) for row in return_id]
        return users_id

def get_user_by_id(user_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM users where user_id = %s", (user_id,))
        users = cur.fetchall()
        users = [dict(row) for row in users]       
        return users

def get_users_by_ids(user_id_list):
    with get_db_cursor() as cur:
        users = []
        for user_id in user_id_list:
            users.append(get_user_by_id(user_id)[0])
        current_app.logger.info(users)
        return users

def get_all_users_id():
    with get_db_cursor() as cur:
        cur.execute("SELECT user_id FROM users")
        users = cur.fetchall()
        users = [dict(row) for row in users]       
        return users

def update_bio(user_id, bio_text):
    with get_db_cursor(True) as cur:
        try:
            cur.execute("UPDATE users SET bio = %s WHERE user_id = %s", (bio_text, user_id))
            current_app.logger.info("update bio SUCCESS")

        except:
            current_app.logger.info("failed to update bio")


def get_top_users(list_type):
    with get_db_cursor() as cur:
        if list_type == "watched":
            cur.execute("SELECT user_id, COUNT(1) AS score FROM watched GROUP BY user_id ORDER BY count(media_id) desc")
            res = cur.fetchall()
            users = [dict(row) for row in res]       
            
        elif list_type == "watching":
            cur.execute("SELECT user_id, COUNT(1) AS score FROM watching GROUP BY user_id ORDER BY count(media_id) desc")
            res = cur.fetchall()
            users = [dict(row) for row in res]       

        else:
            cur.execute("SELECT user_id, COUNT(1) AS score FROM will_watch GROUP BY user_id ORDER BY count(media_id) desc")
            res = cur.fetchall() 
            users = [dict(row) for row in res]    

        return users    

def add_new_follow(follower, followee):
    with get_db_cursor(True) as cur:
        cur.execute("INSERT INTO follow (follower, followee) values (%s, %s)", (follower, followee))
       

def get_followee_ids_by_user_id(user_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT followee from follow where follower = %s", (user_id,))
        followees = cur.fetchall()
        if (len(followees) == 0):
            followees = []
        else:
            followees = [dict(row)['followee'] for row in followees]
        current_app.logger.info(followees)
        return followees

def get_followees_by_user_id_sorted_by_username(user_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT users.* FROM follow INNER JOIN users ON follow.followee = users.user_id WHERE follow.follower = %s ORDER BY users.username", (user_id,))
        followees = cur.fetchall()
        if (len(followees) == 0):
            followees = []
        else:
            followees = [dict(row) for row in followees]
        current_app.logger.info(followees)
        return followees

def unfollow(follower, followee):
    with get_db_cursor(True) as cur:
        cur.execute("DELETE FROM follow WHERE follower = %s AND followee = %s", (follower, followee))
