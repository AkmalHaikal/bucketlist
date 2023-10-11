import os
from os.path import join, dirname
from dotenv import load_dotenv

from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)

db = client[DB_NAME]

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route("/bucket", methods=["POST"])
def bucket_post():
    bucket_receive = request.form["bucket_give"]
    # untuk menghitung semua dokumen di koleksi bucket lalu memasukannya ke variable count
    count = db.bucket.count_documents({})
    num = count + 1  # setiap dokument dapat memiliki angka unik
    doc = {
        'num': num,
        'bucket': bucket_receive,
        'done': 0  # status 0 ini artinya tugas belum selesai, dan status done 1 maka tugas telah selesai
    }
    db.bucket.insert_one(doc)
    return jsonify({'msg': 'data saved!'})


@app.route("/bucket/done", methods=["POST"])
def bucket_done():
    num_receive = request.form['num_give']
    db.bucket.update_one(
        # yang pertama untuk menambahkan data yang ingin di update, dan menggunakan int agar menghindari user memasukan data type string (sering terjadi ketika menggunakan jquary dan ajax)
        {'num': int(num_receive)},
        # untuk menunjukan cara mengupdate document yang ada di database
        {'$set': {'done': 1}}
    )
    return jsonify({'msg': 'Update done!'})


@app.route("/bucket/delete", methods=["POST"])
def bucket_delete():
    num_receive = request.form['num_give']
    db.bucket.delete_one({'num': int(num_receive)})
    return jsonify({'msg': 'Task deleted!'})


@app.route("/bucket", methods=["GET"])
def bucket_get():
    # yang pertama kosong karena akan mengambil semua bucket list, dan yang kedua adalah data yang tidak dibutuhkan
    buckets_list = list(db.bucket.find({}, {'_id': False}))
    return jsonify({'buckets': buckets_list})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
