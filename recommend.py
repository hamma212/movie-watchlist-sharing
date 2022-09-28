from ctypes import cast
from distutils.file_util import move_file
from flask import Flask, redirect, render_template, request, session, url_for, current_app, jsonify, abort
import db
import tmdb
import os
from os import environ as env
import requests
import numpy


def get_score_list(curUserId):
    # fetch all users' id
    id_list = db.get_all_users_id()

    # fetch cur user watched list
    cur_watched_list =  db.get_user_media_for_list(curUserId, "watched")
    cur_watching_list = db.get_user_media_for_list(curUserId, "watching")
    cur_will_watch_list = db.get_user_media_for_list(curUserId, "will_watch")

    # fetch other users' watched list
    watched_similarity_score = []
    watching_similarity_score = []
    will_watch_similarity_score = []
    for i in range(len(id_list)):
        watched_info = {}
        watching_info = {}
        will_watch_info = {}
        watched_similarity_count = 0
        watching_similarity_count = 0
        will_watch_similarity_count = 0
        # skip cur user
        if(id_list[i]['user_id'] == curUserId):
            continue
        # get list and count media
        else:
            # WATCHED list compare
            watched_result = db.get_user_media_for_list(id_list[i]['user_id'], "watched")
            for j in range(len(watched_result)):
                if watched_result[j] in cur_watched_list:
                    watched_similarity_count = watched_similarity_count + 1
                else:
                    continue
            # only append users that have the common media in list
            if(watched_similarity_count > 0):
                watched_info["user_id"] = id_list[i]['user_id']
                watched_info["score"] = watched_similarity_count
                watched_similarity_score.append(watched_info)
            
            # WATCHING list compare
            watching_result = db.get_user_media_for_list(id_list[i]['user_id'], "watching")
            for j in range(len(watching_result)):
                if watching_result[j] in cur_watching_list:
                    watching_similarity_count = watching_similarity_count + 1
                else:
                    continue
            # only append users that have the common media in list
            if(watching_similarity_count > 0):
                watching_info["user_id"] = id_list[i]['user_id']
                watching_info["score"] = watching_similarity_count
                watching_similarity_score.append(watching_info)
            
            # WILL WATCH list compare
            will_watch_result = db.get_user_media_for_list(id_list[i]['user_id'], "will_watch")
            for j in range(len(will_watch_result)):
                if will_watch_result[j] in cur_will_watch_list:
                    will_watch_similarity_count = will_watch_similarity_count + 1
                else:
                    continue
            # only append users that have the common media in list
            if(will_watch_similarity_count > 0):
                will_watch_info["user_id"] = id_list[i]['user_id']
                will_watch_info["score"]  = will_watch_similarity_count
                will_watch_similarity_score.append(will_watch_info)

    # Sort by score    
    watched_similarity_score = sorted(watched_similarity_score, key = lambda i: i["score"], reverse = True)
    watching_similarity_score = sorted(watching_similarity_score, key = lambda i: i["score"], reverse = True)
    will_watch_similarity_score = sorted(will_watch_similarity_score, key = lambda i: i["score"], reverse = True)

    return  watched_similarity_score, watching_similarity_score, will_watch_similarity_score

def get_user_info(score_list):
    list_range = 5 if len(score_list) > 5 else len(score_list)
    similar_users = []
    for i in range(list_range):
        user_info = {}
        result = db.get_user_by_id(score_list[i]["user_id"])

        user_info["info"] = result[0]
        name = result[0]["username"].replace(' ', '+')
        user_info["link"] = user_info["link"] = '/user/' + result[0]["user_id"]
        similar_users.append(user_info)
    
    return similar_users

def get_top5_users():
    # get top5 from watched list
    watched_users = db.get_top_users("watched")
    watching_users = db.get_top_users("watching")
    will_watch_users = db.get_top_users("will_watch")

    # get user info
    watched_top = get_user_info(watched_users)
    watching_top = get_user_info(watching_users)
    will_watch_top = get_user_info(will_watch_users)

    return watched_top, watching_top, will_watch_top

def get_top5_watched_users():
    watched_users = db.get_top_users("watched")
    watched_top = get_user_info(watched_users)
    return  watched_top

def get_top5_watching_users():
    watching_users = db.get_top_users("watching")
    watching_top = get_user_info(watching_users)
    return watching_top

def get_top5_will_watch_users():
        will_watch_users = db.get_top_users("will_watch")
        will_watch_top = get_user_info(will_watch_users)
        return will_watch_top


