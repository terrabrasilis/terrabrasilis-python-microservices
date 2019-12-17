from flask import Flask
import socket

SERVER_IP='0.0.0.0'
app = Flask(__name__)

@app.route('/health', methods=['GET'])
def pingPong():

    return socket.gethostname()

if __name__ == '__main__':
    app.run(host=SERVER_IP, port=5000, debug=True)