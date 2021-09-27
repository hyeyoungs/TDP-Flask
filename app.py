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
<<<<<<< Updated upstream
=======
<<<<<<< Updated upstream
=======
client = MongoClient('mongodb://test:test@localhost', 27017)
db = client.dbsparta_plus_week2

<<<<<<< Updated upstream
<<<<<<< Updated upstream
@app.route('/')
def home():
    return render_template('index.html')


>>>>>>> Stashed changes
=======

client = MongoClient('mongodb://test:test@localhost', 27017)
db = client.dbsparta_plus_week2

=======
>>>>>>> Stashed changes
@app.route('/write_til', methods=['POST'])
=======
@app.route('/til_board', methods=['POST'])
>>>>>>> Stashed changes
def delete_til():
    til_no = request.form['til_no']
    db.til.delete_one({'til_no': til_no})
    return jsonify({'msg': '삭제 완료!'})

<<<<<<< Updated upstream
<<<<<<< Updated upstream

@app.route('/write_til', methods=['GET','POST'])
=======
@app.route('/til_board', methods=['GET','POST'])
>>>>>>> Stashed changes
def read_til():
    til_no = request.form['til_no']
    temp = db.til.find_one({'til_no': til_no})
    return jsonify({'til': temp})

<<<<<<< Updated upstream
=======
@app.route('/write_til', methods=['GET','POST'])
def read_til():
    til_no = request.form['til_no']
    temp = db.til.find_one({'til_no': til_no})
    return jsonify({'til': temp})

>>>>>>> Stashed changes
@app.route('/write_til', methods=['GET'])
=======
@app.route('/til_board', methods=['GET'])
>>>>>>> Stashed changes
def all_til():
    temp = list(db.til.find({}, {'_id': False}))
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
>>>>>>> Stashed changes

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
