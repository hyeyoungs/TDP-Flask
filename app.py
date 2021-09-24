from flask import Flask, render_template, jsonify, request
from datetime import datetime
from pymongo import MongoClient

app = Flask(__name__)

# pc 용 :
client = MongoClient('localhost', 27017)

@app.route('/')
def main_page():
    return render_template('main_page.html')

@app.route('/signup_page')
def signup_page():
    return render_template('signup_page.html')

@app.route('/my_page')
def my_page():
    return render_template('my_page.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/delete', methods=['POST'])
def delete_til():
    til_id = request.form['til_id']
    db.til.delete_one({'_id': til_id})
    return jsonify({'msg': '삭제 완료!'})

@app.route('/', methods=['GET'])
def show_til():
    temp = list(db.til.find({}, {'_id': False}))
    return jsonify({'tils': temp})



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
