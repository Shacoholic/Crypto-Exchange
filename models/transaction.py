from app import db


class Transaction(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    sender = db.Column(db.String(100))
    recipient = db.Column(db.String(100))
    state = db.Column(db.String(100))
    amount = db.Column(db.Float)
    crypto_currency = db.Column(db.String(100))