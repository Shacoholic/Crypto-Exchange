from flask import Flask, jsonify, request, Response, session, redirect, url_for
from configuration import db, bcrypt, ApplicationConfig
from models.models import User, Account, Transaction, CryptoCurrency, CreditCard
from flask_session import Session
from urllib.parse import urlencode
import glob
import os
import random
import requests
import json

app = Flask(__name__)
app.config.from_object(ApplicationConfig)
db.init_app(app)
bcrypt.init_app(app)
Session(app)

@app.route('/')
def hello_world():
    return 'Hello world'

@app.route('/createDB')
def createDB():
    db.create_all()
    return 'DB created!'

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
    if(buying == "USD"):
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

#posle kreiranja crypto accounta mora da se izvrsi verifikacija
@app.route('/verification', methods=["POST"])
def verification():
    number = request.form["Card"]
    first_name = request.form["Name"]
    expiration_date = request.form["Date"]
    security_code = request.form["Code"]
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

        return redirect('http://127.0.0.1:5002/', code=307)
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


@app.route('/register', methods=['POST', 'GET'])#moramo doraditi poziv kad se dogovorimo za frontend
def register():
    firstName = request.form["Name"]
    lastName = request.form["Surname"]
    address = request.form["Adress"]
    city = request.form["City"]
    country = request.form["Country"]
    phone = request.form["Phone"]
    email = request.form["email"]
    password = request.form["pass"]

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

    return redirect('http://127.0.0.1:5002/verify', code=307)

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["pass"]

    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({"error": "Unauthorized"})

    if not bcrypt.check_password_hash(user.password, password):
        return  jsonify({"error":"Unauthorized"})
    session["user_id"] = user.id
    #dodata linija za verifikaciju koji oni moraju hendlovati na frontendu, stranica za unos kreditne kartice
   # if user.verified == False:
     #   return redirect('http://127.0.0.1:5002/verify', code=307)

    return redirect('http://127.0.0.1:5002/home', code=307)

@app.route("/logout", methods=["POST"])
def logout():

    session.pop("user_id", None)
    return redirect('http://127.0.0.1:5002/', code=307)

@app.route('/getCurrentUser', methods=['GET', 'POST'])
def getCurrentUser():

    id = session.get("user_id")
    user = User.query.get(id)

    path = r"C:\Users\Nebojsa\Documents\GitHub\Crypto-Exchange\templates\Files" + "\\" + user.email
    image = ""
    if os.path.exists(path):
        for file in os.listdir(path):
            image = file
            break

    filename = os.path.basename(image)
    imagepath = user.email + "\\" + filename

    dicti = {
        "Name": user.first_name,
        "Surname": user.last_name,
        "Country": user.country,
        "City": user.city,
        "Address": user.address,
        "PhoneNumber": user.phone,
        "Image": imagepath
    }

    redirect_baseUrl = "http://127.0.0.1:5002/profile"
    redirect_url = redirect_baseUrl + ("?" + urlencode(dicti) if dicti else "")
    return redirect(redirect_url)

@app.route("/changeUserData", methods=["PUT", "GET", "POST"])
def change_user_data():

    id = session.get("user_id")

    user = User.query.get(id)

    user.first_name = request.form["Name"]
    user.last_name = request.form["Surname"]
    user.address = request.form["Adress"]
    user.city = request.form["City"]
    user.country = request.form["Country"]
    user.phone = request.form["Phone"]

    db.session.commit()

    image = request.files['image']
    newpath = r'C:\Users\Nebojsa\Documents\GitHub\Crypto-Exchange\\templates\Files' + '\\' + user.email
    if not os.path.exists(newpath):
        os.makedirs(newpath)

    path = newpath + '\\*'
    files = glob.glob(path)
    for f in files:
        os.remove(f)

    image.save(os.path.join(newpath + '\\' + image.filename))

    return redirect('http://127.0.0.1:5002/home', code=307)

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
    return redirect("")

if __name__ == '__main__':
    app.run(port=5000)
