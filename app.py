from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

# pc 용 :
client = MongoClient('localhost', 27017)
db = client.tdp


SECRET_KEY = 'CodingDeserterPursuit'

import jwt
import datetime
import hashlib


@app.route('/')
def login_page():
    return render_template('login_page.html')


@app.route('/signup_page')
def signup_page():
    return render_template('signup_page.html')


@app.route('/mytil_page')
def mytil_page():
    return render_template('mytil_page.html')


@app.route('/create_page')
def create_page():
    return render_template('create.html')


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/til_board')
def list_page():
    return render_template('til_board.html')


@app.route('/detail')
def detail_page():
    title = request.args.get("title")
    content = db.til.find_one({'til_title': title}, {'_id': False})
    return render_template('detail.html', content=content)


@app.route('/til_board_listing', methods=['GET'])
def all_til():
    temp = list(db.til.find({}, {'_id': False}))
    return jsonify({'result': "success", 'all_til': temp})


@app.route('/user/til', methods=['POST'])
def read_my_til():
    til_user_receive = request.form['til_user_give']
    my_til = list(db.til.find({'til_user': til_user_receive}, {'_id': False}).sort('_id', -1))
    return jsonify({'result': 'success', 'my_til': my_til})


@app.route('/home_listing', methods=['GET'])
def home_til():
    temp = list(db.til.find({}, {'_id': False}).sort("_id", -1))
    return jsonify({'result': "success", 'home_til': temp})


@app.route('/home_ranking', methods=['GET'])
def home_ranking():
    agg_result = list(db.til.aggregate([
        {"$group":
            {
                "_id": "$til_user",
                "til_score": {"$sum": 1}
            }
        },
        {"$sort":
             {'til_score': -1}
         }
    ]))
    return jsonify({'result': "success", 'home_til': agg_result})


@app.route('/til', methods=['POST'])
def create_til():
    til_user_receive = request.form['til_user_give']
    til_title_receive = request.form['til_title_give']
    til_content_receive = request.form['til_content_give']
    til_count = db.til.count()
    if til_count == 0:
        max_value = 1
    else:
        max_value = db.til.find_one(sort=[("til_idx", -1)])['til_idx'] + 1
    db.til.count()
    doc = {'til_idx': max_value, 'til_title': til_title_receive, 'til_user': til_user_receive, 'til_content': til_content_receive,
           'til_day': datetime.datetime.now(), 'til_view': True}
    db.til.insert_one(doc)
    return jsonify({'msg': 'til 작성 완료!'})

@app.route('/til', methods=['GET'])
def get_post():
    idx = request.args['idx']
    doc = db.til.find_one({'til_idx': int(idx)}, {'_id': False})
    return jsonify({"til": doc})

@app.route('/til/<idx>', methods=['DELETE'])
def delete_til(idx):
    db.til.delete_one({'til_idx': int(idx)})
    return jsonify({'msg': 'til 삭제 완료!'})


@app.route('/til/<idx>', methods=['PUT'])
def update_til(idx):
    til_title_receive = request.form['til_title_give']
    til_content_receive = request.form['til_content_give']
    current_time = datetime.datetime.now()
    doc = {"$set": {'til_title': til_title_receive, 'til_content': til_content_receive, 'til_update_day': current_time}}
    db.til.update_one({'til_idx': int(idx)}, doc)
    return jsonify({'msg': '수정 완료!'})


@app.route('/til/view/<idx>', methods=['PUT'])
def update_view(idx):
    doc = db.til.find_one({'til_idx': int(idx)})
    view_value = doc["til_view"]

    if not isinstance(view_value, bool):
        msg = '공개 여부의 값이 정확하지 않습니다.'
    else:
        doc = {"$set": {'til_view': not (view_value)}}
        print(idx, doc)
        db.til.update_one({'til_idx': int(idx)}, doc)

    msg = '변경 완료!'
    return jsonify({'msg': msg})


@app.route('/users', methods=['POST'])
def create_user():
    user_id= request.form['user_id_give']
    user_password = request.form['user_pw_give']
    user_nickname = request.form['user_nickname_give']

    pw_hash = hashlib.sha256(user_password.encode('utf-8')).hexdigest()

    doc = {'id': user_id, 'password': pw_hash, 'nickname': user_nickname}
    db.user.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/login', methods=['POST'])
def login():
    user_id_receive = request.form['user_id_give']
    user_pw_receive = request.form['user_pw_give']

    pw_hash = hashlib.sha256(user_pw_receive.encode('utf-8')).hexdigest()

    result = db.user.find_one({'id': user_id_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': user_id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * 24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/nick', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')


    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)

        userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'nickname': userinfo['nickname']})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})


@app.route('/check_dup', methods=['POST'])
def check_dup():
    user_id_receive = request.form['user_id_give']
    exists = bool(db.user.find_one({"id": user_id_receive}))
    return jsonify({'result': 'success', 'exists': exists})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)



