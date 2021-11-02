import boto3, os, jwt, datetime, hashlib
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from werkzeug.utils import secure_filename
from pymongo import MongoClient

app = Flask(__name__)


client = MongoClient(os.environ.get("MONGO_DB_PATH"))
db = client.tdp

SECRET_KEY = 'CodingDeserterPursuit'


@app.route('/')
@app.route('/login')
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
        return redirect(url_for("login"))


@app.route('/create_page')
def create_page():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"user_id": payload["id"]}, {"_id": False})
        return render_template('create.html', user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


@app.route('/detail')
def detail_page():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"user_id": payload["id"]}, {"_id": False})
        return render_template('detail.html', user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


@app.route('/main_page')
def home():
    flag = 0
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"user_id": payload["id"]}, {"_id": False})
        til_state = list(db.til.find({"til_user": payload["id"]}, {"til_day": 1, "_id": False}))
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        for doc in til_state:
            old_day = doc['til_day'].strftime('%Y-%m-%d')
            if today == old_day:
                flag = 1
                break
            else:
                flag = 0
        return render_template('home.html', user_info=user_info, flag=flag)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


@app.route('/til_board')
def list_page():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        user_info = db.user.find_one({"user_id": payload["id"]}, {"_id": False})
        return render_template('til_board.html', user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


@app.route('/til/comment', methods=['POST'])
def create_comment():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"user_id": payload["id"]}, {"_id": False})
        comment_receive = request.form['comment_give']
        date_receive = request.form['date_give']
        til_idx_receive = request.form['til_idx_give']
        til_idx_receive = int(til_idx_receive)
        comment_count = db.comment.count()
        if comment_count == 0:
            max_value = 1
        else:
            max_value = db.comment.find_one(sort=[("comment_idx", -1)])['comment_idx'] + 1
        doc = {
            'user_id': user_info["user_id"],
            'comment_idx': max_value,
            'til_idx': til_idx_receive,
            'til_comment': comment_receive,
            'til_comment_day': date_receive,
            'user_nickmane' : user_info["user_nickname"]
        }
        db.comment.insert_one(doc)
        msg = "댓글작성 완료"
        return jsonify({'msg': msg})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/til/comment/<idx>', methods=['GET'])
def read_comment(idx):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"user_id": payload["id"]}, {"_id": False})
        temp = list(db.comment.find({'til_idx': int(idx)}, {'_id': False, 'user_id': False}))
        print(temp)
        writer = user_info['user_nickname']
        print(writer)
        return jsonify({'comment': temp, 'writer': writer})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


@app.route('/til/comment', methods=['DELETE'])
def delete_comment():
    comment_idx_receive = request.form['comment_idx_give']
    comment_idx_receive = int(comment_idx_receive)
    db.comment.delete_one({'comment_idx': comment_idx_receive})
    return jsonify({'result': "success", 'msg': '삭제 완료'})


@app.route('/til_board_detail')
def search_detail_page():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)
        keyword = request.args.get("keyword")
        setting = request.args.get("setting")
        if setting == '제목':
            setting = 'til_title'
        elif setting == '작성자':
            setting = 'til_user'
        else:
            setting = 'til_content'
        userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})
        temp = list(db.til.find({setting: keyword}, {'_id': False}))
        return render_template("til_board_detail.html", til=temp, userinfo=userinfo)
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})


@app.route('/my_page')
def my_page():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"user_id": payload["id"]}, {"_id": False})
        return render_template('my_page.html', user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


@app.route('/til/board', methods=['GET'])
def read_all_til():
    temp = list(db.til.find({}, {'_id': False}))
    til_count = db.til.count()
    return jsonify({'result': "success", 'all_til': temp, "til_count": til_count})


@app.route('/til/user/', methods=['POST'])
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
            }},
        {"$sort":
            {
                 'til_score': -1}
         }
    ]))
    return jsonify({'result': "success", 'til_rank': agg_result})


