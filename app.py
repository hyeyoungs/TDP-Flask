from flask import Flask, render_template, jsonify, request
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

# pc 용 :
client = MongoClient('localhost', 27017)
db = client.tdp

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

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/til_board')
def listing_page():
    return render_template('til_board.html')

@app.route('/til_board_listing', methods=['GET'])
def all_til():
    temp = list(db.til.find({}, {'_id': False}))
    return jsonify({'result': "success", 'all_til': temp})

@app.route('/api/list_myTIL', methods=['POST'])
def read_myTIL():
    til_user_receive = request.form['til_user_give']
    my_til = list(db.til.find({'til_user': til_user_receive}).sort('_id', -1))
    for doc in my_til:
       doc["_id"] = str(doc["_id"])
    return jsonify({'result' : 'success', 'my_til' : my_til})

@app.route('/home_listing', methods=['GET'])
def home_til():
    temp = list(db.til.find({}, {'_id': False}).sort("_id",-1))
    return jsonify({'result': "success", 'home_til': temp})

@app.route('/home_ranking', methods=['GET'])
def home_ranking():
    agg_result=list(db.til.aggregate([
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

    doc = {'til_title': til_title_receive, 'til_user': til_user_receive, 'til_content': til_content_receive, 'til_day': current_time, 'til_view': True}
    db.til.insert_one(doc)
    return jsonify({'msg': 'til 작성 완료!'})

@app.route('/api/delete', methods=['POST'])
def api_delete():
    til_id_receive = request.form['til_id_give']
    db.til.delete_one({'_id' : ObjectId(til_id_receive)})
    return jsonify({'msg': 'til 삭제 완료!'})

@app.route('/api/update', methods=['POST'])
def api_update():
    til_id_receive = request.form['til_id_give']
    til_title_receive = request.form['til_title_give']
    til_content_receive = request.form['til_content_give']
    current_time = datetime.now()

    doc = {'til_title': til_title_receive, 'til_content': til_content_receive, 'til_update_day': current_time}
    db.til.update_one({'_id': til_id_receive}, doc)
    return jsonify({'msg': '수정 완료!'})

@app.route('/api/update/view', methods=['POST'])
def api_update_view():
    til_id_receive = request.form['til_id_give']
    til_view = db.til.find_one({'_id': ObjectId(til_id_receive)}, {"_id": 0, "til_view": 1})
    view_value = til_view["til_view"]
    if not isinstance(view_value, bool):
        msg = '공개 여부의 값이 정확하지 않습니다.'
    else:
        doc = {"$set": {'til_view': not(view_value)}}
        db.til.update_one({'_id': ObjectId(til_id_receive)}, doc)

    msg = '변경 완료!'
    return jsonify({'msg': msg})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)