from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os


db = SQLAlchemy()
from models.models import Account, Transaction, CreditCard, User, CryptoCurrency
bcrypt = Bcrypt()

basedir = os.path.abspath(os.path.dirname(__file__))


class ApplicationConfig:
    SECRET_KEY = 'unhSADAdDh9'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        basedir, "database.db"
    )

