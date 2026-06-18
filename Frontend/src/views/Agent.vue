<template>
  <div class="agent-page">
    <Navbar />
    
    <div class="container">
      <h1 class="page-title">🤖 AI智能助手</h1>
      
      <div class="mode-tabs">
        <button 
          :class="{ active: currentMode === 'chat' }" 
          @click="currentMode = 'chat'"
        >
          💬 对话模式
        </button>
        <button 
          :class="{ active: currentMode === 'consultation' }" 
          @click="currentMode = 'consultation'"
        >
          🏥 结构化问诊
        </button>
        <button 
          :class="{ active: currentMode === 'history' }" 
          @click="currentMode = 'history'"
        >
          📜 历史记录
        </button>
      </div>
      
      <!-- 对话模式 -->
      <div v-if="currentMode === 'chat'" class="chat-container">
        <div class="chat-header">
          <div class="chat-info">
            <span class="status-indicator" :class="{ online: agentOnline }"></span>
            <span>{{ agentOnline ? 'AI助手在线' : 'AI助手离线' }}</span>
          </div>
          <label class="stream-toggle">
            <input type="checkbox" v-model="useStream" />
            <span>流式输出</span>
          </label>
        </div>
        
        <div class="chat-messages" ref="messagesContainer">
          <div 
            v-for="(message, index) in messages" 
            :key="index" 
            class="message-item"
            :class="{ 'is-user': message.isUser, 'is-error': message.isError }"
          >
            <div class="avatar">{{ message.isUser ? '👤' : (message.isError ? '❌' : '🤖') }}</div>
            <div class="message-content">
              <div v-if="message.isStreaming" class="streaming-text">
                {{ message.displayedContent }}<span class="cursor">|</span>
              </div>
              <p v-else>{{ message.content }}</p>
              <span class="time">{{ message.time }}</span>
            </div>
          </div>
          
          <div v-if="isTyping && !useStream" class="typing-indicator">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
          </div>
        </div>
        
        <div class="chat-input">
          <select v-model="selectedPet" class="pet-select">
            <option value="">选择宠物档案</option>
            <option v-for="pet in pets" :key="pet.id" :value="pet.id">
              {{ pet.name }} ({{ pet.breed }})
            </option>
          </select>
          <input 
            v-model="inputMessage" 
            type="text" 
            placeholder="输入您的问题..."
            @keyup.enter="sendMessage"
            :disabled="isTyping"
          />
          <button @click="sendMessage" :disabled="!inputMessage || isTyping">
            {{ isTyping ? '发送中...' : '发送' }}
          </button>
        </div>
        
        <div class="quick-actions">
          <h3>快捷功能</h3>
          <div class="action-grid">
            <button class="action-btn" @click="getQuickAdvice('饮食建议')">
              🍽️ 饮食建议
            </button>
            <button class="action-btn" @click="getQuickAdvice('训练指导')">
              🎾 训练指导
            </button>
            <button class="action-btn" @click="getQuickAdvice('日常护理')">
              🛁 日常护理
            </button>
            <button class="action-btn danger" @click="handleEmergency">
              🚨 紧急咨询
            </button>
          </div>
        </div>
      </div>
      
      <!-- 结构化问诊模式 -->
      <div v-if="currentMode === 'consultation'" class="consultation-container">
        <div class="consultation-form">
          <h3>请填写以下信息</h3>
          
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
          <div class="result-content">
            {{ consultationResult }}
          </div>
          <div class="result-warning">
            ⚠️ 建议：尽快联系宠物医院进行专业诊断
          </div>
        </div>
      </div>
      
      <!-- 历史记录模式 -->
      <div v-if="currentMode === 'history'" class="history-container">
        <div class="history-list">
          <div v-if="chatHistory.length" class="history-items">
            <div 
              v-for="item in chatHistory" 
              :key="item.id" 
              class="history-item"
            >
              <div class="history-header">
                <span class="history-role">{{ item.role === 'user' ? '👤 您' : '🤖 AI' }}</span>
                <span class="history-time">{{ item.created_at }}</span>
              </div>
              <p class="history-content">{{ item.message }}</p>
            </div>
          </div>
          <div v-else class="empty-state">
            <p>暂无对话记录</p>
          </div>
        </div>
        
        <div class="history-actions">
          <button class="clear-btn" @click="clearHistory">
            清空历史记录
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import Navbar from '@/components/Navbar.vue'
import { agentAPI } from '@/api/agent'
import { petsAPI } from '@/api/pets'
import { healthAPI } from '@/api/health'

