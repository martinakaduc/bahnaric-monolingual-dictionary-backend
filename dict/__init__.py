import os
from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

# from flask_ngrok import run_with_ngrok
app = Flask(__name__)

dir = os.path.dirname(__file__)

# run_with_ngrok(app)
dir_db = os.path.join(dir,'dict.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ dir_db
app.config['SECRET_KEY'] ='1b253b240b0a78e764b9ec90'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    
#audio_dir
bana_bd = os.path.join(dir,'Bana-BinhDinh', 'audio_by_word')
bana_kt = os.path.join(dir,'Bana-KonTum', 'audio_by_word')
bana_gl = os.path.join(dir,'Bana-GiaLai', 'audio_by_word')

from dict import routes
from .models import User, Word, DailyWord

with app.app_context():
    db.create_all()
    print('Created Database!')


