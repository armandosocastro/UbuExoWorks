# app.py
import os

from flask import Flask
app = Flask(__name__)

_port = os.environ.get('PORT', 5000)

@app.route("/")
def home():
    return "Hello, Flask!"


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=_port)