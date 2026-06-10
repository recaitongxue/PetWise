from flask import Blueprint, request, jsonify
from models.db import get_db
from utils import log_action, login_required, get_current_user_id

comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/comments/<breed>', methods=['GET'])
def get_comments(breed):
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        offset = (page - 1) * per_page

        db = get_db()
        comments = db.execute('''
            SELECT c.id, c.content, c.rating, c.likes, c.created_at, u.username, u.avatar
            FROM comments c
            LEFT JOIN users u ON c.user_id = u.id
            WHERE c.breed = ?
            ORDER BY c.created_at DESC
            LIMIT ? OFFSET ?
        ''', (breed, per_page, offset)).fetchall()

        total = db.execute('SELECT COUNT(*) FROM comments WHERE breed = ?', (breed,)).fetchone()[0]

        return jsonify({
            "success": True,
            "data": [dict(c) for c in comments],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@comments_bp.route('/comments', methods=['POST'])
@login_required
def add_comment():
    try:
        user_id = get_current_user_id()
        data = request.get_json()

        breed = data.get('breed')
        content = data.get('content')
        rating = data.get('rating', 5)

        if not breed or not content:
            return jsonify({"error": "Breed and content are required"}), 400

        if rating < 1 or rating > 5:
            return jsonify({"error": "Rating must be between 1 and 5"}), 400

        db = get_db()
        db.execute('''
            INSERT INTO comments (user_id, breed, content, rating)
            VALUES (?, ?, ?, ?)
        ''', (user_id, breed, content, rating))
        db.commit()

        log_action(db, user_id, 'add_comment', {'breed': breed, 'rating': rating})

        return jsonify({"success": True, "message": "Comment added"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@comments_bp.route('/comments/<int:comment_id>/like', methods=['POST'])
@login_required
def like_comment(comment_id):
    """点赞评论"""
    try:
        user_id = get_current_user_id()
        db = get_db()

        comment = db.execute('SELECT * FROM comments WHERE id = ?', (comment_id,)).fetchone()
        if not comment:
            return jsonify({"error": "Comment not found"}), 404

        # 检查是否已点赞
        existing_like = db.execute('SELECT * FROM comment_likes WHERE comment_id = ? AND user_id = ?', 
                                  (comment_id, user_id)).fetchone()
        
        if existing_like:
            # 已点赞，取消点赞
            db.execute('DELETE FROM comment_likes WHERE comment_id = ? AND user_id = ?', (comment_id, user_id))
            db.execute('UPDATE comments SET likes = likes - 1 WHERE id = ?', (comment_id,))
            db.commit()
            return jsonify({"success": True, "message": "Comment unliked", "liked": False})
        else:
            # 未点赞，添加点赞
            db.execute('INSERT INTO comment_likes (comment_id, user_id) VALUES (?, ?)', (comment_id, user_id))
            db.execute('UPDATE comments SET likes = likes + 1 WHERE id = ?', (comment_id,))
            db.commit()
            return jsonify({"success": True, "message": "Comment liked", "liked": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@comments_bp.route('/comments/<int:comment_id>/liked', methods=['GET'])
@login_required
def check_comment_liked(comment_id):
    """检查是否已点赞"""
    try:
        user_id = get_current_user_id()
        db = get_db()

        liked = db.execute('SELECT * FROM comment_likes WHERE comment_id = ? AND user_id = ?', 
                          (comment_id, user_id)).fetchone()
        
        return jsonify({"success": True, "liked": bool(liked)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@comments_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    """删除评论"""
    try:
        user_id = get_current_user_id()
        db = get_db()

        comment = db.execute('SELECT * FROM comments WHERE id = ?', (comment_id,)).fetchone()
        if not comment:
            return jsonify({"error": "Comment not found"}), 404

        # 只有评论作者可以删除
        if comment['user_id'] != user_id:
            return jsonify({"error": "Permission denied"}), 403

        # 删除点赞记录
        db.execute('DELETE FROM comment_likes WHERE comment_id = ?', (comment_id,))
        # 删除评论
        db.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
        db.commit()

        log_action(db, user_id, 'delete_comment', {'comment_id': comment_id})

        return jsonify({"success": True, "message": "Comment deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
