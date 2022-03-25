from email.policy import default
import imp
import re
from flask import Flask
from firebase_admin import credentials,initialize_app
from flask_cors import CORS

cred = credentials.Certificate("api/key.json")
default_app = initialize_app(cred)

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config['SECRET_KEY'] = '12345azsxdc'

    from .userAPI import userAPI
    
    #註冊api名字 xxx/user
    app.register_blueprint(userAPI,url_prefix='/user')
    return app