from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf import CSRFProtect
import os
from flask_wtf.csrf import CSRFProtect



app = Flask(__name__)


app.config['SECRET_KEY'] = 'daa75c750b3aedd0b69a7fa6ae208e4172d1cdb3cf48b15fbf9c110899d910a5'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pythonic.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['UPLOADED_IMAGES_DEST'] = os.path.join(app.root_path, 'static/uploads')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"
csrf = CSRFProtect(app)
csrf.init_app(app)
csrf = CSRFProtect(app)



from pythonic import routes