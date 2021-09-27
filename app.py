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

<<<<<<< Updated upstream
=======
<<<<<<< Updated upstream
=======
client = MongoClient('mongodb://test:test@localhost', 27017)
db = client.dbsparta_plus_week2

@app.route('/')
def home():
    return render_template('index.html')


>>>>>>> Stashed changes
@app.route('/write_til', methods=['POST'])
def delete_til():
    til_no = request.form['til_no']
    db.til.delete_one({'til_no': til_no})
    return jsonify({'msg': '삭제 완료!'})

@app.route('/write_til', methods=['GET','POST'])
def read_til():
    til_no = request.form['til_no']
    temp = db.til.find_one({'til_no': til_no})
    return jsonify({'til': temp})

@app.route('/write_til', methods=['GET'])
def all_til():
    temp = list(db.til.find({}, {'_id': False}))
    return jsonify({'result':'success'}, {'all_til': temp})
<<<<<<< Updated upstream
=======







>>>>>>> Stashed changes


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
