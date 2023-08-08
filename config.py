import os
from pathlib import Path


class BaseConfig:
    SECRET_KEY = os.environ['SECRET_KEY']
    BASE_DIR = Path(__file__).resolve().parent
    DBNAME = 'app.db'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{BASE_DIR}/{DBNAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class LocalPostgresConfig:
    SECRET_KEY = os.environ['SECRET_KEY']

    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
        dbuser=os.environ['DBUSER'],
        dbpass=os.environ['DBPASS'],
        dbhost=os.environ['DBHOST'],
        dbname=os.environ['DBNAME']
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False


class AzureConfig:
    SECRET_KEY = os.getenv('SECRET_KEY')

    CSRF_TRUSTED_ORIGINS = ['https://' + os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []
    ALLOWED_HOSTS = [os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []

    # Configure Postgres database based on connection string of the libpq Keyword/Value form
    # https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
    conn_str = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
    conn_str_params = {pair.split('=')[0]: pair.split('=')[1] for pair in conn_str.split(' ')}

    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
        dbuser=conn_str_params['user'],
        dbpass=conn_str_params['password'],
        dbhost=conn_str_params['host'],
        dbname=conn_str_params['dbname']
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
