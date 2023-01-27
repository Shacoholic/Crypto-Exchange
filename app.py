import _thread
import time
from multiprocessing import Process
from queue import Queue

import sqlalchemy
from flask import Flask, jsonify, request, Response, session
from configuration import db, bcrypt, ApplicationConfig
from models import StateEnum
from models.models import User, Account, Transaction, CryptoCurrency, CreditCard
from flask_session import Session
import _sha3
import random
import requests
import json

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


@app.route("/showCryptoCurrencies")
def showCryptoCurrencies():
    header = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": "4ceb685b-2766-45cc-8127-147c64386639"
    }

    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    s = requests.Session()
    s.headers.update(header)
    response = s.get(url)
    json_response = response.json()
    cryptolist = json.dumps(addingToList(json_response["data"]))
    return cryptolist, 200


@app.route("/exchange", methods=["PATCH"])
def exchange():
    selling = request.json["selling"]
    buying = request.json["buying"]
    amount = request.json["amount"]
    user_id = session.get("user_id")
    user = User.query.get(user_id)
    account = user.account

    price = gettingPrice(selling, buying)

    paying_sum = price * amount

    if selling == "USD":
        if paying_sum > account.amount:
            return jsonify({"error": "Not enough money on account"})
        account.amount -= paying_sum
        crypto_currencies = account.crypto_currencies
        iterator = filter(lambda x: x.crypto_currency_name == buying, crypto_currencies)

        crypto_currencies = list(iterator)
        if crypto_currencies == []:
            newCryptoCurrency(buying, amount, account)
        else:
            cryptoCurrencyUpdate(buying, amount, crypto_currencies)
    elif buying == "USD":
        crypto_currencies = account.crypto_currencies
        crypto_currency = next(
            filter(lambda x: x.crypto_currency_name == selling, crypto_currencies), None)

        if crypto_currency == None:
            return jsonify({"error": "You dont have this crypto"})

        if paying_sum > crypto_currency.crypto_currency_amount:
            return jsonify({"error": "You dont have enough crypto"})
        crypto_currency.crypto_currency_amount -= paying_sum
        account.amount += amount
        db.session.commit()
    else:
        crypto_currencies = account.crypto_currencies
        crypto_currency = next(
            filter(lambda x: x.crypto_currency_name == selling, crypto_currencies), None)

        if crypto_currency == None:
            return jsonify({"error": "You dont have this crypto"})

        if paying_sum > crypto_currency.crypto_currency_amount:
            return jsonify({"error": "You dont have enough crypto"})
        crypto_currency.crypto_currency_amount -= paying_sum
        crypto_currencies = account.crypto_currencies
        iterator = filter(lambda x: x.crypto_currency_name == buying, crypto_currencies)
        crypto_currencies = list(iterator)
        if crypto_currencies == []:
            newCryptoCurrency(buying, amount, account)
        else:
            cryptoCurrencyUpdate(buying, amount, crypto_currencies)

    return Response(status=200)


def gettingPrice(selling, buying):
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    if (buying == "USD"):
        parameters = {"symbol": selling, "convert": buying}
    else:
        parameters = {"symbol": buying, "convert": selling}

    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": "4ceb685b-2766-45cc-8127-147c64386639"
    }
    sess = requests.Session()
    sess.headers.update(headers)
    response = sess.get(url, params=parameters)

    if (buying == "USD"):
        price = response.json()["data"][selling]["quote"][buying]["price"]
        price = 1 / price
    else:
        price = response.json()["data"][buying]["quote"][selling]["price"]

    return price


def cryptoCurrencyUpdate(crypto_currency_name, crypto_currency_amount, crypto_currencies):
    crypto_currency = next(filter(lambda x: x.crypto_currency_name == crypto_currency_name, crypto_currencies),
                           None)
    crypto_currency.crypto_currency_amount += crypto_currency_amount
    db.session.commit()
    return


def newCryptoCurrency(crypto_currency_name, crypto_currency_amount, crypto_account):
    crypto_currency = CryptoCurrency(crypto_currency_amount=crypto_currency_amount,
                                     crypto_currency_name=crypto_currency_name,
                                     account_id=crypto_account.id)
    db.session.add(crypto_currency)
    db.session.commit()
    return


def addingToList(data):
    crypto_value_list = []
    for crypto in data:
        symbol = str(crypto["symbol"])
        name = str(crypto["name"])
        price = crypto["quote"]["USD"]["price"]
        crypto_value_list.append({
            "name": name,
            "symbol": symbol,
            "price": price
        })
    return crypto_value_list


# posle kreiranja crypto accounta mora da se izvrsi verifikacija
@app.route('/verification', methods=["POST"])
def verification():
    number = request.json["number"]
    first_name = request.json["first_name"]
    expiration_date = request.json["expiration_date"]
    security_code = request.json["security_code"]
    user_id = session.get("user_id")
    user = User.query.get(user_id)

    if (
            user.verified == False and number == 4242424242424242 and first_name == user.first_name and expiration_date == "02/23" and security_code == 123):
        money_amount = random.randint(1000, 3000)
        money_amount -= 1
        credit_card = CreditCard(credit_card_holder_name=user.first_name,
                                 money_amount=money_amount,
                                 user=user)
        user.verified = True
        db.session.add(credit_card)
        db.session.commit()
        create_crypto_account(user)

        return "verified", 200
    else:
        return "already verified", 200


