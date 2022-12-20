from app import db

class CryptoCurrency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crypto_currency_amount = db.Column(db.Float)
    crypto_currency_name = db.Column(db.String(200))