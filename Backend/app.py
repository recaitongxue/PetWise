import os
from flask import Flask
from config import Config
from models.db import init_db
from routes.auth import auth_bp
from routes.recognize import recognize_bp
from routes.agent import agent_bp
from routes.pets import pets_bp
from routes.favorites import favorites_bp
from routes.comments import comments_bp
from routes.admin import admin_bp
from routes.other import other_bp

app = Flask(__name__)
app.config.from_object(Config)

app.secret_key = os.urandom(24)

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(recognize_bp, url_prefix='/api')
app.register_blueprint(agent_bp, url_prefix='/api')
app.register_blueprint(pets_bp, url_prefix='/api')
app.register_blueprint(favorites_bp, url_prefix='/api')
app.register_blueprint(comments_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')
app.register_blueprint(other_bp, url_prefix='/api')

def init_app():
    Config.init_folders()
    init_db()

init_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)