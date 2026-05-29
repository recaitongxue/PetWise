# PetWise AI Agent Service

宠物智能识别和服务系统的AI模型板块，提供智能对话、知识库管理、宠物护理建议等功能。

## 功能特性

### 🤖 智能对话
- 基于硅基流动API的大语言模型集成
- 支持多模型选择（DeepSeek-V3、Qwen2、Llama-3等）
- 自定义温度参数调节响应风格
- 支持流式响应（Server-Sent Events）

### 📚 知识库管理
- 完整的宠物知识体系（品种、医疗、护理、训练）
- 支持知识的增删改查（CRUD）
- 智能知识检索和匹配
- 知识库与AI对话的深度融合

### 🐾 宠物服务
- 宠物品种识别与介绍
- 健康咨询与医疗建议
- 日常护理指南
- 行为训练指导
- 紧急情况处理

### ⚙️ 系统配置
- 系统提示词管理
- 自定义提示词支持
- 灵活的配置选项

## 技术栈

- **框架**: FastAPI 0.100+
- **语言**: Python 3.9+
- **AI服务**: 硅基流动 (SiliconFlow)
- **模型**: DeepSeek-V3、Qwen2、Llama-3等

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置API密钥：

```env
SILICONFLOW_API_KEY=your-api-key-here
SILICONFLOW_MODEL=deepseek-ai/DeepSeek-V3
API_HOST=0.0.0.0
API_PORT=8000
```

### 3. 启动服务

```bash
python main.py
```

### 4. 访问服务

- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 项目结构

```
ai_agent/
├── main.py                    # 主入口文件
├── api.py                     # FastAPI接口定义
├── ai_service.py              # AI服务核心逻辑
├── siliconflow_client.py      # 硅基流动API客户端
├── knowledge_base.py          # 知识库管理模块
├── prompt_manager.py          # 提示词管理模块
├── config.py                  # 配置管理
├── utils.py                   # 工具函数
├── exceptions.py              # 异常定义
├── requirements.txt           # 依赖包列表
├── .env                       # 环境变量（需创建）
├── .env.example               # 环境变量示例
├── knowledge_base/            # 知识库数据
│   └── pet_knowledge.json     # 宠物知识数据（27+条目）
├── prompts/                   # 提示词目录
│   └── system_prompt.txt      # 系统提示词
└── README.md                  # 项目说明文档
```

## API接口

### 智能对话

| 接口 | 方法 | 描述 |
|------|------|------|
| `/chat` | POST | 智能对话（同步） |
| `/stream` | POST | 智能对话（流式） |
| `/models` | GET | 获取可用模型列表 |

**请求示例**：

```json
{
  "user_message": "我的狗狗最近不爱吃东西怎么办？",
  "use_knowledge_base": true,
  "temperature": 0.7,
  "model": "deepseek-ai/DeepSeek-V3"
}
```

### 知识库管理

| 接口 | 方法 | 描述 |
|------|------|------|
| `/knowledge/stats` | GET | 获取知识库统计 |
| `/knowledge/categories` | GET | 获取知识分类 |
| `/knowledge/{id}` | GET | 获取单条知识 |
| `/knowledge/query` | POST | 搜索知识库 |
| `/knowledge/import` | POST | 添加/导入知识 |
| `/knowledge` | PUT | 更新知识 |
| `/knowledge/{id}` | DELETE | 删除知识 |

### 宠物护理

| 接口 | 方法 | 描述 |
|------|------|------|
| `/advice` | POST | 获取宠物护理建议 |
| `/emergency` | POST | 紧急情况咨询 |

### 图像分析（预留）

| 接口 | 方法 | 描述 |
|------|------|------|
| `/analyze-image` | POST | 图像分析 |
| `/upload-image` | POST | 上传并分析图像 |

### 提示词管理

| 接口 | 方法 | 描述 |
|------|------|------|
| `/prompts/system` | GET | 获取系统提示词 |
| `/prompts/custom` | POST | 创建自定义提示词 |

### 系统信息

| 接口 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 根路径 |
| `/health` | GET | 健康检查 |
| `/info` | GET | 服务信息 |

## 知识库内容

当前知识库包含 **27+条** 宠物相关知识：

