from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from werkzeug.utils import secure_filename
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
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        user_info = db.user.find_one({"user_id": payload["id"]}, {"_id": False})
        return render_template('mytil_page.html', user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/create_page')
def create_page():
    return render_template('create.html')


@app.route('/main_page')
def home():
    global flag
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        user_info = db.user.find_one({"user_id": payload["id"]}, {"_id": False})
        print(payload['id'])
        print(user_info)
        print("여기")
        til_state = list(db.til.find({"til_user": payload["id"]}, {"til_day": 1, "_id": False}))
        print(til_state)
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        for doc in til_state:
            old_day = doc['til_day'].strftime('%Y-%m-%d')
            print(old_day)
            if today == old_day:
                flag = 1
                break
            else:
                flag = 0
        print(flag)
        return render_template('home.html', user_info=user_info, flag=flag)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/til_board')
def list_page():
    return render_template('til_board.html')


@app.route('/detail')
def detail_page():
    title = request.args.get("title")
    content = db.til.find_one({'til_title': title}, {'_id': False})
    return render_template('detail.html', content=content)


@app.route('/my_page')
def my_page():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        user_info = db.user.find_one({"user_id": payload["id"]}, {"_id": False})
        print(payload['id'])
        print(user_info)
        return render_template('my_page.html', user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/til/board', methods=['GET'])
def read_all_til():
    temp = list(db.til.find({}, {'_id': False}))
    til_count = db.til.count()
    return jsonify({'result': "success", 'all_til': temp, "til_count": til_count})


@app.route('/til/user', methods=['POST'])
def read_user_til():
    til_user_receive = request.form['til_user_give']
    my_til = list(db.til.find({'til_user': til_user_receive}, {'_id': False}).sort('_id', -1))
    return jsonify({'result': 'success', 'my_til': my_til})


@app.route('/til/rank', methods=['GET'])
def rank_til():
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
    return jsonify({'result': "success", 'til_rank': agg_result})


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
def read_til():
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


@app.route('/user', methods=['POST'])
def create_user():
    user_id = request.form['user_id_give']
    user_password = request.form['user_pw_give']
    user_nickname = request.form['user_nickname_give']

    pw_hash = hashlib.sha256(user_password.encode('utf-8')).hexdigest()
    doc = {'user_id': user_id, 'user_password': pw_hash, 'user_nickname': user_nickname, 'github_id': '', 'user_profile_pic': '', 'user_profile_pic_real': 'profile_pics/profile_placeholder.png', 'user_profile_info': ''}

    db.user.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/login', methods=['POST'])
def login():
    user_id_receive = request.form['user_id_give']
    user_pw_receive = request.form['user_pw_give']
    pw_hash = hashlib.sha256(user_pw_receive.encode('utf-8')).hexdigest()
    result = db.user.find_one({'user_id': user_id_receive, 'user_password': pw_hash})
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
        print(payload['id'])

        userinfo = db.user.find_one({'user_id': payload['id']}, {'_id': 0})
        print(userinfo)

        return jsonify({'result': 'success', 'id': userinfo['user_id']})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})


@app.route('/check_dup', methods=['POST'])
def check_dup():
    user_id_receive = request.form['user_id_give']
    exists = bool(db.user.find_one({"id": user_id_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/update_profile', methods=['POST'])
def save_img():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_id = payload["id"]
        name_receive = request.form["nickname_give"]
        github_id_receive = request.form["github_id_give"]
        about_receive = request.form["about_give"]
        new_doc = {
            "user_nickname": name_receive,
            "github_id": github_id_receive,
            "user_profile_info": about_receive
        }
        if 'file_give' in request.files:
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"profile_pics/{user_id}.{extension}"
            file.save("./static/" + file_path)
            new_doc["user_profile_pic"] = filename
            new_doc["user_profile_pic_real"] = file_path
        print(new_doc)
        db.user.update_one({'user_id': user_id}, {'$set': new_doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

