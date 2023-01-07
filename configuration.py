from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt



import os


db = SQLAlchemy()
bcrypt = Bcrypt()

basedir = os.path.abspath(os.path.dirname(__file__))


class ApplicationConfig:
    SECRET_KEY = 'unhSADAdDh9'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        basedir, "database.db"
    )

    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True

