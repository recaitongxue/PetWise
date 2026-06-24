import os
import subprocess
import sys
import time
import requests
from flask import Flask, send_from_directory
from flask_cors import CORS
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
from routes.health import health_bp
from routes.schedule import schedule_bp
from routes.model_admin import model_admin_bp
from routes.sample_admin import sample_admin_bp

app = Flask(__name__)
app.config.from_object(Config)

# 启用 CORS，支持前端跨域访问
CORS(app, supports_credentials=True, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

app.secret_key = os.urandom(24)

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(recognize_bp, url_prefix='/api')
app.register_blueprint(agent_bp, url_prefix='/api')
app.register_blueprint(pets_bp, url_prefix='/api')
app.register_blueprint(favorites_bp, url_prefix='/api')
app.register_blueprint(comments_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')
app.register_blueprint(other_bp, url_prefix='/api')
app.register_blueprint(health_bp, url_prefix='/api')
app.register_blueprint(schedule_bp, url_prefix='/api')
app.register_blueprint(model_admin_bp, url_prefix='/api')
app.register_blueprint(sample_admin_bp, url_prefix='/api')

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def start_ai_agent():
    """启动AI智能体服务"""
    ai_agent_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ai_agent', 'main.py')
    if os.path.exists(ai_agent_path):
        try:
            print(f"Starting AI Agent service from {ai_agent_path}...")
            process = subprocess.Popen(
                [sys.executable, ai_agent_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=os.path.dirname(ai_agent_path),
                text=True
            )
            
            def read_output():
                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None:
                        break
                    if line:
                        print(f"[AI Agent] {line.strip()}")
            
            import threading
            output_thread = threading.Thread(target=read_output, daemon=True)
            output_thread.start()
            
            print("AI Agent service started. Waiting for it to be ready...")
            
            max_retries = 30
            retry_interval = 2
            
            for attempt in range(max_retries):
                time.sleep(retry_interval)
                try:
                    response = requests.get("http://localhost:8000/health", timeout=5)
                    if response.status_code == 200:
                        print("AI Agent service is ready!")
                        return process
                    else:
                        print(f"AI Agent service not ready yet (status: {response.status_code}), attempt {attempt + 1}/{max_retries}")
                except requests.exceptions.RequestException as e:
                    print(f"AI Agent service not ready yet: {e}, attempt {attempt + 1}/{max_retries}")
            
            print("WARNING: AI Agent service did not become ready within timeout, but continuing anyway")
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
    
    from routes.agent import ai_client
    from models.db import get_db
    
    db = get_db()
    default_model = db.execute(
        'SELECT * FROM llm_models WHERE is_default = 1 AND is_active = 1 LIMIT 1'
    ).fetchone()
    
    if default_model:
        model_config = dict(default_model)
        ai_client.set_default_model_config(model_config)
        print(f"Loaded default model: {model_config['name']} ({model_config['model_name']})")
    else:
        print("No default model found in database, using AI Agent default configuration")

    default_embedding = db.execute(
        'SELECT * FROM llm_models WHERE is_embedding = 1 AND is_default = 1 AND is_active = 1 LIMIT 1'
    ).fetchone()
    
    if default_embedding:
        embedding_config = dict(default_embedding)
        ai_client.set_default_embedding_config(embedding_config)
        print(f"Loaded default embedding model: {embedding_config['name']} ({embedding_config['model_name']})")
    else:
        print("No default embedding model found in database, using AI Agent default configuration")

init_app()

if __name__ == '__main__':
    ai_agent_process = start_ai_agent()
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    finally:
        if ai_agent_process:
            ai_agent_process.terminate()
            ai_agent_process.wait()
            print("AI Agent service stopped")