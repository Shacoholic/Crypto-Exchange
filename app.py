from flask import Flask, jsonify, request, Response, session
from configuration import db, bcrypt, ApplicationConfig
from models.user import User

app = Flask(__name__)
app.config.from_object(ApplicationConfig)
db.init_app(app)
bcrypt.init_app(app)


@app.route('/createDB')
def createDB():
    db.create_all()
    return 'DB created!'

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



if __name__ == '__main__':
    app.run()
