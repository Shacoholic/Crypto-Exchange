from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow
from models import account, transaction, credit_card, user, crypto_currency


import os


db = SQLAlchemy()
bcrypt = Bcrypt()
mm = Marshmallow()

basedir = os.path.abspath(os.path.dirname(__file__))


class ApplicationConfig:
    SECRET_KEY = 'unhSADAdDh9'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        basedir, "database.db"
    )

