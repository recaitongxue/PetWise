import json
from flask import Blueprint, request, jsonify, session
from models.db import get_db
from utils import log_action, generate_fallback_response, generate_suggestions

agent_bp = Blueprint('agent', __name__)

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    import torch
    LLM_AVAILABLE = True
    try:
        tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-2")
        model = AutoModelForCausalLM.from_pretrained(
            "microsoft/phi-2",
            device_map="auto",
            torch_dtype="auto",
            trust_remote_code=True
        )
        pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
    except Exception:
        LLM_AVAILABLE = False
except Exception:
    LLM_AVAILABLE = False

def generate_llm_response(prompt, breed_context=""):
    try:
        system_prompt = "你是一个专业的宠物顾问，擅长回答关于宠物饲养、健康、训练等方面的问题。"
        
        if breed_context:
            system_prompt += f"当前讨论的宠物品种是：{breed_context}。"
        
        system_prompt += "请用中文回答，语言简洁友好。"
        
        full_prompt = f"{system_prompt}\n\n用户问题：{prompt}\n\n回答："
        
        if LLM_AVAILABLE:
            outputs = pipe(
                full_prompt,
                max_new_tokens=200,
                temperature=0.7,
                top_p=0.95,
                repetition_penalty=1.15,
                pad_token_id=tokenizer.eos_token_id
            )
            response = outputs[0]['generated_text'].replace(full_prompt, "").strip()
            if not response or len(response) < 10:
                response = generate_fallback_response(prompt, breed_context)
        else:
            response = generate_fallback_response(prompt, breed_context)
        
        return response
    except Exception:
        return generate_fallback_response(prompt, breed_context)

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
        ''', (user_id, session_id, response, breed_context, 'microsoft/phi-2' if LLM_AVAILABLE else 'fallback'))
        db.commit()

        suggestions = generate_suggestions(message, breed_context)

        log_action(db, user_id, 'agent_chat', {'message': message[:50], 'breed_context': breed_context})

        return jsonify({
            "success": True,
            "session_id": session_id,
            "response": response,
            "model": 'microsoft/phi-2' if LLM_AVAILABLE else 'fallback',
            "suggestions": suggestions
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