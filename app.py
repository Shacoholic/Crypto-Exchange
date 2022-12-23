from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


app = Flask(__name__)
app.secret_key = 'unhSADAdDh9'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db: SQLAlchemy = SQLAlchemy(app)

bcrypt = Bcrypt(app)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/register', methods=["POST"])#moramo doraditi poziv kad se dogovorimo za frontend
def register():
    firstName = request.json["firstName"]
    lastName = request.json["lastName"]
    address = request.json["address"]
    city = request.json["city"]
    country = request.json["country"]
    phone = request.json["phone"]
    email = request.json["email"]
    password = request.json["password"]

    hash_password = bcrypt.generate_password_hash(password).decode('utf8')

    #trebam dodati provjeru da li postoji korisnik kad odradimo bazu i ubaciti ga ako postoji i vratiti kod

@app.route('/login', methods=["POST"])
def login():
    email = request.json["email"]
    password = request.json["password"]
    #odradicu kad bazu zavrsimo


@app.route('/logout', methods=["POST"])
def logout():
    return #todo


if __name__ == '__main__':
    app.run()
