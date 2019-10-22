import os
from flask import Flask, request, send_file
from flask_restful import Api, Resource
from uuid_table_dao import UuidTableDao

SERVER_IP='0.0.0.0'
FILE_PATH='/documents'
FILE_NAME=os.getenv("FILE_NAME", "test.zip")

app = Flask(__name__)
api = Api(app)

class DownloadControl(Resource):
     def get(self, uuid):
        file_path = os.path.realpath(os.path.dirname(__file__) + "/" + FILE_PATH)
        try:
            db = UuidTableDao()
            if db.confirmUUID(uuid)==True:
                db.increaseDownloadByUUID(uuid)
                db.storeClientIP(uuid,request.remote_addr)
            else:
                return 'Invalid identifier', 404
        except Exception as error:
            return 'Server Error', 500

        return send_file(os.path.realpath(file_path+"/"+FILE_NAME),attachment_filename=FILE_NAME, as_attachment=True)

api.add_resource(DownloadControl, '/files/bycode/<uuid>')

if __name__ == '__main__':
     app.run(host=SERVER_IP, port=5000, debug=True)