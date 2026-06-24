<template>
  <div class="agent-page">
    <Navbar />
    
    <div class="main-container" :class="{ 'show-consultation': showConsultation }">
      <!-- 左侧历史记录面板 -->
      <aside v-if="!showConsultation" class="sidebar">
        <div class="sidebar-header">
          <h2>🤖 AI助手</h2>
          <button class="new-chat-btn" @click="createNewChat">
            + 新对话
          </button>
        </div>
        
        <div class="chat-history">
          <div 
            v-for="chat in chatSessions" 
            :key="chat.id" 
            class="chat-item"
            :class="{ active: currentChatId === chat.id }"
            @click="switchChat(chat.id)"
          >
            <div class="chat-preview">
              <span class="chat-icon">💬</span>
              <div class="chat-info">
                <span class="chat-title">{{ chat.title }}</span>
                <span class="chat-time">{{ chat.updated_at }}</span>
              </div>
            </div>
            <button class="delete-chat-btn" @click.stop="deleteChat(chat.id)">
              ×
            </button>
          </div>
          
          <div v-if="chatSessions.length === 0" class="empty-history">
            <span class="empty-icon">📭</span>
            <p>暂无对话记录</p>
            <button class="new-chat-btn primary" @click="createNewChat">
              开始新对话
            </button>
          </div>
        </div>
        
        <div class="sidebar-footer">
          <button class="consultation-btn" @click="toggleConsultation">
            🏥 结构化问诊
          </button>
        </div>
      </aside>
      
      <!-- 右侧主内容区域 -->
      <main class="main-content">
        <!-- 对话模式 -->
        <div v-if="!showConsultation" class="chat-container">
          <div class="chat-header">
            <div class="chat-info">
              <span class="status-indicator" :class="{ online: agentOnline }"></span>
              <span>{{ agentOnline ? 'AI助手在线' : 'AI助手离线' }}</span>
            </div>
            <div class="chat-actions">
              <label class="stream-toggle">
                <input type="checkbox" v-model="useStream" />
                <span>流式输出</span>
              </label>
            </div>
          </div>
          
          <div class="chat-messages" ref="messagesContainer">
            <div v-if="!currentChat" class="welcome-screen">
              <span class="welcome-icon">🐾</span>
              <h3>欢迎使用PetWise AI助手</h3>
              <p>我可以帮您解答关于宠物护理、饮食、健康等方面的问题</p>
              <div class="quick-start">
                <button class="quick-btn" @click="startQuickChat('狗狗饮食注意事项')">🍽️ 饮食建议</button>
                <button class="quick-btn" @click="startQuickChat('狗狗训练方法')">🎾 训练指导</button>
                <button class="quick-btn" @click="startQuickChat('日常护理技巧')">🛁 日常护理</button>
              </div>
            </div>
            
            <template v-else>
              <div 
                v-for="(message, index) in currentChat.messages" 
                :key="index" 
                class="message-item"
                :class="{ 'is-user': message.isUser, 'is-error': message.isError }"
              >
                <div class="avatar">{{ message.isUser ? '👤' : (message.isError ? '❌' : '🤖') }}</div>
                <div class="message-content">
                  <div v-if="message.isStreaming" class="streaming-text">
                    {{ message.displayedContent }}<span class="cursor">|</span>
                  </div>
                  <div v-else class="markdown-content" v-html="parseMarkdown(message.content)"></div>
                  <span class="time">{{ message.time }}</span>
                  <button 
                    v-if="!message.isUser && !message.isError" 
                    class="follow-up-btn"
                    @click="followUpOnMessage(message)"
                  >
                    ↩️ 追问
                  </button>
                </div>
              </div>
              
              <div v-if="isTyping && !useStream" class="typing-indicator">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
              </div>
            </template>
          </div>
          
          <div v-if="currentChat" class="chat-input">
            <select v-model="selectedPet" class="pet-select">
              <option value="">选择宠物档案</option>
              <option v-for="pet in pets" :key="pet.id" :value="pet.id">
                {{ pet.name }} ({{ pet.breed }})
              </option>
            </select>
            <input 
              v-model="inputMessage" 
              type="text" 
              :placeholder="followUpMessage ? `追问: ${followUpMessage.substring(0, 30)}...` : '输入您的问题...'"
              @keyup.enter="sendMessage"
              :disabled="isTyping"
            />
            <button @click="sendMessage" :disabled="!inputMessage || isTyping">
              {{ isTyping ? '发送中...' : '发送' }}
            </button>
          </div>
        </div>
        
        <!-- 结构化问诊模式 -->
        <div v-else class="consultation-container">
          <button class="back-btn" @click="showConsultation = false">
            ← 返回对话
          </button>
          
          <div class="consultation-form">
            <h3>🏥 结构化问诊</h3>
            <p class="form-desc">请详细填写宠物的症状信息，AI将为您提供专业的诊断建议</p>
            
            <div class="form-group">
              <label>选择宠物</label>
              <select v-model="consultationForm.petId">
                <option value="">请选择宠物</option>
                <option v-for="pet in pets" :key="pet.id" :value="pet.id">
                  {{ pet.name }} - {{ pet.breed }} ({{ pet.age }}岁)
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label>主要症状（可多选）</label>
              <div class="symptom-checkboxes">
                <label v-for="symptom in symptoms" :key="symptom" class="symptom-checkbox">
                  <input type="checkbox" :value="symptom" v-model="consultationForm.symptoms" />
                  {{ symptom }}
                </label>
              </div>
            </div>
            
            <div class="form-group">
              <label>发病时长</label>
              <select v-model="consultationForm.duration">
                <option value="">请选择</option>
                <option value="今天">今天</option>
                <option value="1-3天">1-3天</option>
                <option value="3-7天">3-7天</option>
                <option value="1-2周">1-2周</option>
                <option value="2周以上">2周以上</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>严重程度</label>
              <div class="severity-slider">
                <input type="range" min="1" max="5" v-model="consultationForm.severity" />
                <div class="severity-labels">
                  <span>轻微</span>
                  <span>中等</span>
                  <span>严重</span>
                </div>
              </div>
            </div>
            
            <div class="form-group">
              <label>补充信息</label>
              <textarea 
                v-model="consultationForm.additionalInfo" 
                placeholder="其他需要说明的情况..."
                rows="4"
              ></textarea>
            </div>
            
            <button class="submit-btn" @click="submitConsultation" :disabled="!canSubmitConsultation">
              提交问诊
            </button>
          </div>
          
          <div v-if="consultationResult" class="consultation-result">
            <div class="result-header">
              <h3>问诊结果</h3>
              <div class="result-actions">
                <button class="action-btn export-btn" @click="exportCurrentConsultation">
                  📄 导出MD
                </button>
                <button class="action-btn save-btn" @click="saveConsultationToHealth" :disabled="isSaving || savedRecordId">
                  {{ savedRecordId ? '✅ 已保存' : (isSaving ? '保存中...' : '💾 保存到健康记录') }}
                </button>
              </div>
            </div>
            <div class="result-content" v-html="parseMarkdown(consultationResult)"></div>
            <div class="result-warning">
              ⚠️ 建议：尽快联系宠物医院进行专业诊断
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import Navbar from '@/components/Navbar.vue'
import { agentAPI } from '@/api/agent'
import { petsAPI } from '@/api/pets'
import { healthAPI } from '@/api/health'
import { marked } from 'marked'

