from app import db

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)