| 分类 | 条目数 | 内容 |
|------|--------|------|
| 狗狗品种 | 5 | 金毛、泰迪、哈士奇、斗牛犬、柯基 |
| 猫咪品种 | 5 | 波斯猫、英短、布偶、美短、无毛猫 |
| 宠物医疗 | 5 | 疫苗接种、寄生虫预防、口腔护理、急救处理、营养饮食 |
| 日常护理 | 4 | 美容护理、运动锻炼、居住环境、出行指南 |
| 行为训练 | 4 | 基础训练、如厕训练、行为问题、社会化 |
| 老年护理 | 3 | 衰老迹象、护理要点、常见疾病 |

## 可用AI模型

| 模型名称 | 描述 | 上下文窗口 |
|---------|------|-----------|
| `deepseek-ai/DeepSeek-V3` | DeepSeek-V3大语言模型 | 128K |
| `Qwen/Qwen2-7B-Instruct` | Qwen2-7B指令模型 | 32K |
| `Qwen/Qwen2-14B-Instruct` | Qwen2-14B指令模型 | 32K |
| `Llama-3-8B-Instruct` | Llama 3 8B指令模型 | 8K |
| `Llama-3-70B-Instruct` | Llama 3 70B指令模型 | 8K |

## 使用示例

### Python客户端

```python
import requests

# 智能对话
response = requests.post("http://localhost:8000/chat", json={
    "user_message": "我的猫咪呕吐怎么办？",
    "use_knowledge_base": True,
    "temperature": 0.7
})
print(response.json()["content"])

# 获取护理建议
response = requests.post("http://localhost:8000/advice", json={
    "topic": "饮食",
    "pet_type": "狗狗",
    "specific_issue": "食欲不振"
})
print(response.json()["advice"])

# 查询知识库
response = requests.post("http://localhost:8000/knowledge/query", json={
    "query": "疫苗",
    "limit": 3
})
print(response.json()["results"])
```

### 命令行测试

```bash
# 健康检查
curl http://localhost:8000/health

# 智能对话
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_message": "如何给狗狗洗澡？", "use_knowledge_base": true}'

# 获取模型列表
curl http://localhost:8000/models
```

## 配置说明

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SILICONFLOW_API_KEY` | 硅基流动API密钥 | - |
| `SILICONFLOW_API_URL` | API地址 | https://api.siliconflow.cn/v1 |
| `SILICONFLOW_MODEL` | 默认模型 | deepseek-ai/DeepSeek-V3 |
| `API_HOST` | 服务主机 | 0.0.0.0 |
| `API_PORT` | 服务端口 | 8000 |
| `LOG_LEVEL` | 日志级别 | INFO |

## 开发指南

### 添加新的知识库条目

```python
# 通过API添加
import requests

new_knowledge = {
    "title": "新知识点标题",
    "content": {"key": "value"}
}

response = requests.post("http://localhost:8000/knowledge/import", json={
    "knowledge_data": new_knowledge,
    "category": "general"
})
```

### 自定义提示词

```python
# 创建自定义提示词
response = requests.post("http://localhost:8000/prompts/custom", json={
    "name": "简洁回答",
    "content": "请用最简短的语言回答问题，不超过3句话。",
    "description": "用于快速获取简洁答案"
})
```

## 集成说明

### 后端集成

```python
from ai_service import AIAgentService

# 初始化服务
ai_service = AIAgentService()

# 使用服务
response = ai_service.chat(
    user_message="问题",
    use_knowledge_base=True,
    temperature=0.7
)
```

### 前端集成

```javascript
// 使用fetch API
const response = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_message: '问题',
    use_knowledge_base: true,
    temperature: 0.7
  })
});
const result = await response.json();
```

## 注意事项

1. **API密钥安全**: 请妥善保管API密钥，不要提交到代码仓库
2. **模型权限**: 部分模型可能需要额外的权限或配额
3. **知识库更新**: 修改知识库后需要重启服务才能生效
4. **网络要求**: 需要网络连接才能访问硅基流动API

## 许可证

MIT License

---

🐾 **PetWise AI Agent Service** - 为宠物智能识别和服务提供强大的AI支持