const currentMode = ref('chat')
const messages = ref([
  {
    isUser: false,
    content: '您好！我是PetWise AI助手。请问有什么可以帮到您的？',
    time: new Date().toLocaleTimeString(),
    isStreaming: false,
    displayedContent: ''
  }
])
const inputMessage = ref('')
const isTyping = ref(false)
const useStream = ref(false)
const agentOnline = ref(false)
const messagesContainer = ref(null)
const pets = ref([])
const selectedPet = ref('')
const chatHistory = ref([])

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

const loadHistory = async () => {
  try {
    const response = await agentAPI.getHistory()
    if (response.success) {
      chatHistory.value = response.history || []
    }
  } catch (error) {
    console.error('Failed to load history:', error)
  }
}

const checkAgentHealth = async () => {
  const maxRetries = 3
  const retryDelay = 2000
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = await agentAPI.healthCheck()
      console.log('Health check response:', response)
      console.log('Response status:', response.status)
      agentOnline.value = response.status === 'healthy'
      console.log('Agent online status:', agentOnline.value)
      return
    } catch (error) {
      console.error(`Health check error (attempt ${attempt}/${maxRetries}):`, error)
      if (attempt < maxRetries) {
        console.log(`Retrying in ${retryDelay}ms...`)
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

const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message) return
  
  const userMessage = {
    isUser: true,
    content: message,
    time: new Date().toLocaleTimeString(),
    isStreaming: false
  }
  messages.value.push(userMessage)
  inputMessage.value = ''
  scrollToBottom()
  
  if (useStream.value) {
    await sendStreamMessage(message)
  } else {
    await sendNormalMessage(message)
  }
}

