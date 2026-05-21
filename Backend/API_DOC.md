# PetWise API 接口文档 v3.0

## 概述

PetWise API v3.0 是一个功能完善的用户系统，包含用户角色（管理员/普通用户）、SQLite 数据库、功能丰富的宠物服务平台。

**基础 URL**: `http://localhost:5000`

### 核心功能

- 👤 **用户认证系统** - 注册、登录、Token 认证
- 🔐 **角色权限管理** - 管理员(admin)和普通用户(user)
- 📸 **宠物品种识别** - 基于 EfficientNet-B3
- 🤖 **AI 智能体对话** - 基于大语言模型
- 🐾 **宠物档案管理** - 用户宠物管理
- ⭐ **收藏与评论** - 宠物品种收藏、评分评论
- 📊 **系统管理后台** - 用户管理、统计日志
- 📢 **公告系统** - 系统公告发布

### 数据库

使用 **SQLite** 数据库，文件位置：`e:\PetWise\Backend\petwise.db`

#### 数据表

| 表名 | 说明 |
|------|------|
| users | 用户表 |
| pets | 宠物档案表 |
| recognitions | 识别记录表 |
| chat_history | 对话历史表 |
| favorites | 收藏表 |
| breed_info | 品种信息表 |
| comments | 评论表 |
| system_logs | 系统日志表 |
| announcements | 公告表 |
| feedback | 用户反馈表 |

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

### 宠物识别 (3个)

| 方法 | 路径 | 认证 | 描述 |
|------|------|------|------|
| POST | `/api/recognize` | ✅ | 识别宠物品种 |
| GET | `/api/recognize/history` | ✅ | 识别历史记录 |
| GET | `/api/classes` | ❌ | 获取所有宠物类别 |

### AI智能体 (3个)

| 方法 | 路径 | 认证 | 描述 |
|------|------|------|------|
| POST | `/api/agent/chat` | ✅ | AI对话 |
| GET | `/api/agent/history` | ✅ | 对话历史 |
| DELETE | `/api/agent/history` | ✅ | 清除对话历史 |

### 宠物档案 (5个)

| 方法 | 路径 | 认证 | 描述 |
|------|------|------|------|
| GET | `/api/pets` | ✅ | 我的宠物列表 |
| POST | `/api/pets` | ✅ | 添加宠物 |
| GET | `/api/pets/<id>` | ✅ | 宠物详情 |
| PUT | `/api/pets/<id>` | ✅ | 更新宠物 |
| DELETE | `/api/pets/<id>` | ✅ | 删除宠物 |

### 收藏与评论 (5个)

| 方法 | 路径 | 认证 | 描述 |
|------|------|------|------|
| GET | `/api/favorites` | ✅ | 我的收藏 |
| POST | `/api/favorites` | ✅ | 添加收藏 |
| DELETE | `/api/favorites/<breed>` | ✅ | 取消收藏 |
| GET | `/api/comments/<breed>` | ❌ | 评论列表 |
| POST | `/api/comments` | ✅ | 添加评论 |

### 其他接口 (2个)

| 方法 | 路径 | 认证 | 描述 |
|------|------|------|------|
| GET | `/api/breed/<breed>` | ❌ | 品种详情 |
| POST | `/api/feedback` | ✅ | 提交反馈 |

### 管理员接口 (8个)

| 方法 | 路径 | 认证 | 描述 |
|------|------|------|------|
| GET | `/api/admin/users` | ✅Admin | 用户管理 |
| PUT | `/api/admin/users/<id>` | ✅Admin | 更新用户 |
| GET | `/api/admin/stats` | ✅Admin | 系统统计 |
| GET | `/api/admin/logs` | ✅Admin | 操作日志 |
| GET | `/api/admin/announcements` | ❌ | 获取公告 |
| POST | `/api/admin/announcements` | ✅Admin | 发布公告 |
| GET | `/api/admin/feedback` | ✅Admin | 用户反馈 |
| PUT | `/api/admin/feedback/<id>` | ✅Admin | 回复反馈 |
| PUT | `/api/admin/breeds/<breed>` | ✅Admin | 更新品种信息 |

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
  }
}
```

---

## 6. AI智能体对话

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

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| message | string | ✅ | 用户问题 |
| session_id | string | ❌ | 会话ID（默认default） |
| breed_context | string | ❌ | 宠物上下文 |

### 响应

```json
{
  "success": true,
  "session_id": "user123",
  "response": "关于英国短毛猫的饲养建议...",
  "model": "microsoft/phi-2",
  "suggestions": [
    "告诉我关于英国短毛猫的性格特点",
    "英国短毛猫容易患什么疾病？",
    "如何训练英国短毛猫？"
  ]
}
```

---

## 7. 宠物档案管理

### 7.1 添加宠物

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

### 7.2 获取宠物列表

```http
GET /api/pets
Authorization: <token>
```

### 7.3 获取宠物详情

```http
GET /api/pets/1
Authorization: <token>
```

### 7.4 更新宠物

```http
PUT /api/pets/1
Authorization: <token>
Content-Type: application/json

{
  "name": "小白白",
  "age": 3
}
```

### 7.5 删除宠物

```http
DELETE /api/pets/1
Authorization: <token>
```

---

## 8. 收藏与评论

### 8.1 添加收藏

```http
POST /api/favorites
Authorization: <token>
Content-Type: application/json

{
  "breed": "英国短毛猫"
}
```

### 8.2 我的收藏

```http
GET /api/favorites
Authorization: <token>
```

### 8.3 取消收藏

```http
DELETE /api/favorites/英国短毛猫
Authorization: <token>
```

### 8.4 获取评论

```http
GET /api/comments/英国短毛猫?page=1&per_page=10
```

### 8.5 添加评论

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

## 9. 管理员接口

### 9.1 获取用户列表

```http
GET /api/admin/users?page=1&per_page=20&role=user
Authorization: <admin_token>
```

### 9.2 更新用户

```http
PUT /api/admin/users/1
Authorization: <admin_token>
Content-Type: application/json

{
  "role": "admin",
  "is_active": 1
}
```

### 9.3 系统统计

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
  "breed_stats": [
    {"breed": "英国短毛猫", "views": 1000, "likes": 100, "comment_count": 50}
  ],
  "recent_registrations": [
    {"username": "user1", "created_at": "2024-01-15"}
  ],
  "daily_recognitions": [
    {"date": "2024-01-15", "count": 100}
  ]
}
```

### 9.4 操作日志

```http
GET /api/admin/logs?page=1&per_page=50
Authorization: <admin_token>
```

### 9.5 发布公告

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

### 9.6 回复反馈

```http
PUT /api/admin/feedback/1
Authorization: <admin_token>
Content-Type: application/json

{
  "reply": "感谢您的反馈，我们已经处理..."
}
```

### 9.7 更新品种信息

```http
PUT /api/admin/breeds/英国短毛猫
Authorization: <admin_token>
Content-Type: application/json

{
  "personality": "安静、温和、亲人、粘人",
  "common_issues": "心脏病、肥胖、肾脏疾病、眼部问题"
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

## 环境要求

- Python 3.8+
- Flask 2.0+
- PyTorch 2.0+
- transformers 4.30+
- torchvision 0.15+
- Pillow 9.0+

---

## 默认管理员

注册用户名为 `admin` 的账号将自动设置为管理员角色。

示例：

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

然后使用 admin/admin123 登录即可访问所有管理员接口。