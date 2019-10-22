import os
from flask import Flask, request, render_template, jsonify
from user_table_dao import UserTableDao

SERVER_IP='0.0.0.0'
#DOWNLOAD_URL='http://terrabrasilis.dpi.inpe.br/'
DOWNLOAD_URL='http://localhost:8000/files/bycode/'

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/prepare/download', methods=['POST'])
def store_form_post():
    path=None
    code=None

    email = request.form['email']
    user_name = request.form['user_name']
    institution = request.form['institution']
    db = UserTableDao()
    user=db.storeClient(user_name,email,institution)
    if(user["user_id"]):
        code=db.generateUUID(user["user_id"])
    else:
        code=db.getUUID(email)

    if(code["uuid"]):
        path=DOWNLOAD_URL+code["uuid"]

    result = {
        "output": path
    }
    result = {str(key): value for key, value in result.items()}
    return jsonify(result=result)

if __name__ == '__main__':
    app.run(host=SERVER_IP, port=5000, debug=True)