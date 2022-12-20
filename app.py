from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key = 'unhSADAdDh9'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db: SQLAlchemy = SQLAlchemy(app)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
