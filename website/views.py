from flask import Blueprint, render_template
import json
views = Blueprint('views', __name__)


@views.route("/")
def home():
    return render_template("index.html")
@views.route("/search/<search_type>")
def search(search_type):
    return render_template("search.html",type=search_type)
@views.route("/results")
def results():
    # Just a placeholder for now
    with open('recommendations.json','r') as f:
        data = json.load(f)
    return render_template("results.html",result=data['books'])
@views.route("/account")
def account():
    return render_template("account.html")
@views.route("/watchlist")
def watchlist():
    return render_template("watchlist.html")