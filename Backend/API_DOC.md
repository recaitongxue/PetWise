# PetWise API 接口文档 v4.0

## 概述

PetWise API v4.0 是一个功能完善的宠物服务平台后端系统，包含：
- 👤 用户认证系统（管理员/普通用户角色）
- 📸 宠物品种识别（基于 EfficientNet-B3）
- 🤖 AI智能体对话（调用 ai_agent 服务）
- 🐾 宠物档案管理
- ⭐ 收藏与评论系统
- 📊 系统管理后台
- 📢 公告与反馈系统

**基础 URL**: `http://localhost:5000`

### 核心功能模块

| 模块 | 功能 |
|------|------|
| **认证模块** | 用户注册、登录、个人信息管理 |
| **宠物识别** | 图片识别、Base64识别、识别历史 |
| **AI智能体** | 对话、咨询建议、紧急救援 |
| **宠物档案** | CRUD完整管理 |
| **收藏评论** | 品种收藏、评分评论 |
| **系统管理** | 用户管理、统计日志、公告管理 |

### 数据库

使用 **SQLite** 数据库，文件位置：`e:\PetWise\Backend\petwise.db`

#### 数据表

| 表名 | 说明 |
|------|------|
| users | 用户表（含角色：admin/user） |
| pets | 宠物档案表 |
| recognitions | 识别记录表 |
| chat_history | AI对话历史表 |
| favorites | 收藏表 |
| breed_info | 品种信息表（23种宠物） |
| comments | 评论表 |
| system_logs | 系统日志表 |
| announcements | 公告表 |
| feedback | 用户反馈表 |
| llm_models | 大模型配置表 |
| knowledge_base | 知识库表 |

---

## 认证说明

### 认证方式

Token 认证：登录成功后返回 `token`，后续请求通过以下方式传递：

```
Authorization: <token>
```

或通过 Cookie 自动携带。

### 角色说明

| 角色 | 说明 | 权限 |
|------|------|------|
| admin | 管理员 | 全部接口 |
| user | 普通用户 | 个人数据接口 + 公告查看 |

> ⚠️ 注册用户名为 `admin` 时自动设置为管理员角色

---

## 接口列表

### 认证相关 (5个)

| 方法 | 路径 | 认证 | 描述 |
|------|------|------|------|
| POST | `/api/auth/register` | ❌ | 用户注册 |
| POST | `/api/auth/login` | ❌ | 用户登录 |
| POST | `/api/auth/logout` | ✅ | 用户登出 |
| GET | `/api/auth/profile` | ✅ | 获取个人信息 |
| PUT | `/api/auth/profile` | ✅ | 更新个人信息 |

### 宠物识别 (10个)

| 方法 | 路径 | 认证 | 描述 |
|------|------|------|------|
| POST | `/api/recognize` | ✅ | 识别宠物品种（文件上传） |
| POST | `/api/recognize/base64` | ✅ | 识别宠物品种（Base64） |
| POST | `/api/recognize/camera` | ✅ | 摄像头识别（单帧） |
| POST | `/api/recognize/camera/stream` | ✅ | 摄像头批量识别 |
| GET | `/api/recognize/camera/session/{session_id}` | ✅ | 获取摄像头会话记录 |
| GET | `/api/recognize/camera/sessions` | ✅ | 获取摄像头会话列表 |
| GET | `/api/recognize/history` | ✅ | 识别历史记录 |
| DELETE | `/api/recognize/history/{id}` | ✅ | 删除识别记录 |
| GET | `/api/classes` | ❌ | 获取所有宠物类别 |
| GET | `/api/model/status` | ❌ | 模型状态检查 |

### AI智能体 (7个)

| 方法 | 路径 | 认证 | 描述 |
|------|------|------|------|
| POST | `/api/agent/chat` | ✅ | AI对话 |
| GET | `/api/agent/history` | ✅ | 对话历史 |
| DELETE | `/api/agent/history` | ✅ | 清除对话历史 |
| POST | `/api/agent/advice` | ✅ | 获取养宠建议 |
| POST | `/api/agent/emergency` | ✅ | 紧急咨询 |
| GET | `/api/agent/health` | ✅ | AI服务健康检查 |
| GET | `/api/agent/models` | ✅ | 获取可用模型 |

### 宠物档案 (5个)

| 方法 | 路径 | 认证 | 描述 |
|------|------|------|------|
| GET | `/api/pets` | ✅ | 我的宠物列表 |
| POST | `/api/pets` | ✅ | 添加宠物 |
| GET | `/api/pets/{id}` | ✅ | 宠物详情 |
| PUT | `/api/pets/{id}` | ✅ | 更新宠物 |
| DELETE | `/api/pets/{id}` | ✅ | 删除宠物 |

