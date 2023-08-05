from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

app.config.from_object('deployment.development')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# The import must be done after db initialization due to circular import issue
from models import Restaurant


@app.route('/')
def index():
    print('Request for index page received')
    restaurants = Restaurant.query.all()
    return render_template('index.html', restaurants=restaurants)


if __name__ == '__main__':
    app.run()