const showConsultation = ref(false)
const useStream = ref(false)
const agentOnline = ref(false)
const messagesContainer = ref(null)
const pets = ref([])
const selectedPet = ref('')
const inputMessage = ref('')
const isTyping = ref(false)
const followUpMessage = ref('')

const chatSessions = ref([])
const currentChatId = ref(null)

const consultationForm = reactive({
  petId: '',
  symptoms: [],
  duration: '',
  severity: 3,
  additionalInfo: ''
})

const consultationResult = ref('')
const consultationRecommendation = ref('')
const lastConsultationResponse = ref({})
const isExporting = ref(false)
const isSaving = ref(false)
const savedRecordId = ref(null)

const symptoms = [
  '呕吐', '拉稀', '腹泻', '发烧', '咳嗽', 
  '呼吸困难', '出血', '抽搐', '食欲不振',
  '精神萎靡', '皮肤问题', '眼睛异常'
]

const canSubmitConsultation = computed(() => {
  return consultationForm.petId && 
         consultationForm.symptoms.length > 0 && 
         consultationForm.duration
})

const currentChat = computed(() => {
  return chatSessions.value.find(chat => chat.id === currentChatId.value)
})

const parseMarkdown = (content) => {
  if (!content) return ''
  let cleanedContent = content.trim()
  cleanedContent = cleanedContent.replace(/^```markdown\s*/i, '')
  cleanedContent = cleanedContent.replace(/^```\s*/, '')
  cleanedContent = cleanedContent.replace(/\s*```$/, '')
  return marked.parse(cleanedContent)
}

const loadPets = async () => {
  try {
    const response = await petsAPI.getPets()
    if (response.success) {
      pets.value = response.data || []
    }
  } catch (error) {
    console.error('Failed to load pets:', error)
  }
}

const loadChatHistory = async () => {
  try {
    const response = await agentAPI.getHistory()
    if (response.success) {
      const history = response.history || []
      const sessions = {}
      
      history.forEach(item => {
        const sessionId = item.session_id || 'default'
        if (!sessions[sessionId]) {
          sessions[sessionId] = {
            id: sessionId,
            title: '',
            messages: [],
            updated_at: item.created_at
          }
        }
        sessions[sessionId].messages.push({
          isUser: item.role === 'user',
          content: item.message,
          time: item.created_at?.split(' ')[1] || new Date().toLocaleTimeString(),
          isStreaming: false,
          isError: false,
          displayedContent: ''
        })
        sessions[sessionId].updated_at = item.created_at
      })
      
      Object.values(sessions).forEach(session => {
        const firstUserMsg = session.messages.find(m => m.isUser)
        session.title = firstUserMsg ? 
          (firstUserMsg.content.length > 30 ? firstUserMsg.content.substring(0, 30) + '...' : firstUserMsg.content) :
          '无标题对话'
      })
      
      chatSessions.value = Object.values(sessions).sort((a, b) => 
        new Date(b.updated_at) - new Date(a.updated_at)
      )
      
      if (chatSessions.value.length > 0 && !currentChatId.value) {
        currentChatId.value = chatSessions.value[0].id
      }
    }
  } catch (error) {
    console.error('Failed to load chat history:', error)
  }
}

const createNewChat = () => {
  const newId = Date.now().toString()
  chatSessions.value.unshift({
    id: newId,
    title: '新对话',
    messages: [{
      isUser: false,
      content: '您好！我是PetWise AI助手。请问有什么可以帮到您的？',
      time: new Date().toLocaleTimeString(),
      isStreaming: false,
      displayedContent: ''
    }],
    updated_at: new Date().toLocaleString()
  })
  currentChatId.value = newId
  inputMessage.value = ''
  followUpMessage.value = ''
}

const switchChat = (chatId) => {
  currentChatId.value = chatId
  inputMessage.value = ''
  followUpMessage.value = ''
  nextTick(() => scrollToBottom())
}

const deleteChat = (chatId) => {
  if (!confirm('确定要删除这个对话吗？')) return
  chatSessions.value = chatSessions.value.filter(chat => chat.id !== chatId)
  if (currentChatId.value === chatId) {
    currentChatId.value = chatSessions.value.length > 0 ? chatSessions.value[0].id : null
  }
}

const toggleConsultation = () => {
  showConsultation.value = !showConsultation.value
}

const checkAgentHealth = async () => {
  const maxRetries = 3
  const retryDelay = 2000
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = await agentAPI.healthCheck()
      agentOnline.value = response.status === 'healthy'
      return
    } catch (error) {
      if (attempt < maxRetries) {
        await new Promise(resolve => setTimeout(resolve, retryDelay))
      } else {
        agentOnline.value = false
      }
    }
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const startQuickChat = (topic) => {
  if (!currentChatId.value) {
    createNewChat()
  }
  inputMessage.value = `请提供关于${topic}的建议`
  sendMessage()
}

const followUpOnMessage = (message) => {
  followUpMessage.value = message.content
  inputMessage.value = ''
}

const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message) return
  
  let chat = currentChat.value
  if (!chat) {
    createNewChat()
    chat = currentChat.value
  }
  
  let finalMessage = message
  if (followUpMessage.value) {
    finalMessage = `基于以下内容进行追问：\n\n${followUpMessage.value}\n\n追问：${message}`
  }
  
  const userMessage = {
    isUser: true,
    content: message,
    time: new Date().toLocaleTimeString(),
    isStreaming: false
  }
  chat.messages.push(userMessage)
  inputMessage.value = ''
  followUpMessage.value = ''
  scrollToBottom()
  
  if (!chat.title || chat.title === '新对话') {
    chat.title = message.length > 30 ? message.substring(0, 30) + '...' : message
  }
  chat.updated_at = new Date().toLocaleString()
  
  if (useStream.value) {
    await sendStreamMessage(finalMessage, chat)
  } else {
    await sendNormalMessage(finalMessage, chat)
  }
  
  chatSessions.value = [...chatSessions.value].sort((a, b) => 
    new Date(b.updated_at) - new Date(a.updated_at)
  )
}

const sendNormalMessage = async (message, chat) => {
  isTyping.value = true
  
  try {
    const response = await agentAPI.chat({
      message,
      pet_id: selectedPet.value || undefined
    })
    
    if (response.success) {
      chat.messages.push({
        isUser: false,
        content: response.response,
        time: new Date().toLocaleTimeString(),
        isStreaming: false
      })
      
      if (response.is_sensitive) {
        chat.messages.push({
          isUser: false,
          content: '⚠️ 检测到敏感健康信息，建议使用结构化问诊功能获取更准确的建议。',
          time: new Date().toLocaleTimeString(),
          isStreaming: false
        })
      }
    }
  } catch (error) {
    chat.messages.push({
      isUser: false,
      content: '抱歉，服务暂时不可用，请稍后重试。',
      time: new Date().toLocaleTimeString(),
      isError: true,
      isStreaming: false
    })
  } finally {
    isTyping.value = false
    scrollToBottom()
  }
}

const sendStreamMessage = async (message, chat) => {
  isTyping.value = true
  
  const assistantMessage = reactive({
    isUser: false,
    content: '',
    time: new Date().toLocaleTimeString(),
    isStreaming: true,
    displayedContent: ''
  })
  chat.messages.push(assistantMessage)
  
  try {
    const response = await fetch('/api/agent/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        message,
        pet_id: selectedPet.value || undefined
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    if (!response.body) {
      throw new Error('Response body is null')
    }
    
    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''
    
    while (true) {
      const { done, value } = await reader.read()
      
      if (value) {
        buffer += decoder.decode(value, { stream: !done })
        
        let lineEnd
        while ((lineEnd = buffer.indexOf('\n')) !== -1) {
          const line = buffer.substring(0, lineEnd).trim()
          buffer = buffer.substring(lineEnd + 1)
          
          if (line.startsWith('data: ')) {
            try {
              const jsonStr = line.substring(5).trim()
              if (jsonStr) {
                const data = JSON.parse(jsonStr)
                
                if (data.content) {
                  assistantMessage.displayedContent += data.content
                  assistantMessage.content = assistantMessage.displayedContent
                  scrollToBottom()
                }
                
                if (data.done) {
                  assistantMessage.isStreaming = false
                  break
                }
                
                if (data.error) {
                  assistantMessage.isStreaming = false
                  assistantMessage.content = data.error
                  assistantMessage.isError = true
                  break
                }
              }
            } catch (e) {
              console.error('JSON parse error:', e)
            }
          }
        }
      }
      
      if (done) {
        break
      }
    }
  } catch (error) {
    assistantMessage.isStreaming = false
    assistantMessage.content = '抱歉，流式响应暂时不可用，请关闭流式输出模式。'
    assistantMessage.isError = true
  } finally {
    isTyping.value = false
    scrollToBottom()
  }
}

const submitConsultation = async () => {
  if (!canSubmitConsultation.value) {
    ElMessage.error('请填写完整的问诊信息')
    return
  }
  
  isTyping.value = true
  consultationResult.value = ''
  consultationRecommendation.value = ''
  lastConsultationResponse.value = {}
  savedRecordId.value = null
  
  try {
    const response = await agentAPI.structuredConsultation({
      pet_id: consultationForm.petId,
      symptoms: consultationForm.symptoms,
      duration: consultationForm.duration,
      severity: ['轻微', '较轻', '中等', '较重', '严重'][consultationForm.severity - 1],
      additional_info: consultationForm.additionalInfo
    })
    
    if (response.success) {
      consultationResult.value = response.consultation || ''
      consultationRecommendation.value = response.recommendation || ''
      lastConsultationResponse.value = response
      
      await saveConsultationToHealth(false)
    } else {
      ElMessage.error(response.error || '问诊失败')
    }
  } catch (error) {
    ElMessage.error('问诊失败，请稍后重试')
  } finally {
    isTyping.value = false
  }
}

const saveConsultationToHealth = async (showMessages = true) => {
  if (!consultationForm.petId) {
    if (showMessages) {
      ElMessage.error('请先选择宠物')
    }
    return
  }
  
  isSaving.value = true
  
  try {
    const response = await healthAPI.saveConsultationRecord(consultationForm.petId, {
      symptoms: consultationForm.symptoms,
      duration: consultationForm.duration,
      severity: ['轻微', '较轻', '中等', '较重', '严重'][consultationForm.severity - 1],
      consultation_result: consultationResult.value,
      recommendation: consultationRecommendation.value,
      additional_info: consultationForm.additionalInfo,
      full_response: lastConsultationResponse.value
    })
    
    if (response && response.success) {
      savedRecordId.value = response.record_id
      if (showMessages) {
        ElMessage.success('已保存到健康记录')
      }
    } else {
      if (showMessages) {
        ElMessage.error(response?.error || '保存失败')
      }
    }
  } catch (error) {
    if (showMessages) {
      ElMessage.error('保存失败，请稍后重试')
    }
  } finally {
    isSaving.value = false
  }
}

const exportCurrentConsultation = () => {
  const pet = pets.value.find(p => p.id === consultationForm.petId)
  const petName = pet?.name || '宠物'
  const petType = pet?.species || '未知'
  const petBreed = pet?.breed || '未知'
  
  const severityText = ['轻微', '较轻', '中等', '较重', '严重'][consultationForm.severity - 1]
  const timestamp = new Date().toLocaleString('zh-CN')
  
  const mdContent = `# 🏥 PetWise AI问诊记录

## 📋 基本信息

| 项目 | 内容 |
|------|------|
| **宠物名称** | ${petName} |
| **宠物类型** | ${petType} |
| **宠物品种** | ${petBreed} |
| **问诊时间** | ${timestamp} |

## 🔍 症状信息

### 主要症状
${consultationForm.symptoms.map(s => `- ${s}`).join('\n')}

### 发病时长
${consultationForm.duration || '未记录'}

### 严重程度
${severityText}

### 补充信息
${consultationForm.additionalInfo || '无'}

---

## 💊 AI问诊分析

${consultationResult.value}

---

## ⚠️ 免责声明

本问诊结果由PetWise AI助手生成，仅供参考，不能替代专业兽医诊断。
如您的宠物出现严重症状，请尽快联系专业宠物医院就诊。

---

*本记录由 PetWise 智能宠物管理系统自动生成*
*生成时间: ${timestamp}*
`

  const blob = new Blob([mdContent], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `问诊记录_${petName}_${new Date().toISOString().split('T')[0]}.md`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  
  ElMessage.success('导出成功')
}

onMounted(() => {
  const token = localStorage.getItem('token')
  if (token) {
    loadPets()
  }
  loadChatHistory()
  checkAgentHealth()
  
  setInterval(checkAgentHealth, 30000)
})
</script>

<style scoped>
.agent-page {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.main-container {
  flex: 1;
  display: flex;
  gap: 0;
  overflow: hidden;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.sidebar {
  width: 260px;
  background: white;
  border-right: 1px solid #eee;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  flex-shrink: 0;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.sidebar-header h2 {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #333;
}

.new-chat-btn {
  width: 100%;
  padding: 10px 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  transition: all 0.2s;
}

.new-chat-btn:hover {
  opacity: 0.9;
}

.new-chat-btn.primary {
  margin-top: 15px;
}

.chat-history {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.chat-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 5px;
  transition: all 0.2s;
  position: relative;
}

.chat-item:hover {
  background: #f5f7fa;
}

.chat-item.active {
  background: #eef2ff;
}

.chat-preview {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  overflow: hidden;
}

.chat-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.chat-info {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-title {
  font-size: 14px;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-time {
  font-size: 12px;
  color: #999;
  white-space: nowrap;
}

.delete-chat-btn {
  padding: 4px 8px;
  border: none;
  background: transparent;
  color: #999;
  font-size: 18px;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s;
}

.chat-item:hover .delete-chat-btn {
  opacity: 1;
}

.delete-chat-btn:hover {
  color: #f56c6c;
}

.empty-history {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 15px;
}

.empty-history p {
  margin-bottom: 0;
}

.sidebar-footer {
  padding: 15px;
  border-top: 1px solid #eee;
}

.consultation-btn {
  width: 100%;
  padding: 10px;
  background: #fff7e6;
  color: #e6a23c;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.consultation-btn:hover {
  background: #ffeeba;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  height: calc(100vh - 60px);
  max-height: calc(100vh - 60px);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: #f9fafb;
  border-bottom: 1px solid #eee;
}

.chat-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #999;
}

.status-indicator.online {
  background: #67c23a;
}

.chat-actions {
  display: flex;
  gap: 15px;
}

.stream-toggle {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  cursor: pointer;
}

.stream-toggle input {
  cursor: pointer;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  min-height: 0;
}

.welcome-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666;
}

.welcome-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.welcome-screen h3 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 20px;
}

.welcome-screen p {
  margin: 0 0 30px 0;
  font-size: 14px;
}

.quick-start {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
}

.quick-btn {
  padding: 10px 20px;
  background: #f5f7fa;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.quick-btn:hover {
  background: #eee;
  transform: translateY(-2px);
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

.message-item.is-error .message-content {
  background: #fff2f0;
  border: 1px solid #f56c6c;
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
  position: relative;
}

.message-content p {
  margin: 0;
  white-space: pre-wrap;
}

.markdown-content {
  line-height: 1.7;
}

.markdown-content h1 {
  font-size: 1.5em;
  font-weight: bold;
  margin: 0.5em 0;
}

.markdown-content h2 {
  font-size: 1.3em;
  font-weight: bold;
  margin: 0.5em 0;
}

.markdown-content h3 {
  font-size: 1.2em;
  font-weight: bold;
  margin: 0.5em 0;
}

.markdown-content p {
  margin: 0.5em 0;
}

.markdown-content ul,
.markdown-content ol {
  padding-left: 1.5em;
  margin: 0.5em 0;
}

.markdown-content li {
  margin: 0.3em 0;
}

.markdown-content strong {
  font-weight: bold;
  color: #667eea;
}

.message-item.is-user .markdown-content strong {
  color: #ffd700;
}

.markdown-content em {
  font-style: italic;
}

.markdown-content code {
  background: #f4f4f4;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.9em;
}

.message-item.is-user .markdown-content code {
  background: rgba(255, 255, 255, 0.2);
}

.markdown-content pre {
  background: #f4f4f4;
  padding: 10px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 0.5em 0;
}

.markdown-content pre code {
  background: transparent;
  padding: 0;
}

.markdown-content blockquote {
  border-left: 4px solid #667eea;
  padding-left: 1em;
  margin: 0.5em 0;
  color: #666;
  font-style: italic;
}

.message-item.is-user .markdown-content blockquote {
  border-left-color: #ffd700;
  color: rgba(255, 255, 255, 0.9);
}

.markdown-content hr {
  border: none;
  border-top: 1px solid #ddd;
  margin: 1em 0;
}

.markdown-content table {
  border-collapse: collapse;
  width: 100%;
  margin: 0.5em 0;
}

.markdown-content th,
.markdown-content td {
  border: 1px solid #ddd;
  padding: 6px 12px;
  text-align: left;
}

.markdown-content th {
  background: #f5f7fa;
}

.streaming-text {
  font-family: monospace;
}

.cursor {
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.time {
  display: block;
  font-size: 11px;
  color: #999;
  margin-top: 5px;
}

.message-item.is-user .time {
  color: rgba(255, 255, 255, 0.6);
}

.follow-up-btn {
  display: none;
  margin-top: 8px;
  padding: 4px 10px;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  border: 1px solid #667eea;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.message-content:hover .follow-up-btn {
  display: inline-block;
}

.follow-up-btn:hover {
  background: #667eea;
  color: white;
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
  align-items: center;
  flex-shrink: 0;
}

.pet-select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  min-width: 150px;
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

.consultation-container {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
  min-height: 0;
}

.back-btn {
  padding: 8px 16px;
  background: #f5f7fa;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  margin-bottom: 20px;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #eee;
}

.consultation-form {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  max-width: 1200px;
  margin: 0 auto;
}

.consultation-form h3 {
  margin: 0 0 10px 0;
  font-size: 20px;
}

.form-desc {
  color: #999;
  font-size: 14px;
  margin: 0 0 25px 0;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
}

.symptom-checkboxes {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
}

.symptom-checkbox {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
}

.symptom-checkbox input {
  cursor: pointer;
}

.severity-slider input {
  width: 100%;
}

.severity-labels {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.consultation-result {
  margin-top: 30px;
  padding: 20px;
  background: #f0f9ff;
  border-radius: 12px;
  border: 1px solid #409eff;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  flex-wrap: wrap;
  gap: 10px;
}

.result-header h3 {
  margin: 0;
  color: #409eff;
}

.result-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 5px;
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.export-btn {
  background: #67c23a;
  color: white;
}

.export-btn:hover:not(:disabled) {
  background: #5daf34;
}

.save-btn {
  background: #409eff;
  color: white;
}

.save-btn:hover:not(:disabled) {
  background: #337ecc;
}

.result-content {
  line-height: 1.8;
  margin-bottom: 15px;
}

.result-warning {
  padding: 12px;
  background: #fff7e6;
  border-radius: 8px;
  color: #e6a23c;
  font-weight: 500;
}

@media (max-width: 768px) {
  .sidebar {
    width: 200px;
  }
  
  .chat-title {
    font-size: 12px;
  }
  
  .message-content {
    max-width: 85%;
  }
}
</style>