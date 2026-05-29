# PetWise Backend

PetWise 宠物识别平台后端服务，基于 Flask 框架开发，提供宠物品种识别、AI智能体对话、用户管理等完整功能。

---

## 📋 项目概述

### 已完成功能

| 模块 | 功能描述 | 状态 |
|------|----------|------|
| **用户认证** | 注册、登录、登出、个人信息管理 | ✅ 完成 |
| **角色管理** | 管理员/普通用户角色区分 | ✅ 完成 |
| **宠物识别** | 图片识别、Base64识别、识别历史 | ✅ 完成 |
| **AI智能体** | 对话、养宠建议、紧急咨询 | ✅ 完成 |
| **宠物档案** | 创建、查看、更新、删除 | ✅ 完成 |
| **收藏系统** | 品种收藏、取消收藏 | ✅ 完成 |
| **评论系统** | 评论、评分、点赞 | ✅ 完成 |
| **系统管理** | 用户管理、统计、日志、公告 | ✅ 完成 |
| **数据持久化** | SQLite数据库存储 | ✅ 完成 |

### 技术栈

- **框架**: Flask 3.1.x
- **数据库**: SQLite
- **AI模型**: PyTorch + EfficientNet-B3 (宠物识别)
- **AI Agent**: 调用外部服务 `http://localhost:8000`
- **认证**: Session + Token

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Conda 环境 (推荐)
- PyTorch 2.5.0 (含 CUDA 支持)

### 安装依赖

```bash
# 激活 conda 环境
conda activate petwise

# 安装依赖
pip install flask torch torchvision pillow requests
```

### 启动服务

```bash
cd e:\PetWise\Backend
python app.py
```

服务将在 `http://localhost:5000` 启动，首次运行自动创建数据库。

### AI Agent 服务 (可选)

如需使用完整的 AI 智能体功能，请先启动 AI Agent 服务：

```bash
cd e:\PetWise\ai_agent
python main.py
```

---

## 🔌 API 接口

### 接口总览

| 模块 | 接口数 | 认证要求 |
|------|--------|----------|
| 认证 | 5 | 登录后 |
| 宠物识别 | 6 | 登录后 |
| AI智能体 | 7 | 登录后 |
| 宠物档案 | 5 | 登录后 |
| 收藏评论 | 6 | 登录后 |
| 管理员 | 9 | 管理员 |
| 公共接口 | 3 | 无需认证 |

### 核心接口示例

**1. 用户注册**
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "password": "123456",
  "email": "test@example.com"
}
```

**2. 用户登录**
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "testuser",
  "password": "123456"
}
```

**3. 宠物识别**
```http
POST /api/recognize
Content-Type: multipart/form-data

image: <file>
```

**4. AI对话**
```http
POST /api/agent/chat
Authorization: <token>
Content-Type: application/json

{
  "message": "英国短毛猫好养吗？",
  "breed_context": "英国短毛猫"
}
```

**5. 添加宠物档案**
```http
POST /api/pets
Authorization: <token>
Content-Type: application/json

{
  "name": "小白",
  "breed": "英国短毛猫",
  "category": "cat",
  "age": 2,
  "gender": "male"
}
```

---

## 🐾 支持的宠物品种

### 猫类 (12种)
- 阿比西尼亚猫
- 埃及猫
- 豹猫
- 布偶猫
- 波斯猫
- 缅甸猫
- 俄罗斯蓝猫
- 孟买猫
- 缅因猫
- 无毛猫
- 暹罗猫
- 英国短毛猫

### 犬类 (11种)
- 中华田园犬
- 吉娃娃
- 哈士奇
- 德牧
- 拉布拉多
- 杜宾
- 柴犬
- 法国斗牛
- 萨摩耶
- 藏獒
- 金毛

---

## 🗂️ 项目结构

