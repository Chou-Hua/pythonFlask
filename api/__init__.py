from email.policy import default
import imp
import re
from flask import Flask
from firebase_admin import credentials,initialize_app
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from getEvn import getPrivateKey


print(getPrivateKey)
cred = credentials.Certificate(getPrivateKey)
default_app = initialize_app(cred)
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config['JWT_SECRET_KEY'] = '12345azsxdc'
    jwt.init_app(app)

    from .userAPI import userAPI
    
    
    #註冊api名字 xxx/user
    app.register_blueprint(userAPI,url_prefix='/user')
    return app