### 收藏与评论 (6个)

| 方法 | 路径 | 认证 | 描述 |
|------|------|------|------|
| GET | `/api/favorites` | ✅ | 我的收藏 |
| POST | `/api/favorites` | ✅ | 添加收藏 |
| DELETE | `/api/favorites/{breed}` | ✅ | 取消收藏 |
| GET | `/api/comments/{breed}` | ❌ | 评论列表 |
| POST | `/api/comments` | ✅ | 添加评论 |
| POST | `/api/comments/{id}/like` | ✅ | 点赞评论 |

### 其他接口 (3个)

| 方法 | 路径 | 认证 | 描述 |
|------|------|------|------|
| GET | `/api/breed/{breed}` | ❌ | 品种详情 |
| POST | `/api/feedback` | ✅ | 提交反馈 |
| GET | `/api/health_check` | ❌ | 服务健康检查 |

### 管理员接口 (20个)

| 方法 | 路径 | 认证 | 描述 |
|------|------|------|------|
| GET | `/api/admin/users` | ✅Admin | 用户管理 |
| PUT | `/api/admin/users/{id}` | ✅Admin | 更新用户 |
| GET | `/api/admin/stats` | ✅Admin | 系统统计 |
| GET | `/api/admin/logs` | ✅Admin | 操作日志 |
| GET | `/api/admin/announcements` | ❌ | 获取公告 |
| POST | `/api/admin/announcements` | ✅Admin | 发布公告 |
| GET | `/api/admin/feedback` | ✅Admin | 用户反馈 |
| PUT | `/api/admin/feedback/{id}` | ✅Admin | 回复反馈 |
| PUT | `/api/admin/breeds/{breed}` | ✅Admin | 更新品种信息 |
| GET | `/api/admin/models` | ✅Admin | 获取大模型列表 |
| POST | `/api/admin/models` | ✅Admin | 添加大模型 |
| PUT | `/api/admin/models/{id}` | ✅Admin | 更新大模型 |
| DELETE | `/api/admin/models/{id}` | ✅Admin | 删除大模型 |
| POST | `/api/admin/models/default/{id}` | ✅Admin | 设置默认模型 |
| GET | `/api/admin/knowledge` | ✅Admin | 获取知识库列表 |
| POST | `/api/admin/knowledge` | ✅Admin | 添加知识库 |
| PUT | `/api/admin/knowledge/{id}` | ✅Admin | 更新知识库 |
| DELETE | `/api/admin/knowledge/{id}` | ✅Admin | 删除知识库 |
| GET | `/api/admin/knowledge/categories` | ✅Admin | 获取知识库分类 |

---

## 1. 用户注册

### 请求

```http
POST /api/auth/register
Content-Type: application/json
```

**请求体**:

```json
{
  "username": "testuser",
  "password": "123456",
  "email": "test@example.com"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | ✅ | 用户名 |
| password | string | ✅ | 密码（至少6位） |
| email | string | ❌ | 邮箱 |

### 响应

```json
{
  "success": true,
  "message": "Registration successful",
  "user": {
    "id": 1,
    "username": "testuser",
    "role": "user"
  }
}
```

> ⚠️ 用户名为 `admin` 时自动设置为管理员

---

## 2. 用户登录

### 请求

```http
POST /api/auth/login
Content-Type: application/json
```

**请求体**:

```json
{
  "username": "testuser",
  "password": "123456"
}
```

### 响应

```json
{
  "success": true,
  "message": "Login successful",
  "token": "1",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "role": "user",
    "avatar": null,
    "bio": null
  }
}
```

---

## 3. 获取个人信息

### 请求

```http
GET /api/auth/profile
Authorization: <token>
```

### 响应

```json
{
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "role": "user",
    "avatar": null,
    "bio": null,
    "created_at": "2024-01-15 10:30:00",
    "last_login": "2024-01-15 10:30:00"
  },
  "stats": {
    "pets_count": 2,
    "recognitions_count": 10,
    "favorites_count": 5,
    "comments_count": 3
  }
}
```

---

## 4. 更新个人信息

### 请求

```http
PUT /api/auth/profile
Authorization: <token>
Content-Type: application/json
```

**请求体**:

```json
{
  "email": "newemail@example.com",
  "bio": "我爱宠物",
  "password": "newpassword123"
}
```

### 响应

```json
{
  "success": true,
  "message": "Profile updated"
}
```

---

## 5. 识别宠物品种

### 请求

```http
POST /api/recognize
Authorization: <token>
Content-Type: multipart/form-data
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| image | file | ✅ | 图片文件 |

