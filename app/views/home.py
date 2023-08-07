from flask import Blueprint, render_template
from app.models import Restaurant

home = Blueprint('home', __name__)


@home.route('/')
def index():
    print('Request for index page received')
    restaurants = Restaurant.query.all()
    return render_template('home/index.html')
