import json
from threading import Thread, Lock

from flask import Blueprint, render_template
from flask import flash

from book_shelf import BookShelf
from user_info import UserInfo

views = Blueprint('views', __name__)
thread_lock = Lock()
RESULTS = []


def get_user_info(story_graph=False, good_reads=False):
    user = UserInfo()
    if story_graph:
        user.story_graph_csv("story_graph.csv")
    if good_reads:
        user.good_reads_csv("goodreads_library_export.csv")
    return user


def get_subjects(type_of):
    with open('recommendations.json', 'r') as f:
        data = json.load(f)
        return data['subjects']


def get_recs(type_of):
    subjects = get_subjects(type_of)
    with Thread:
        global RESULTS
        shelf = BookShelf()
        shelf.books_from_subjects(subjects)
        RESULTS = shelf.recommendations


@views.route("/")
def home():
    return render_template("index.html")


@views.route("/start_search/<type_of>")
def start_task(type_of):
    thread = Thread(target=get_recs, args=type_of)
    thread.start()
    thread.join()
    return render_template("recommendations",result=RESULTS)


@views.route("/search/<search_type>")
def search(search_type):
    return render_template("search.html", type=search_type)


@views.route("/recommendations")
def recommendations():
    global RESULTS
    if RESULTS:
        return render_template("results.html", result=RESULTS)
    else:
        return render_template("loading.html")


@views.route("/account")
def account():
    return render_template("account.html")


@views.route("/watchlist")
def watchlist():
    return render_template("watchlist.html")
