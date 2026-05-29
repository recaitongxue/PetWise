import json
from flask import Blueprint, request, jsonify, session
from models.db import get_db
from utils import log_action
from services.ai_agent_client import AIAgentClient

agent_bp = Blueprint('agent', __name__)

ai_client = AIAgentClient()

def generate_llm_response(prompt, breed_context=""):
    """Generate response from AI Agent service"""
    try:
        response = ai_client.chat(
            user_message=prompt,
            use_knowledge_base=True,
            temperature=0.7
        )
        
        if response.get("success") and response.get("content"):
            return response["content"]
        else:
            return f"抱歉，AI服务暂时不可用，请稍后重试。关于{breed_context}，建议咨询专业兽医获取专业建议。"
    except Exception as e:
        return f"抱歉，服务暂时不可用，请稍后重试。"

@agent_bp.route('/agent/chat', methods=['POST'])
def agent_chat():
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required", "code": "AUTH_REQUIRED"}), 401

    try:
        data = request.get_json()
        message = data.get('message')
        session_id = data.get('session_id', 'default')
        breed_context = data.get('breed_context', '')

        if not message:
            return jsonify({"error": "Message is required"}), 400

        user_id = session['user_id']
        db = get_db()

        db.execute('''
            INSERT INTO chat_history (user_id, session_id, role, message, breed_context)
            VALUES (?, ?, 'user', ?, ?)
        ''', (user_id, session_id, message, breed_context))
        db.commit()

        response = generate_llm_response(message, breed_context)

        db.execute('''
            INSERT INTO chat_history (user_id, session_id, role, message, breed_context, model_used)
            VALUES (?, ?, 'assistant', ?, ?, ?)
        ''', (user_id, session_id, response, breed_context, 'ai_agent_service'))
        db.commit()

        log_action(db, user_id, 'agent_chat', {'message': message[:50], 'breed_context': breed_context})

        return jsonify({
            "success": True,
            "session_id": session_id,
            "response": response,
            "model": 'ai_agent_service'
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@agent_bp.route('/agent/history', methods=['GET'])
def agent_history():
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required", "code": "AUTH_REQUIRED"}), 401

    try:
        user_id = session['user_id']
        session_id = request.args.get('session_id', 'default')

        db = get_db()
        history = db.execute('''
            SELECT role, message, breed_context, created_at 
            FROM chat_history 
            WHERE user_id = ? AND session_id = ? 
            ORDER BY created_at ASC
        ''', (user_id, session_id)).fetchall()

        return jsonify({
            "success": True,
            "session_id": session_id,
            "history": [dict(h) for h in history]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@agent_bp.route('/agent/history', methods=['DELETE'])
def clear_history():
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required", "code": "AUTH_REQUIRED"}), 401

    try:
        user_id = session['user_id']
        session_id = request.args.get('session_id')

        db = get_db()
        if session_id:
            db.execute('DELETE FROM chat_history WHERE user_id = ? AND session_id = ?', (user_id, session_id))
        else:
            db.execute('DELETE FROM chat_history WHERE user_id = ?', (user_id,))
        db.commit()

        return jsonify({"success": True, "message": "History cleared"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@agent_bp.route('/agent/advice', methods=['POST'])
def get_advice():
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required", "code": "AUTH_REQUIRED"}), 401

    try:
        data = request.get_json()
        topic = data.get('topic')
        pet_type = data.get('pet_type')
        specific_issue = data.get('specific_issue')

        if not topic:
            return jsonify({"error": "Topic is required"}), 400

        user_id = session['user_id']
        db = get_db()

        response = ai_client.get_pet_advice(topic, pet_type, specific_issue)

        if response.get("success"):
            log_action(db, user_id, 'get_advice', {'topic': topic, 'pet_type': pet_type})
            return jsonify({
                "success": True,
                "topic": topic,
                "pet_type": pet_type,
                "advice": response.get("advice", response.get("content", "")),
                "timestamp": response.get("timestamp")
            })
        else:
            error_msg = response.get("error", "AI服务暂时不可用")
            log_action(db, user_id, 'get_advice', {'topic': topic, 'pet_type': pet_type, 'error': error_msg})
            return jsonify({
                "success": False,
                "error": error_msg
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@agent_bp.route('/agent/emergency', methods=['POST'])
def emergency_consultation():
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required", "code": "AUTH_REQUIRED"}), 401

    try:
        data = request.get_json()
        symptoms = data.get('symptoms')
        pet_type = data.get('pet_type')
        severity = data.get('severity', 'medium')

        if not symptoms or not pet_type:
            return jsonify({"error": "Symptoms and pet_type are required"}), 400

        user_id = session['user_id']
        db = get_db()

        response = ai_client.emergency_consultation(symptoms, pet_type, severity)

        if response.get("success"):
            log_action(db, user_id, 'emergency_consultation', {'symptoms': symptoms[:50], 'pet_type': pet_type, 'severity': severity})
            return jsonify({
                "success": True,
                "severity": severity,
                "pet_type": pet_type,
                "consultation": response.get("consultation", response.get("content", "")),
                "recommendation": response.get("recommendation", "general_advice"),
                "timestamp": response.get("timestamp")
            })
        else:
            error_msg = response.get("error", "AI服务暂时不可用")
            log_action(db, user_id, 'emergency_consultation', {'symptoms': symptoms[:50], 'pet_type': pet_type, 'severity': severity, 'error': error_msg})
            return jsonify({
                "success": False,
                "error": error_msg,
                "warning": "紧急情况下请直接联系宠物医院！"
            })
    except Exception as e:
        return jsonify({"error": str(e), "warning": "紧急情况下请直接联系宠物医院！"}), 500

@agent_bp.route('/agent/health', methods=['GET'])
def agent_health():
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required", "code": "AUTH_REQUIRED"}), 401

    try:
        response = ai_client.health_check()
        return jsonify(response)
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        })

@agent_bp.route('/agent/info', methods=['GET'])
def agent_info():
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required", "code": "AUTH_REQUIRED"}), 401

    try:
        response = ai_client.get_info()
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@agent_bp.route('/agent/models', methods=['GET'])
def agent_models():
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required", "code": "AUTH_REQUIRED"}), 401

    try:
        response = ai_client.get_models()
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500