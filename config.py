import os
from pathlib import Path


class Config:
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # WEBSITE_HOSTNAME exists only in production environment
    if 'WEBSITE_HOSTNAME' not in os.environ:
        # Local deployment : we'll use environment variables
        SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
            dbuser=os.environ['DBUSER'],
            dbpass=os.environ['DBPASS'],
            dbhost=os.environ['DBHOST'],
            dbname=os.environ['DBNAME']
        )

    else:
        # Production
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


class SQLiteConfig:
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BASE_DIR = Path(__file__).resolve().parent
    DBNAME = 'app.db'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{BASE_DIR}/{DBNAME}'
