from flask import Flask, jsonify, request, Response, session
from configuration import db, bcrypt, ApplicationConfig
from models.models import User, Account, Transaction, CryptoCurrency, CreditCard
from flask_session import Session
import random

app = Flask(__name__)
app.config.from_object(ApplicationConfig)
db.init_app(app)
bcrypt.init_app(app)
Session(app)


@app.route('/createDB')
def createDB():
    db.create_all()
    return 'DB created!'

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

#posle kreiranja crypto accounta mora da se izvrsi verifikacija
@app.route('/verification', methods=["POST"])
def verification():
    number = request.json["number"]
    first_name = request.json["first_name"]
    expiration_date = request.json["expiration_date"]
    security_code = request.json["security_code"]
    user_id = session.get("user_id")
    user = User.query.get(user_id)


    if(user.verified == False and number == 4242424242424242 and first_name == user.first_name and expiration_date == "02/23" and security_code == 123):
        money_amount = random.randint(1000, 3000)
        money_amount -= 1
        credit_card = CreditCard(credit_card_holder_name = user.first_name,
                                   money_amount=money_amount,
                                   user=user)
        user.verified = True
        db.session.add(credit_card)
        db.session.commit()
        create_crypto_account(user)

        return "verified", 200
    else:
        return "already verified", 200


#posle ovoga moze da uplatni sredstva na online racun - posebna stranica i metoda
def create_crypto_account(user):
    account = Account(amount=0,
                                   crypto_currencies=[],
                                   user_id=user.id,
                                   user=user)

    db.session.add(account)
    db.session.commit()
    return

#prebacivanje novca na crypto racun
@app.route('/transfer_money_to_account', methods=["POST"])
def transfer_money_to_account():
    amount = request.json["amount"]
    user_id = session.get("user_id")
    user = User.query.get(user_id)

    if(user.credit_card.money_amount >= amount):
        user.credit_card.money_amount -= amount
        user.account.amount += amount
        db.session.commit()
        return "money successfully transferred", 200
    else:
        return jsonify({"error": "Not enough money on a card"})


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

    exists = User.query.filter_by(email=email).first() is not None
    if exists == True:
        return jsonify({"error": "That email is already in use"}), 409

    user = User()
    user.first_name = firstName
    user.last_name = lastName
    user.address = address
    user.city = city
    user.country = country
    user.phone = phone
    user.email = email
    user.password = hash_password
    user.verified = False

    db.session.add(user)
    db.session.commit()

    return Response(status=200)


@app.route("/login", methods=["POST"])
def login():
    email = request.json["email"]
    password = request.json["password"]

    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({"error": "Unauthorized"})

    if not bcrypt.check_password_hash(user.password, password):
        return  jsonify({"error":"Unauthorized"})
    session["user_id"] = user.id

    #dodata linija za verifikaciju koji oni moraju hendlovati na frontendu, stranica za unos kreditne kartice
    if user.verified == False:
        return jsonify({"error": "Not Verified"})

    return Response(status=200)

@app.route("/logout", methods=["POST"])
def logout():

    session.pop("user_id", None)
    return  Response(status=200)

@app.route("/changeUserData", methods=["PUT"])
def change_user_data():
    id = session.get("user_id")

    user = User.query.get(id)

    user.first_name = request.json["firstName"]
    user.last_name = request.json["lastName"]
    user.address = request.json["address"]
    user.city = request.json["city"]
    user.country = request.json["country"]
    user.phone = request.json["phone"]
    user.email = request.json["email"]
    user.password = request.json["password"]

    email_exists = User.query.filter_by(email=user.email).count()
    user.password = bcrypt.generate_password_hash(user.password)

    if email_exists > 1:
        return jsonify({"error":"Email already in use"}), 409

    db.session.commit()
    return Response(status=200)

@app.route("/check_session_working")
def check_session_working():
    user_id = session.get("user_id")
    return jsonify({"user_id": user_id})

# 4. Pregled stanja
@app.route("/status_account_check")
def status_account_check():
    user_id = session.get("user_id")
    user = User.query.get(user_id)
    crypto_acc = user.account
    return jsonify({"amount": crypto_acc.amount})

if __name__ == '__main__':
    app.run()
