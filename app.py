from flask import Flask, render_template, jsonify, request
from datetime import datetime
from pymongo import MongoClient

app = Flask(__name__)

# pc 용 :
client = MongoClient('localhost', 27017)
db = client.til

@app.route('/')
def main_page():
    return render_template('home.html')

@app.route('/signup_page')
def signup_page():
    return render_template('signup_page.html')

@app.route('/my_page')
def my_page():
    return render_template('my_page.html')

@app.route('/create_page')
def create_page():
    return render_template('create.html')

@app.route('/til_board')
def til_board():
    return render_template('til_board.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/api/delete', methods=['POST'])
def api_delete():
    til_no_receive = request.form['til_no_give']
    db.til.delete_one({'til_no': til_no_receive})
    return jsonify({'msg': '삭제 완료!'})

@app.route('/api/read', methods=['GET','POST'])
def api_read():
    til_no_receive = request.form['til_no_give']
    temp = db.til.find_one({'til_no': til_no_receive})
    return jsonify({'til': temp})

@app.route('/til_board')
def listing_page():
    return render_template('til_board.html')

# @app.route('/til_board', methods=['POST'])
# def delete_til():
#     til_id_receive = request.form['til_id_give']
#     db.til.delete_one({'_id': til_id_receive})
#     return jsonify({'msg': '삭제 완료!'})

@app.route('/til_board', methods=['POST'])
def read_til_detail():
    til_id_receive = request.form['til_title']
    temp = list(db.til.find({'til_title': til_id_receive}, {'_id': False}))
    return jsonify({'result': "success", 'til': temp})

@app.route('/til_board_listing', methods=['GET'])
def all_til():
    temp = list(db.til.find({}, {'_id': False}))
    return jsonify({'result': "success", 'all_til': temp})

@app.route('/api/update', methods=['POST'])
def api_update():
    til_id_receive = request.form['til_id_give']
    til_title_receive = request.form['til_title_give']
    til_content_receive = request.form['til_content_give']
    current_time = datetime.now()

    doc = {'til_title': til_title_receive, 'til_content': til_content_receive, 'til_update_day': current_time}
    db.til.update_one({'_id': til_id_receive}, doc)
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