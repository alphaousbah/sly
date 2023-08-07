from pathlib import Path
import os


class BaseConfig:
    BASE_DIR = Path(__file__).resolve().parent
    DBNAME = 'app.db'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{BASE_DIR}/{DBNAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ['SECRET_KEY']