### 响应

```json
{
  "success": true,
  "result": {
    "breed": "英国短毛猫",
    "confidence": 0.9989,
    "category": "cat",
    "top5": [
      {"class": "英国短毛猫", "confidence": 0.9989},
      {"class": "美国短毛猫", "confidence": 0.0008},
      {"class": "俄罗斯蓝猫", "confidence": 0.0001}
    ]
  },
  "breed_info": {
    "breed": "英国短毛猫",
    "category": "cat",
    "origin": "英国",
    "personality": "安静、温和、亲人",
    "lifespan": "12-17年",
    "feeding": "控制饮食避免肥胖",
    "care": "定期毛发护理",
    "common_issues": "心脏病、肥胖、肾脏疾病",
    "suitable_for": "新手铲屎官",
    "views": 100,
    "likes": 20
  },
  "model_available": true
}
```

---

## 6. Base64识别

### 请求

```http
POST /api/recognize/base64
Authorization: <token>
Content-Type: application/json
```

**请求体**:

```json
{
  "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQE..."
}
```

---

## 7. AI智能体对话

### 请求

```http
POST /api/agent/chat
Authorization: <token>
Content-Type: application/json
```

**请求体**:

```json
{
  "message": "英国短毛猫好养吗？",
  "session_id": "user123",
  "breed_context": "英国短毛猫"
}
```

### 响应

```json
{
  "success": true,
  "session_id": "user123",
  "response": "英国短毛猫性格温和，适合家庭饲养...",
  "model": "ai_agent_service",
  "suggestions": [
    "告诉我关于英国短毛猫的性格特点",
    "英国短毛猫容易患什么疾病？",
    "如何训练英国短毛猫？"
  ]
}
```

---

## 8. 养宠建议

### 请求

```http
POST /api/agent/advice
Authorization: <token>
Content-Type: application/json
```

**请求体**:

```json
{
  "topic": "饮食",
  "pet_type": "cat",
  "specific_issue": "英国短毛猫的饮食建议"
}
```

### 响应

```json
{
  "success": true,
  "topic": "饮食",
  "pet_type": "cat",
  "advice": "英国短毛猫需要高蛋白饮食...",
  "timestamp": "2024-01-15 10:30:00"
}
```

---

## 9. 紧急咨询

### 请求

```http
POST /api/agent/emergency
Authorization: <token>
Content-Type: application/json
```

**请求体**:

```json
{
  "symptoms": "猫咪呕吐、精神不振",
  "pet_type": "cat",
  "severity": "high"
}
```

### 响应

```json
{
  "success": true,
  "severity": "high",
  "pet_type": "cat",
  "consultation": "紧急情况！猫咪呕吐可能是多种原因...",
  "recommendation": "seek_immediate_medical_attention",
  "timestamp": "2024-01-15 10:30:00"
}
```

---

## 10. 宠物档案管理

### 10.1 添加宠物

```http
POST /api/pets
Authorization: <token>
Content-Type: application/json

{
  "name": "小白",
  "breed": "英国短毛猫",
  "category": "cat",
  "age": 2,
  "gender": "male",
  "bio": "可爱的小猫咪"
}
```

### 10.2 获取宠物列表

```http
GET /api/pets?page=1&per_page=10
Authorization: <token>
```

### 10.3 获取宠物详情

```http
GET /api/pets/1
Authorization: <token>
```

### 10.4 更新宠物

```http
PUT /api/pets/1
Authorization: <token>
Content-Type: application/json

{
  "name": "小白白",
  "age": 3
}
```

### 10.5 删除宠物

```http
DELETE /api/pets/1
Authorization: <token>
```

---

## 11. 收藏与评论

### 11.1 添加收藏

```http
POST /api/favorites
Authorization: <token>
Content-Type: application/json

{
  "breed": "英国短毛猫"
}
```

### 11.2 我的收藏

```http
GET /api/favorites
Authorization: <token>
```

### 11.3 添加评论

```http
POST /api/comments
Authorization: <token>
Content-Type: application/json

{
  "breed": "英国短毛猫",
  "content": "我的猫咪就是英国短毛猫，非常可爱！",
  "rating": 5
}
```

---

## 12. 管理员接口

### 12.1 获取用户列表

```http
GET /api/admin/users?page=1&per_page=20&role=user
Authorization: <admin_token>
```

### 12.2 系统统计

```http
GET /api/admin/stats
Authorization: <admin_token>
```