# posle ovoga moze da uplatni sredstva na online racun - posebna stranica i metoda
def create_crypto_account(user):
    account = Account(amount=0,
                      crypto_currencies=[],
                      user_id=user.id,
                      user=user)

    db.session.add(account)
    db.session.commit()
    return


# prebacivanje novca na crypto racun
@app.route('/transfer_money_to_account', methods=["POST"])
def transfer_money_to_account():
    amount = request.json["amount"]
    user_id = session.get("user_id")
    user = User.query.get(user_id)

    if (user.credit_card.money_amount >= amount):
        user.credit_card.money_amount -= amount
        user.account.amount += amount
        db.session.commit()
        return "money successfully transferred", 200
    else:
        return jsonify({"error": "Not enough money on a card"})


def mining(transaction_id, crypto_currency, amount, q):
    time.sleep(5*60)

    engine = sqlalchemy.create_engine(
        'mysql+mysqlconnector://root:1234@db/mysql_db'
    )
    local_session = sqlalchemy.orm.Session(bind=engine)
    transaction = local_session.query(Transaction).get(transaction_id)
    user = local_session.query(User).filter_by(email=transaction.recipient).first()
    account = user.account
    currencies = account.crypto_currencies
    filtered = filter(lambda a: a.name == crypto_currency, currencies)
    currencies = list(filtered)

    if currencies == []:
        currency = CryptoCurrency(crypto_currency_amount=amount, crypto_currency_name=crypto_currency, account_id=account.id)
        local_session.add(currency)
        local_session.commit()
    else:
        currency = next(
            filter(lambda a: a.name == crypto_currency, currencies), None)
        currency.amount = currency.amount + amount

        if currency.amount < 0:
            return {"Insufficient funds"}
        local_session.commit

        transaction.state = StateEnum.PROCESSED.value
        local_session.commit()
        q.put("processed")


def announce(q1, q2):
    q1.get()
    q2.put("processed")


@app.route("/transactionState", methods=["PATCH"])
def transaction_state():
    trans_id = request.json["id"]
    state = request.json["state"]
    user_id = session.get("user_id")
    transaction = Transaction.query.get(trans_id)
    crypto_account = User.query.filter_by(email=transaction.sender).first().crypto_account
    q1 = Queue()
    q2 = Queue()

    if StateEnum[state].value == "PROCESSING":
        transaction.state = StateEnum.PROCESSING.value
        db.session.commit()
        cryptoCurrencyUpdate(transaction.cryptocurrency, transaction.amount, crypto_account)
        _thread.start_new_thread(announce, (q1, q2))
        process = Process(target=mining,
                          args=(user_id, trans_id, transaction.cryptocurrency,
                                transaction.amount, q1))
        process.start()
        q2.get()
    else:
        transaction.state = Transaction.REJECTED.value
        db.session.commit()

    return Response(status=200)


@app.route("/startTransaction", methods=["POST"])
def start_transaction():
    recipient_email = request.json["recipient"]
    amount = int(request.json["transferAmount"])
    currency = request.json["currencyTransfer"]
    user_exists = User.query.filter_by(email=recipient_email).first()
    if user_exists is None:
        return {"error": "There is no user with chosen email"}
    else:
        id = session.get("user_id")
        user = User.query.get(id)
        currencies = user.account.crypto_currencies
        balances = filter(lambda  a: a.name == currency and a.amount, currencies)
        balances = list(balances)
        if balances == []:
            return {"error": "Not enough funds"}
        sha3 = _sha3.sha3_256()
        new_string = "" + user.email + recipient_email + \
            str(amount) + str(random.Random().randint(0, 1000))
        sha3.update(new_string.encode())
        transaction = Transaction(
            hashID = sha3.hexdigest(),
            id=user.id,
            sender=user.email,
            recipient=recipient_email,
            amount=amount,
            crypto_currency=currency,
        )
        db.session.add(transaction)
        db.session.commit()
        return Response(status=200)


@app.route("/allTransactions")
def all_transactions():
    user_id = session.get("user_id")
    user = User.query.get(user_id)
    transactions = Transaction.query.all()
    filtered = filter(
        lambda a: (a.sender == user.email or a.recipient == user.email), transactions
    )
    transactions = list(filtered)
    return jsonify(transactions)


@app.route('/register', methods=["POST"])
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
        return jsonify({"error": "Unauthorized"})
    session["user_id"] = user.id

    # dodata linija za verifikaciju koji oni moraju hendlovati na frontendu, stranica za unos kreditne kartice
    if user.verified == False:
        return jsonify({"error": "Not Verified"})

    return Response(status=200)


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return Response(status=200)


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
        return jsonify({"error": "Email already in use"}), 409

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
