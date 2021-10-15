from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

# pc 용 :
client = MongoClient('localhost', 27017)
db = client.tdp

SECRET_KEY = 'CodingDeserterPursuit'

import jwt
import datetime
import hashlib


# 위아래 두칸씩 벌려야함


@app.route('/')
def login_page():
    return render_template('login_page.html')


@app.route('/main_page', methods=['GET'])
def main_page():
    api_valid()
    return render_template('home.html')


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
def listing_page():
    return render_template('til_board.html')


@app.route('/detail')
def detail_page():
    title = request.args.get("title")
    content = db.til.find_one({'til_title': title}, {'_id': False})
    return render_template('detail.html', content=content)


# @app.route('/til_board', methods=['POST'])
# def delete_til():
#     til_id_receive = request.form['til_id_give']
#     db.til.delete_one({'_id': til_id_receive})
#     return jsonify({'msg': '삭제 완료!'})


@app.route('/til_board', methods=['POST'])
def read_til():
    til_title_receive = request.form['til_title']
    temp = list(db.til.find({'til_title': til_title_receive}, {'_id': False}))
    return jsonify({'til': temp})


@app.route('/til_board_listing', methods=['GET'])
def all_til():
    temp = list(db.til.find({}, {'_id': False}))
    return jsonify({'result': "success", 'all_til': temp})


@app.route('/api/list_myTIL', methods=['POST'])
def read_my_til():  # pep8에러 함수이름
    til_user_receive = request.form['til_user_give']
    my_til = list(db.til.find({'til_user': til_user_receive}).sort('_id', -1))
    for doc in my_til:
        doc["_id"] = str(doc["_id"])
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


@app.route('/api/create', methods=['POST'])
def api_create():
    til_user_receive = request.form['til_user_give']
    til_title_receive = request.form['til_title_give']
    til_content_receive = request.form['til_content_give']
    current_time = datetime.now()

    doc = {'til_title': til_title_receive, 'til_user': til_user_receive, 'til_content': til_content_receive,
           'til_day': current_time, 'til_view': True}
    db.til.insert_one(doc)
    return jsonify({'msg': 'til 작성 완료!'})


@app.route('/api/delete', methods=['POST'])
def api_delete():
    til_id_receive = request.form['til_id_give']
    db.til.delete_one({'_id': ObjectId(til_id_receive)})
    return jsonify({'msg': 'til 삭제 완료!'})


@app.route('/api/update', methods=['POST'])
def api_update():
    til_id_receive = request.form['til_id_give']
    til_title_receive = request.form['til_title_give']
    til_content_receive = request.form['til_content_give']
    current_time = datetime.now()

    doc = {"$set": {'til_title': til_title_receive, 'til_content': til_content_receive, 'til_update_day': current_time}}
    db.til.update_one({'_id': ObjectId(til_id_receive)}, doc)
    return jsonify({'msg': '수정 완료!'})


@app.route('/api/update/view', methods=['POST'])
def api_update_view():
    til_id_receive = request.form['til_id_give']
    til_view = db.til.find_one({'_id': ObjectId(til_id_receive)}, {"_id": 0, "til_view": 1})
    view_value = til_view["til_view"]
    if not isinstance(view_value, bool):
        msg = '공개 여부의 값이 정확하지 않습니다.'
    else:
        doc = {"$set": {'til_view': not (view_value)}}
        db.til.update_one({'_id': ObjectId(til_id_receive)}, doc)

    msg = '변경 완료!'
    return jsonify({'msg': msg})


@app.route('/users', methods=['POST'])
def create_user():
    user_id = request.form['user_id_give']
    user_password = request.form['user_pw_give']
    user_nickname = request.form['user_nickname_give']

    pw_hash = hashlib.sha256(user_password.encode('utf-8')).hexdigest()
    # header /payload(이부분)/ signature
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
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * 1)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        # header /payload/ signature(이부분)을 발급 -> header로 전달
        print(token)
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

        return jsonify({'result': 'success', 'id': userinfo['id']})
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
