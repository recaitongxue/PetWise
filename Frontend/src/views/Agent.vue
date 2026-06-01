<template>
  <div class="agent-page">
    <Navbar />
    
    <div class="container">
      <h1 class="page-title">🤖 AI智能助手</h1>
      
      <div class="chat-container">
        <div class="chat-messages" ref="messagesContainer">
          <div 
            v-for="(message, index) in messages" 
            :key="index" 
            class="message-item"
            :class="{ 'is-user': message.isUser }"
          >
            <div class="avatar">{{ message.isUser ? '👤' : '🤖' }}</div>
            <div class="message-content">
              <p>{{ message.content }}</p>
              <span class="time">{{ message.time }}</span>
            </div>
          </div>
          
          <div v-if="isTyping" class="typing-indicator">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
          </div>
        </div>
        
        <div class="chat-input">
          <input 
            v-model="inputMessage" 
            type="text" 
            placeholder="输入您的问题..."
            @keyup.enter="sendMessage"
          />
          <button @click="sendMessage" :disabled="!inputMessage || isTyping">
            发送
          </button>
        </div>
      </div>
      
      <div class="quick-actions">
        <h3>快捷功能</h3>
        <div class="action-grid">
          <button class="action-btn" @click="getAdvice('饮食')">
            🍽️ 饮食建议
          </button>
          <button class="action-btn" @click="getAdvice('训练')">
            🎾 训练指导
          </button>
          <button class="action-btn" @click="getAdvice('健康')">
            🏥 健康咨询
          </button>
          <button class="action-btn danger" @click="handleEmergency">
            🚨 紧急咨询
          </button>
        </div>
      </div>
      
      <div class="history-section">
        <h3>对话历史</h3>
        <div v-if="chatHistory.length" class="history-list">
          <div 
            v-for="item in chatHistory" 
            :key="item.id" 
            class="history-item"
          >
            <p class="history-content">{{ item.content }}</p>
            <span class="history-time">{{ item.created_at }}</span>
          </div>
        </div>
        <div v-else class="empty-history">
          <p>暂无对话记录</p>
        </div>
        <button class="clear-history-btn" @click="clearHistory">
          清空对话历史
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import Navbar from '@/components/Navbar.vue'
import { agentAPI } from '@/api/agent'

const messages = ref([
  {
    isUser: false,
    content: '您好！我是PetWise AI助手，有什么可以帮助您的吗？',
    time: new Date().toLocaleTimeString()
  }
])
const inputMessage = ref('')
const isTyping = ref(false)
const chatHistory = ref([])
const messagesContainer = ref(null)

const addMessage = (content, isUser) => {
  messages.value.push({
    isUser,
    content,
    time: new Date().toLocaleTimeString()
  })
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message) return
  
  addMessage(message, true)
  inputMessage.value = ''
  isTyping.value = true
  
  try {
    const response = await agentAPI.chat({
      message,
      session_id: 'session_' + Date.now()
    })
    
    if (response.success) {
      addMessage(response.response, false)
      
      if (response.suggestions) {
        response.suggestions.forEach(suggestion => {
          addMessage(`💡 建议：${suggestion}`, false)
        })
      }
    }
  } catch (error) {
    addMessage('抱歉，暂时无法回答您的问题。', false)
    ElMessage.error('请求失败')
  } finally {
    isTyping.value = false
  }
}

const getAdvice = async (topic) => {
  isTyping.value = true
  
  try {
    const response = await agentAPI.getAdvice({
      topic,
      pet_type: 'cat',
      specific_issue: topic + '建议'
    })
    
    if (response.success) {
      addMessage(`您询问的是「${topic}」相关建议：`, false)
      addMessage(response.advice, false)
    }
  } catch (error) {
    ElMessage.error('请求失败')
  } finally {
    isTyping.value = false
  }
}

