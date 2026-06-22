"""
AI智能体路由
支持SSE流式响应、档案上下文注入、结构化问诊
"""
import json
import time
from flask import Blueprint, request, jsonify, Response, stream_with_context
from models.db import get_db
from utils import log_action, login_required, get_current_user_id
from services.ai_agent_client import AIAgentClient

agent_bp = Blueprint('agent', __name__)

ai_client = AIAgentClient()

def detect_sensitive_keywords(message):
    """检测敏感健康关键词"""
    sensitive_keywords = ['呕吐', '拉稀', '腹泻', '发烧', '咳嗽', '呼吸困难', '出血', '抽搐', '昏迷', '中毒', '误食']
    return any(keyword in message for keyword in sensitive_keywords)

@agent_bp.route('/agent/chat', methods=['POST'])
@login_required
def agent_chat():
    try:
        data = request.get_json()
        message = data.get('message')
        session_id = data.get('session_id', 'default')
        breed_context = data.get('breed_context', '')
        pet_id = data.get('pet_id')

        if not message:
            return jsonify({"error": "Message is required"}), 400

        user_id = get_current_user_id()
        db = get_db()

        # 获取宠物档案上下文
        pet_context = None
        if pet_id:
            pet = db.execute('SELECT * FROM pets WHERE id = ? AND user_id = ?', (pet_id, user_id)).fetchone()
            if pet:
                pet_context = dict(pet)

        db.execute('''
            INSERT INTO chat_history (user_id, session_id, role, message, breed_context)
            VALUES (?, ?, 'user', ?, ?)
        ''', (user_id, session_id, message, breed_context))
        db.commit()

        response = ai_client.chat(
            user_message=message,
            use_knowledge_base=True,
            temperature=0.7,
            pet_context=pet_context,
            breed_context=breed_context
        )

        if response.get("success") and response.get("content"):
            ai_response = response["content"]
        else:
            ai_response = f"抱歉，AI服务暂时不可用，请稍后重试。错误: {response.get('error', '未知')}"

        db.execute('''
            INSERT INTO chat_history (user_id, session_id, role, message, breed_context, model_used)
            VALUES (?, ?, 'assistant', ?, ?, ?)
        ''', (user_id, session_id, ai_response, breed_context, 'ai_agent_service'))
        db.commit()

        # 检测敏感关键词
        is_sensitive = detect_sensitive_keywords(message)

        log_action(db, user_id, 'agent_chat', {'message': message[:50], 'breed_context': breed_context, 'is_sensitive': is_sensitive})

        return jsonify({
            "success": True,
            "session_id": session_id,
            "response": ai_response,
            "model": 'ai_agent_service',
            "is_sensitive": is_sensitive,
            "suggest_consultation": is_sensitive
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@agent_bp.route('/agent/chat/stream', methods=['POST'])
@login_required
def agent_chat_stream():
    """SSE流式响应接口"""
    data = request.get_json()
    message = data.get('message')
    session_id = data.get('session_id', 'default')
    breed_context = data.get('breed_context', '')
    pet_id = data.get('pet_id')

    if not message:
        return jsonify({"error": "Message is required"}), 400

    user_id = get_current_user_id()
    db = get_db()

    # 获取宠物档案上下文
    pet_context = None
    if pet_id:
        pet = db.execute('SELECT * FROM pets WHERE id = ? AND user_id = ?', (pet_id, user_id)).fetchone()
        if pet:
            pet_context = dict(pet)

    # 保存用户消息
    db.execute('''
        INSERT INTO chat_history (user_id, session_id, role, message, breed_context)
        VALUES (?, ?, 'user', ?, ?)
    ''', (user_id, session_id, message, breed_context))
    db.commit()

    def generate():
        full_content = ""
        try:
            for chunk in ai_client.stream_chat(
                user_message=message,
                use_knowledge_base=True,
                temperature=0.7,
                pet_context=pet_context,
                breed_context=breed_context
            ):
                if chunk.startswith("[DONE]"):
                    break
                if chunk.startswith("Error:"):
                    response_data = json.dumps({'error': chunk[6:]})
                    yield f"data: {response_data}\n\n".encode('utf-8')
                    return
                
                full_content += chunk
                response_data = json.dumps({'content': chunk})
                yield f"data: {response_data}\n\n".encode('utf-8')

            if full_content:
                db.execute('''
                    INSERT INTO chat_history (user_id, session_id, role, message, breed_context, model_used)
                    VALUES (?, ?, 'assistant', ?, ?, ?)
                ''', (user_id, session_id, full_content, breed_context, 'ai_agent_service'))
                db.commit()

                log_action(db, user_id, 'agent_chat_stream', {'message': message[:50], 'breed_context': breed_context})

            yield f"data: {json.dumps({'done': True})}\n\n".encode('utf-8')
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n".encode('utf-8')

    response = Response(
        stream_with_context(generate()),
        mimetype='text/event-stream; charset=utf-8'
    )
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'
    response.headers['X-Accel-Buffering'] = 'no'
    response.headers['Content-Type'] = 'text/event-stream; charset=utf-8'
    return response

@agent_bp.route('/agent/structured-consultation', methods=['POST'])
@login_required
def structured_consultation():
    """结构化问诊接口"""
    try:
        data = request.get_json()
        pet_id = data.get('pet_id')
        symptoms = data.get('symptoms', [])
        duration = data.get('duration')
        severity = data.get('severity', 'medium')
        additional_info = data.get('additional_info', '')

        if not pet_id or not symptoms:
            return jsonify({"error": "pet_id and symptoms are required"}), 400

        user_id = get_current_user_id()
        db = get_db()

        # 获取宠物档案
        pet = db.execute('SELECT * FROM pets WHERE id = ? AND user_id = ?', (pet_id, user_id)).fetchone()
        if not pet:
            return jsonify({"error": "Pet not found"}), 404

        pet_context = dict(pet)

        response = ai_client.structured_consultation(
            pet_id=pet_id,
            symptoms=symptoms,
            duration=duration,
            severity=severity,
            additional_info=additional_info,
            pet_context=pet_context
        )

        if response.get("success"):
            log_action(db, user_id, 'structured_consultation', {'pet_id': pet_id, 'symptoms': symptoms, 'severity': severity})
            return jsonify({
                "success": True,
                "consultation": response.get("consultation"),
                "recommendation": response.get("recommendation", "建议尽快联系宠物医院进行专业诊断")
            })
        else:
            return jsonify({
                "success": False,
                "error": "AI服务暂时不可用",
                "recommendation": "建议尽快联系宠物医院进行专业诊断"
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@agent_bp.route('/agent/history', methods=['GET'])
@login_required
def agent_history():
    try:
        user_id = get_current_user_id()
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
@login_required
def clear_history():
    try:
        user_id = get_current_user_id()
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
@login_required
def get_advice():
    try:
        data = request.get_json()
        topic = data.get('topic')
        pet_type = data.get('pet_type')
        specific_issue = data.get('specific_issue')

        if not topic:
            return jsonify({"error": "Topic is required"}), 400

        user_id = get_current_user_id()
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
@login_required
def emergency_consultation():
    try:
        data = request.get_json()
        symptoms = data.get('symptoms')
        pet_type = data.get('pet_type')
        severity = data.get('severity', 'medium')

        if not symptoms or not pet_type:
            return jsonify({"error": "Symptoms and pet_type are required"}), 400

        user_id = get_current_user_id()
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
    print("DEBUG: agent_health endpoint called")
    try:
        response = ai_client.health_check()
        print(f"DEBUG: ai_client.health_check returned: {response}")
        return jsonify(response)
    except Exception as e:
        print(f"DEBUG: agent_health error: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        })

@agent_bp.route('/agent/info', methods=['GET'])
@login_required
def agent_info():
    try:
        response = ai_client.get_info()
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@agent_bp.route('/agent/models', methods=['GET'])
@login_required
def agent_models():
    try:
        response = ai_client.get_models()
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
