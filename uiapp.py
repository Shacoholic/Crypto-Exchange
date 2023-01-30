import requests
from flask import Flask, render_template, request
from logging import FileHandler, WARNING

uiapp = Flask(__name__)

file_handler = FileHandler('errorlog.txt')
file_handler.setLevel(WARNING)
global amount

@uiapp.route('/', methods=['GET', 'POST'])
def main():
    return render_template('login.html')

@uiapp.route('/registerLink', methods=['GET'])
def registerLink():
    return render_template('Register.html')   

@uiapp.route('/verify', methods=['GET', 'POST'])
def verify():
    return render_template('Verify.html')

@uiapp.route('/transactions', methods=['GET'])
def transactions():
    return render_template('Transactions.html')

@uiapp.route('/home', methods=['GET', 'POST'])
def home():
    amount = request.args.get("amount")
    return render_template('Home.html', user= amount)
    
@uiapp.route('/profile', methods=['GET', 'POST'])
def profile():

    name = request.args.get("Name")
    surname = request.args.get("Surname")
    country = request.args.get("Country")
    city = request.args.get("City")
    address = request.args.get("Address")
    number = request.args.get("PhoneNumber")
    image = request.args.get("Image")

    combine = image.split('\\')
    folder = combine[0]
    file = combine[1]
    print(image)
    return render_template('Profile.html', name=name, surname=surname, country=country, city=city, address=address,
                           number=number, folder=folder, file=file)


if __name__ == '__main__':
    uiapp.run(port=5002)
