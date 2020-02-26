from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import stripe

app=Flask("__name__")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
secret_key = 'sk_test_VnqwuPJG0G3b6Vqq8XoqZVIR00gFPcAG6l'
app.config['SECRET_KEY'] = secret_key
pub_key = 'pk_test_Wb7KgyiT9WIQ6EfDgtH5PnvL004t86Ed6M'

stripe.api_key = secret_key

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from views import *

if __name__=="__main__":
    app.run(debug=True,host='127.0.0.1',port=5000)