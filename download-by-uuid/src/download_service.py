import os
from flask import Flask, request, send_file
from flask_restful import Api, Resource
from uuid_table_dao import UuidTableDao

SERVER_IP='0.0.0.0'
FILE_PATH='/documents'
FILE_NAME=os.getenv("FILE_NAME", "test.zip")

app = Flask(__name__)
api = Api(app)

@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

class DownloadControl(Resource):
    def get(self, uuid):
        file_path = os.path.realpath(os.path.dirname(__file__) + "/" + FILE_PATH)
        client_ip = ""
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            client_ip=request.environ['REMOTE_ADDR']
        else:
            client_ip=request.environ['HTTP_X_FORWARDED_FOR'] # if behind a proxy
        try:
            db = UuidTableDao()
            if db.confirmUUID(uuid)==True:
                db.increaseDownloadByUUID(uuid)
                db.storeClientIP(uuid,client_ip)
            else:
                return 'Invalid identifier', 404
        except Exception as error:
            return 'Server Error', 500

        return send_file(os.path.realpath(file_path+"/"+FILE_NAME),attachment_filename=FILE_NAME, as_attachment=True)

api.add_resource(DownloadControl, '/bycode/<uuid>')

if __name__ == '__main__':
     app.run(host=SERVER_IP, port=5000, debug=True)