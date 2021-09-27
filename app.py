from flask import Flask, render_template, jsonify, request
from datetime import datetime
from pymongo import MongoClient

app = Flask(__name__)

# pc 용 :
client = MongoClient('localhost', 27017)
db = client.tdp

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

@app.route('/create')
def create_page():
    return render_template('create.html')

@app.route('/til_board', methods=['POST'])
def delete_til():
    til_no_receive = request.form['til_no_give']
    db.tdp.delete_one({'til_no': til_no_receive})
    return jsonify({'msg': '삭제 완료!'})

@app.route('/til_board', methods=['GET','POST'])
def read_til():
    til_no_receive = request.form['til_no_give']
    temp = db.tdp.find_one({'til_no': til_no_receive})
    return jsonify({'til': temp})

@app.route('/til_board', methods=['GET'])
def all_til():
    temp = list(db.tdp.find({}, {'_id': False}))
    return jsonify({'result':'success'}, {'all_til': temp})


@app.route('/api/update', methods=['POST'])
def api_update():
    til_no_receive = request.form['til_no_give']
    til_title_receive = request.form['til_title_give']
    til_content_receive = request.form['til_content_give']
    current_time = datetime.now()
    
    doc = {'til_title' : til_title_receive, 'til_content' : til_content_receive, 'til_update_day' : current_time}
    db.til.update_one({'til_no': til_no_receive}, doc)
    return jsonify({'msg': '수정 완료!'})

@app.route('/api/create', methods=['POST'])
def api_create():
    til_user_receive = request.form['til_user_give']
    til_title_receive = request.form['til_title_give']
    til_content_receive = request.form['til_content_give']
    current_time = datetime.now()
    
    doc = {'til_title': til_title_receive, 'til_user': til_user_receive, 'til_content': til_content_receive, 'til_day': current_time}
    db.til.insert_one(doc)
    return jsonify({'msg': 'til 작성 완료!'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