const handleEmergency = async () => {
  const symptoms = prompt('请描述宠物的症状：')
  if (!symptoms) return
  
  isTyping.value = true
  
  try {
    const response = await agentAPI.emergency({
      symptoms,
      pet_type: 'cat',
      severity: 'high'
    })
    
    if (response.success) {
      addMessage(`⚠️ 紧急咨询结果：`, false)
      addMessage(response.consultation, false)
      if (response.recommendation === 'seek_immediate_medical_attention') {
        addMessage('🚨 建议：请立即联系兽医！', false)
      }
    }
  } catch (error) {
    ElMessage.error('请求失败')
  } finally {
    isTyping.value = false
  }
}

const loadHistory = async () => {
  try {
    const response = await agentAPI.getHistory()
    if (response.success) {
      chatHistory.value = response.data || []
    }
  } catch (error) {
    console.log('Failed to load chat history:', error)
  }
}

const clearHistory = async () => {
  try {
    const response = await agentAPI.clearHistory()
    if (response.success) {
      ElMessage.success('已清空对话历史')
      chatHistory.value = []
      messages.value = [{
        isUser: false,
        content: '您好！我是PetWise AI助手，有什么可以帮助您的吗？',
        time: new Date().toLocaleTimeString()
      }]
    }
  } catch (error) {
    ElMessage.error('清空失败')
  }
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.agent-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 30px 20px;
}

.page-title {
  text-align: center;
  font-size: 28px;
  margin-bottom: 30px;
}

.chat-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.chat-messages {
  height: 400px;
  overflow-y: auto;
  padding: 20px;
}

.message-item {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.message-item.is-user {
  flex-direction: row-reverse;
}

.message-item.is-user .message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px 16px 4px 16px;
}

.message-item.is-user .time {
  color: rgba(255, 255, 255, 0.7);
}

.avatar {
  font-size: 32px;
  flex-shrink: 0;
}

.message-content {
  background: #f0f2f5;
  padding: 12px 16px;
  border-radius: 16px 16px 16px 4px;
  max-width: 70%;
}

.message-content p {
  margin: 0;
  word-break: break-word;
}

.time {
  display: block;
  font-size: 11px;
  color: #999;
  margin-top: 5px;
}

.typing-indicator {
  display: flex;
  gap: 5px;
  padding: 12px;
  background: #f0f2f5;
  border-radius: 16px;
  width: fit-content;
}

.typing-dot {
  width: 8px;
  height: 8px;
  background: #999;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 80%, 100% {
    opacity: 0.4;
    transform: scale(0.8);
  }
  40% {
    opacity: 1;
    transform: scale(1);
  }
}

.chat-input {
  display: flex;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #eee;
}

.chat-input input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 24px;
  font-size: 14px;
}

.chat-input button {
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 24px;
  cursor: pointer;
  font-size: 14px;
}

.chat-input button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.quick-actions {
  margin-top: 30px;
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.quick-actions h3 {
  margin-bottom: 15px;
  font-size: 16px;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
}

.action-btn {
  padding: 12px;
  background: #f5f7fa;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #eee;
}

.action-btn.danger {
  background: #fff2f0;
  color: #f56c6c;
}

.action-btn.danger:hover {
  background: #ffccc7;
}

.history-section {
  margin-top: 30px;
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.history-section h3 {
  margin-bottom: 15px;
  font-size: 16px;
}

.history-list {
  max-height: 200px;
  overflow-y: auto;
}

.history-item {
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
  margin-bottom: 10px;
}

.history-content {
  margin: 0;
  font-size: 14px;
  color: #333;
}

.history-time {
  display: block;
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.empty-history {
  text-align: center;
  padding: 30px;
  color: #999;
}

.clear-history-btn {
  margin-top: 15px;
  padding: 8px 16px;
  background: #fff2f0;
  border: none;
  border-radius: 6px;
  color: #f56c6c;
  cursor: pointer;
  font-size: 12px;
}

.clear-history-btn:hover {
  background: #ffccc7;
}
</style>