@app.route('/til', methods=['POST'])
def create_til():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"user_id": payload["id"]}, {"_id": False})
        til_title_receive = request.form['til_title_give']
        til_content_receive = request.form['til_content_give']
        til_count = db.til.count()
        if til_count == 0:
            max_value = 1
        else:
            max_value = db.til.find_one(sort=[("til_idx", -1)])['til_idx'] + 1
        db.til.count()
        doc = {'til_idx': max_value, 'til_title': til_title_receive, 'til_user': user_info['user_id'],
               'til_content': til_content_receive, 'til_day': datetime.datetime.now(), 'til_view': True}
        db.til.insert_one(doc)
        return jsonify({'msg': 'til 작성 완료!'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))
      

@app.route('/til/<idx>', methods=['GET'])
def read_til(idx):
    doc = db.til.find_one({'til_idx': int(idx)}, {'_id': False})
    return jsonify({"til": doc})


@app.route('/til/user/<idx>', methods=['GET'])
def read_til_user(idx):
    user_id = db.til.find_one({'til_idx': int(idx)}, {'_id': False})['til_user']
    user_info = db.user.find_one({'user_id': user_id}, {'id': False}, )
    user_nickname = user_info['user_nickname']
    github_id = user_info['githhub_id']
    user_profile_info = user_info['user_profile_info']
    return jsonify({"user_nickname": user_nickname, 'githhub_id': github_id, 'user_profile_info': user_profile_info})


@app.route('/heart/<idx>', methods=['GET'])
def read_heart(idx):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_id = db.user.find_one({"user_id": payload["id"]}, {"_id": False})['user_id']

        count = db.like.count_documents({"til_idx": int(idx), "type": 'heart'})
        action = bool(db.like.find_one({"user_id": user_id, "til_idx": int(idx)}))
        print(count)
        print(action)
        return jsonify({'count': count, 'action': action})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


@app.route('/status/<idx>', methods=['GET'])
def read_status(idx):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        now_user_id = db.user.find_one({"user_id": payload["id"]}, {"_id": False})['user_id']
        user_id = db.til.find_one({'til_idx': int(idx)}, {'_id': False})['til_user']
        til_user_id = db.user.find_one({'user_id': user_id}, {'id': False})['user_id']
        print(user_id, til_user_id)
        status = bool(now_user_id == til_user_id)
        return jsonify({"status": status})
        
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


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
        db.til.update_one({'til_idx': int(idx)}, doc)

    msg = '변경 완료!'
    return jsonify({'msg': msg})


@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    til_idx_receive = request.form["til_idx_give"]
    type_receive = request.form["type_give"]
    action_receive = request.form["action_give"]
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)
        user_info = db.user.find_one({'user_id': payload['id']}, {'_id': 0})
        print(user_info)
        til_idx_receive = int(til_idx_receive)
        doc = {
            "til_idx": til_idx_receive,
            "type": type_receive,
            "user_id": user_info['user_id']
        }
        if action_receive == "like":
            db.like.insert_one(doc)
        else:
            db.like.delete_one(doc)
        count = db.like.count_documents({"til_idx": til_idx_receive, "type": type_receive})
        return jsonify({"result": "success", 'msg': 'updated', "count": count})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})


@app.route('/user', methods=['POST'])
def create_user():
    user_id = request.form['user_id_give']
    user_password = request.form['user_pw_give']
    user_nickname = request.form['user_nickname_give']

    pw_hash = hashlib.sha256(user_password.encode('utf-8')).hexdigest()

    doc = {'user_id': user_id, 'user_password': pw_hash, 'user_nickname': user_nickname, 'github_id': '', 'user_profile_pic': '', 'user_profile_pic_real': 'static/profile_pics/profile_placeholder.png', 'user_profile_info': ''}

    db.user.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/user', methods=['GET'])
def read_user():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"user_id": payload["id"]}, {"_id": False, "user_password": False})
        return jsonify({'result': 'success', 'user_info': user_info})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


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
        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


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
            file_path = os.environ.get("S3_URI")+"/{filename}"

            new_doc["user_profile_pic"] = filename
            new_doc["user_profile_pic_real"] = file_path
            s3 = boto3.client('s3',
                              aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID"),
                              aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
                              )
            s3.put_object(
                ACL="public-read",
                Bucket=os.environ.get("S3_BUCKET"),
                Body=file,
                Key=filename,
                ContentType=extension)
        print(new_doc)
        db.user.update_one({'user_id': user_id}, {'$set': new_doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

