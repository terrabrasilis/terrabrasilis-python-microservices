import os
from flask import Flask, request, render_template, jsonify
from user_table_dao import UserTableDao
from email_service import EmailService

SERVER_IP='0.0.0.0'
DOWNLOAD_URL='http://localhost:8000/counter/download/bycode/'
# get env var setted in Dockerfile
is_docker_env = os.getenv("DOCKER_ENV", False)
# If the environment is docker then use the absolute path to write log file
if is_docker_env:
    DOWNLOAD_URL='http://terrabrasilis.dpi.inpe.br/counter/download/bycode/'
    
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/registry', methods=['POST'])
def store_form_post():
    link=None
    code=None

    email = request.form['email']
    user_name = request.form['user_name']
    institution = request.form['institution']

    try:
        db = UserTableDao()
        user=db.storeClient(user_name,email,institution)
        if(user["user_id"]):
            code=db.generateUUID(user["user_id"])
        else:
            code=db.getUUID(email)

        if(code["uuid"]):
            link=DOWNLOAD_URL+code["uuid"]
            mail=EmailService()
            mail.sendLinkByEmail(link, email)

        result = { "status": 0}
        if link:
            result = { "status": 1}
        result = {str(key): value for key, value in result.items()}
    except Exception as error:
        result = { "status": 0,"error":str(error)}
        result = {str(key): value for key, value in result.items()}
    return jsonify(result=result)

if __name__ == '__main__':
    app.run(host=SERVER_IP, port=5000, debug=True)