```
Backend/
├── app.py                    # 主应用入口
├── config.py                 # 配置管理
├── API_DOC.md                # 接口文档
├── petwise.db                # SQLite数据库
├── requirements.txt          # 依赖列表
├── models/
│   └── db.py                 # 数据库操作模块
├── routes/
│   ├── auth.py               # 用户认证路由
│   ├── recognize.py          # 宠物识别路由
│   ├── agent.py              # AI智能体路由
│   ├── pets.py               # 宠物档案路由
│   ├── favorites.py          # 收藏管理路由
│   ├── comments.py           # 评论系统路由
│   ├── admin.py              # 管理员后台路由
│   └── other.py              # 其他公共路由
├── services/
│   └── ai_agent_client.py    # AI Agent客户端
├── utils/
│   └── __init__.py           # 工具函数
└── uploads/                  # 图片上传目录
```

---

## 🎯 前端功能建议

### 核心页面

| 页面 | 功能描述 | 对接接口 |
|------|----------|----------|
| **首页** | 展示宠物识别入口、热门品种 | `/api/classes`, `/api/admin/announcements` |
| **识别页** | 图片上传、识别结果展示 | `/api/recognize`, `/api/recognize/base64` |
| **AI助手** | 智能对话、养宠建议、紧急咨询 | `/api/agent/chat`, `/api/agent/advice`, `/api/agent/emergency` |
| **我的宠物** | 宠物档案管理 | `/api/pets`, `/api/pets/{id}` |
| **识别历史** | 查看历史识别记录 | `/api/recognize/history` |
| **品种百科** | 查看品种详情、收藏、评论 | `/api/breed/{breed}`, `/api/favorites`, `/api/comments` |
| **个人中心** | 用户信息、统计数据 | `/api/auth/profile` |
| **管理员后台** | 用户管理、统计分析、公告管理 | `/api/admin/*` |

### 功能模块设计

#### 1. 宠物识别模块
- 图片上传（拍照/相册选择）
- Base64 图片识别
- 识别结果展示（置信度、Top5结果）
- 品种信息展示
- 识别历史记录

#### 2. AI智能体模块
- 实时对话界面
- 对话历史记录
- 养宠建议分类（饮食、护理、健康等）
- 紧急咨询入口（高亮显示）

#### 3. 宠物档案模块
- 宠物列表展示
- 添加/编辑/删除宠物
- 宠物信息展示（名称、品种、年龄、性别）

#### 4. 社交互动模块
- 品种收藏
- 评论评分
- 评论点赞

#### 5. 用户中心模块
- 个人信息展示/编辑
- 统计数据（识别次数、宠物数量、收藏数）
- 登录/注册/退出

#### 6. 管理员模块
- 用户列表管理
- 系统统计仪表盘
- 操作日志查看
- 公告发布管理
- 用户反馈处理

### UI/UX 建议

1. **识别流程**：简洁直接，支持拖拽上传
2. **对话界面**：类似聊天APP的气泡式设计
3. **紧急咨询**：醒目的入口和快速响应
4. **响应式设计**：支持移动端和PC端
5. **加载状态**：识别和对话时显示加载动画

---

## 🔐 管理员权限

注册用户名为 `admin` 的账号将自动获得管理员权限。

### 管理员功能
- 用户管理（查看、修改角色）
- 系统统计数据查看
- 操作日志查看
- 公告发布与管理
- 用户反馈处理
- 品种信息管理

---

## 📝 配置说明

主要配置项（`config.py`）：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `SECRET_KEY` | 会话密钥 | 自动生成 |
| `DATABASE` | 数据库路径 | `petwise.db` |
| `UPLOAD_FOLDER` | 上传目录 | `uploads/` |
| `MODEL_PATH` | 模型文件路径 | `../model/best_model.pth` |
| `ALLOWED_EXTENSIONS` | 允许的图片格式 | `{'png', 'jpg', 'jpeg', 'gif'}` |
| `AGENT_BASE_URL` | AI Agent地址 | `http://localhost:8000` |

---

## 📄 接口文档

完整的 API 接口文档请查看：`API_DOC.md`

---

## 📮 联系方式

如有问题或建议，请联系开发团队。