from flask import Blueprint, render_template
from flaskapp.extensions import db
from flaskapp.models import Restaurant

home = Blueprint('home', __name__)


@home.route('/')
def index():
    print('Request for index page received')
    restaurant = Restaurant(name='Alpha', description='Extra')
    db.session.add(restaurant)
    restaurant = Restaurant(name='Mariama', description='Extra')
    db.session.add(restaurant)
    restaurant = Restaurant(name='Aissatou', description='Super Extra')
    db.session.add(restaurant)
    db.session.commit()
    restaurants = Restaurant.query.all()
    return render_template('home/index.html', restaurants=restaurants)
