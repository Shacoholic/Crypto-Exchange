from configuration import db, mm
from marshmallow import Schema, fields


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
    verified = db.Column(db.Boolean, default="false")

    class UserSchema(mm.Schema):
        id = fields.Number()
        first_name = fields.Str()
        last_name = fields.Str()
        address = fields.Str()
        password = fields.Str()
        email = fields.Str()
        phone = fields.Str()
        country = fields.Str()
        city = fields.Str()