**响应**:

```json
{
  "total_users": 100,
  "total_pets": 150,
  "total_recognitions": 5000,
  "total_favorites": 300,
  "total_comments": 200,
  "total_chats": 1000,
  "pending_feedback": 5,
  "breed_stats": [...],
  "recent_registrations": [...],
  "daily_recognitions": [...]
}
```

### 12.3 发布公告

```http
POST /api/admin/announcements
Authorization: <admin_token>
Content-Type: application/json

{
  "title": "系统维护通知",
  "content": "将于今晚10点进行系统维护...",
  "is_pinned": 1
}
```

---

## 错误响应

| HTTP状态码 | 错误代码 | 说明 |
|-------------|----------|------|
| 400 | - | 请求参数错误 |
| 401 | AUTH_REQUIRED | 需要认证 |
| 401 | INVALID_TOKEN | Token无效 |
| 403 | ADMIN_REQUIRED | 需要管理员权限 |
| 404 | - | 资源不存在 |
| 409 | - | 资源冲突 |
| 500 | - | 服务器内部错误 |

**错误响应示例**:

```json
{
  "error": "Authentication required",
  "code": "AUTH_REQUIRED"
}
```

---

## 启动服务

```bash
cd e:\PetWise\Backend
pip install -r requirements.txt
python app.py
```

服务将在 `http://localhost:5000` 启动，首次运行自动创建 SQLite 数据库。

---

## AI Agent 服务

后端通过 HTTP 调用 `http://localhost:8000` 的 AI Agent 服务。如需使用完整 AI 功能，请先启动 ai_agent 服务：

```bash
cd e:\PetWise\ai_agent
pip install -r requirements.txt
python main.py
```

---

## 默认管理员

注册用户名为 `admin` 的账号将自动设置为管理员角色。

---

## 13. 摄像头识别

### 13.1 摄像头单帧识别

```http
POST /api/recognize/camera
Authorization: <token>
Content-Type: application/json

{
  "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQE...",
  "session_id": "camera_session_001"
}
```

**响应**:
```json
{
  "success": true,
  "result": {
    "breed": "柴犬",
    "confidence": 0.9876,
    "category": "dog",
    "top5": [...]
  },
  "breed_info": {...},
  "model_available": true,
  "session_id": "camera_session_001"
}
```

### 13.2 摄像头批量识别

```http
POST /api/recognize/camera/stream
Authorization: <token>
Content-Type: application/json

{
  "images": ["base64_image_1", "base64_image_2", "base64_image_3"],
  "session_id": "camera_session_001"
}
```

---

## 14. 大模型管理（管理员）

### 14.1 获取大模型列表

```http
GET /api/admin/models
Authorization: <admin_token>
```

### 14.2 添加大模型

```http
POST /api/admin/models
Authorization: <admin_token>
Content-Type: application/json

{
  "name": "DeepSeek-V3",
  "provider": "siliconflow",
  "api_key": "sk-xxx",
  "base_url": "https://api.siliconflow.cn/v1",
  "model_name": "deepseek-ai/DeepSeek-V3",
  "max_tokens": 4096,
  "temperature": 0.7,
  "top_p": 0.9,
  "is_active": 1,
  "is_default": 1,
  "description": "强大的开源大模型"
}
```

### 14.3 设置默认模型

```http
POST /api/admin/models/default/1
Authorization: <admin_token>
```

---

## 15. 知识库管理（管理员）

### 15.1 获取知识库列表

```http
GET /api/admin/knowledge?page=1&per_page=20&category=health
Authorization: <admin_token>
```

### 15.2 添加知识库

```http
POST /api/admin/knowledge
Authorization: <admin_token>
Content-Type: application/json

{
  "title": "猫咪常见疾病预防",
  "content": "猫咪常见疾病包括...",
  "category": "health",
  "tags": "猫咪,疾病,预防",
  "source": "专业兽医"
}
```

### 15.3 更新知识库

```http
PUT /api/admin/knowledge/1
Authorization: <admin_token>
Content-Type: application/json

{
  "title": "更新后的标题",
  "content": "更新后的内容"
}
```

### 15.4 删除知识库

```http
DELETE /api/admin/knowledge/1
Authorization: <admin_token>
```

### 15.5 获取知识库分类统计

```http
GET /api/admin/knowledge/categories
Authorization: <admin_token>
```

**响应**:
```json
{
  "success": true,
  "data": [
    {"category": "health", "count": 15},
    {"category": "feeding", "count": 10},
    {"category": "training", "count": 8}
  ]
}
```