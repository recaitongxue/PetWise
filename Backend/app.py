import os
import subprocess
import sys
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

def start_ai_agent():
    """启动AI智能体服务"""
    ai_agent_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ai_agent', 'main.py')
    if os.path.exists(ai_agent_path):
        try:
            print(f"Starting AI Agent service from {ai_agent_path}...")
            process = subprocess.Popen(
                [sys.executable, ai_agent_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(ai_agent_path)
            )
            print("AI Agent service started successfully")
            return process
        except Exception as e:
            print(f"Failed to start AI Agent: {e}")
            return None
    else:
        print(f"AI Agent not found at {ai_agent_path}")
        return None

def init_app():
    Config.init_folders()
    init_db()

init_app()

if __name__ == '__main__':
    ai_agent_process = start_ai_agent()
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    finally:
        if ai_agent_process:
            ai_agent_process.terminate()
            ai_agent_process.wait()
            print("AI Agent service stopped")