const sendNormalMessage = async (message) => {
  isTyping.value = true
  
  try {
    const response = await agentAPI.chat({
      message,
      pet_id: selectedPet.value || undefined
    })
    
    if (response.success) {
      messages.value.push({
        isUser: false,
        content: response.response,
        time: new Date().toLocaleTimeString(),
        isStreaming: false
      })
      
      if (response.is_sensitive) {
        messages.value.push({
          isUser: false,
          content: '⚠️ 检测到敏感健康信息，建议使用结构化问诊功能获取更准确的建议。',
          time: new Date().toLocaleTimeString(),
          isStreaming: false
        })
      }
    }
  } catch (error) {
    messages.value.push({
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

const sendStreamMessage = async (message) => {
  isTyping.value = true
  
  const assistantMessage = reactive({
    isUser: false,
    content: '',
    time: new Date().toLocaleTimeString(),
    isStreaming: true,
    displayedContent: ''
  })
  messages.value.push(assistantMessage)
  
  try {
    console.log('Starting stream request...')
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
    
    console.log('Stream response status:', response.status, response.statusText)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    if (!response.body) {
      throw new Error('Response body is null')
    }
    
    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''
    
    console.log('Starting to read stream...')
    
    while (true) {
      const { done, value } = await reader.read()
      
      console.log('Stream read:', { done, value: value ? `(${value.length} bytes)` : null })
      
      if (value) {
        buffer += decoder.decode(value, { stream: !done })
        console.log('Buffer content:', buffer)
        
        let lineEnd
        while ((lineEnd = buffer.indexOf('\n')) !== -1) {
          const line = buffer.substring(0, lineEnd).trim()
          buffer = buffer.substring(lineEnd + 1)
          
          if (line.startsWith('data: ')) {
            try {
              const jsonStr = line.substring(5).trim()
              console.log('Received data:', jsonStr)
              if (jsonStr) {
                const data = JSON.parse(jsonStr)
                
                if (data.content) {
                  assistantMessage.displayedContent += data.content
                  assistantMessage.content = assistantMessage.displayedContent
                  console.log('Updated displayedContent:', assistantMessage.displayedContent)
                  scrollToBottom()
                }
                
                if (data.done) {
                  assistantMessage.isStreaming = false
                  console.log('Stream completed')
                  break
                }
                
                if (data.error) {
                  assistantMessage.isStreaming = false
                  assistantMessage.content = data.error
                  assistantMessage.isError = true
                  console.error('Stream error:', data.error)
                  break
                }
              }
            } catch (e) {
              console.error('JSON parse error:', e, 'line:', line)
            }
          }
        }
      }
      
      if (done) {
        console.log('Stream reader done')
        break
      }
    }
  } catch (error) {
    console.error('Stream error:', error)
    assistantMessage.isStreaming = false
    assistantMessage.content = '抱歉，流式响应暂时不可用，请关闭流式输出模式。'
    assistantMessage.isError = true
  } finally {
    isTyping.value = false
    scrollToBottom()
  }
}

const getQuickAdvice = async (topic) => {
  inputMessage.value = `请提供关于${topic}的建议`
  await sendMessage()
}

const handleEmergency = async () => {
  const symptoms = prompt('请简要描述宠物的紧急症状：')
  if (!symptoms) return
  
  isTyping.value = true
  
  try {
    const response = await agentAPI.emergency({
      symptoms,
      pet_type: pets.value.find(p => p.id === selectedPet.value)?.category || 'unknown'
    })
    
    if (response.success) {
      messages.value.push({
        isUser: false,
        content: `🚨 紧急咨询结果：\n\n${response.consultation}`,
        time: new Date().toLocaleTimeString(),
        isStreaming: false
      })
      
      if (response.warning) {
        messages.value.push({
          isUser: false,
          content: response.warning,
          time: new Date().toLocaleTimeString(),
          isError: true,
          isStreaming: false
        })
      }
    }
  } catch (error) {
    ElMessage.error('紧急咨询失败')
  } finally {
    isTyping.value = false
    scrollToBottom()
  }
}

const submitConsultation = async () => {
  console.log('canSubmitConsultation:', canSubmitConsultation.value)
  console.log('consultationForm:', consultationForm)
  
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
    console.log('Sending structured consultation request...')
    const response = await agentAPI.structuredConsultation({
      pet_id: consultationForm.petId,
      symptoms: consultationForm.symptoms,
      duration: consultationForm.duration,
      severity: ['轻微', '较轻', '中等', '较重', '严重'][consultationForm.severity - 1],
      additional_info: consultationForm.additionalInfo
    })
    
    console.log('Structured consultation response:', response)
    
    if (response.success) {
      consultationResult.value = response.consultation || ''
      consultationRecommendation.value = response.recommendation || ''
      lastConsultationResponse.value = response
      
      // 诊断成功后自动保存到健康记录（静默模式）
      await saveConsultationToHealth(false)
    } else {
      ElMessage.error(response.error || '问诊失败')
    }
  } catch (error) {
    console.error('Structured consultation error:', error)
    ElMessage.error('问诊失败，请稍后重试')
  } finally {
    isTyping.value = false
  }
}

// 保存问诊结果到健康记录
const saveConsultationToHealth = async (showMessages = true) => {
  if (!consultationForm.petId) {
    if (showMessages) {
      ElMessage.error('请先选择宠物')
    }
    return
  }
  
  isSaving.value = true
  
  try {
    console.log('saveConsultationToHealth - preparing data...')
    console.log('symptoms:', consultationForm.symptoms)
    console.log('duration:', consultationForm.duration)
    console.log('severity:', ['轻微', '较轻', '中等', '较重', '严重'][consultationForm.severity - 1])
    console.log('consultationResult:', consultationResult.value?.substring?.(0, 100) + '...')
    console.log('recommendation:', consultationRecommendation.value)
    console.log('additionalInfo:', consultationForm.additionalInfo)
    
    const response = await healthAPI.saveConsultationRecord(consultationForm.petId, {
      symptoms: consultationForm.symptoms,
      duration: consultationForm.duration,
      severity: ['轻微', '较轻', '中等', '较重', '严重'][consultationForm.severity - 1],
      consultation_result: consultationResult.value,
      recommendation: consultationRecommendation.value,
      additional_info: consultationForm.additionalInfo,
      full_response: lastConsultationResponse.value
    })
    
    console.log('saveConsultationToHealth response type:', typeof response)
    console.log('saveConsultationToHealth response:', response)
    
    if (response && response.success) {
      savedRecordId.value = response.record_id
      if (showMessages) {
        ElMessage.success('已保存到健康记录')
      }
    } else {
      if (showMessages) {
        ElMessage.error(response?.error || '保存失败')
      } else {
        console.warn('Auto-save failed:', response?.error)
      }
    }
  } catch (error) {
    console.error('Save consultation error:', error)
    if (showMessages) {
      ElMessage.error('保存失败，请稍后重试')
    }
  } finally {
    isSaving.value = false
  }
}

// 导出问诊结果为MD文件
const exportConsultationMD = async () => {
  // 如果还没有保存记录，先保存
  if (!savedRecordId.value) {
    await saveConsultationToHealth()
    if (!savedRecordId.value) {
      ElMessage.error('请先保存问诊记录')
      return
    }
  }
  
  isExporting.value = true
  
  try {
    const response = await healthAPI.exportConsultationMD(consultationForm.petId, savedRecordId.value)
    
    if (response.success) {
      // 创建Blob并下载
      const blob = new Blob([response.content], { type: 'text/markdown;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = response.filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
      
      ElMessage.success('导出成功')
    } else {
      ElMessage.error(response.error || '导出失败')
    }
  } catch (error) {
    console.error('Export consultation error:', error)
    ElMessage.error('导出失败，请稍后重试')
  } finally {
    isExporting.value = false
  }
}

// 直接导出当前问诊结果（不依赖已保存记录）
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

  // 创建Blob并下载
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

const clearHistory = async () => {
  if (!confirm('确定要清空所有对话历史吗？')) return
  
  try {
    const response = await agentAPI.clearHistory()
    if (response.success) {
      ElMessage.success('已清空历史记录')
      chatHistory.value = []
    }
  } catch (error) {
    ElMessage.error('清空失败')
  }
}

onMounted(() => {
  const token = localStorage.getItem('token')
  if (token) {
    loadPets()
  }
  loadHistory()
  checkAgentHealth()
  
  // 每30秒检查一次智能体状态
  setInterval(checkAgentHealth, 30000)
})
</script>

<style scoped>
.agent-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-title {
  text-align: center;
  font-size: 28px;
  margin-bottom: 30px;
}

.mode-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  background: white;
  padding: 10px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.mode-tabs button {
  flex: 1;
  padding: 12px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.mode-tabs button.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.chat-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  overflow: hidden;
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
}

.message-content p {
  margin: 0;
  white-space: pre-wrap;
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

.quick-actions {
  margin-top: 20px;
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

/* 结构化问诊 */
.consultation-container {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.consultation-form h3 {
  margin-bottom: 20px;
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

.consultation-result h3 {
  margin-bottom: 15px;
  color: #409eff;
}

.result-content {
  white-space: pre-wrap;
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

/* 历史记录 */
.history-container {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.history-items {
  max-height: 500px;
  overflow-y: auto;
}

.history-item {
  padding: 15px;
  background: #f9fafb;
  border-radius: 8px;
  margin-bottom: 15px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.history-role {
  font-weight: 600;
}

.history-time {
  font-size: 12px;
  color: #999;
}

.history-content {
  margin: 0;
  white-space: pre-wrap;
  line-height: 1.6;
}

.history-actions {
  margin-top: 20px;
  text-align: center;
}

.clear-btn {
  padding: 10px 30px;
  background: #fff2f0;
  color: #f56c6c;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.empty-state {
  text-align: center;
  padding: 60px;
  color: #999;
}
</style>
