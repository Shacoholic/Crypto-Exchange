from app import db

class CreditCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    credit_card_holder_name = db.Column(db.String(200))
    credit_card_number = db.Column(db.String(200))
    expiration_date = db.Column(db.DateTime)
    cvv = db.Column(db.String(200))
    money_amount = db.Column(db.Float)