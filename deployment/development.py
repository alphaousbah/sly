from pathlib import Path

BASEDIR = Path(__file__).resolve().parent.parent
DBNAME = 'app.db'

SQLALCHEMY_DATABASE_URI = f'sqlite:///{BASEDIR}/{DBNAME}'

SQLALCHEMY_TRACK_MODIFICATIONS = False
