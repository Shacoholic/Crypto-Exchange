from configuration import db
from datetime import datetime


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    crypto_currencies = db.relationship("CryptoCurrency", backref="account")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class CreditCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    credit_card_holder_name = db.Column(db.String(200))
    credit_card_number = db.Column(db.String(200))
    expiration_date = db.Column(db.String(200))
    cvv = db.Column(db.String(200))
    money_amount = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class CryptoCurrency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crypto_currency_amount = db.Column(db.Float)
    crypto_currency_name = db.Column(db.String(200))
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"))


class Transaction(db.Model):
    hashID = db.Column(db.String(256), primary_key=True)
    sender = db.Column(db.String(100))
    recipient = db.Column(db.String(100))
    amount = db.Column(db.Float)
    cryptocurrency = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    address = db.Column(db.String(100))
    password = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(100))
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    verified = db.Column(db.Boolean())
    credit_card = db.relationship("CreditCard", backref="user", uselist=False)
    account = db.relationship("Account", backref="user", uselist=False)
    transactions = db.relationship("Transaction", backref="user")


