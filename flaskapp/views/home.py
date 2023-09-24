from flask import Blueprint, render_template
from flaskapp.extensions import db
from flaskapp.models import *

home = Blueprint('home', __name__)


@home.route('/')
def index():
    return render_template('home/index.html')
