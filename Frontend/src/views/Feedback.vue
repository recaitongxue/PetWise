<template>
  <div class="feedback-page">
    <Navbar />
    
    <div class="container">
      <h1 class="page-title">💬 意见反馈</h1>
      <p class="page-subtitle">您的意见对我们非常重要，帮助我们改进产品</p>
      
      <div class="feedback-form">
        <div class="form-group">
          <label>反馈类型</label>
          <select v-model="form.type" class="form-control">
            <option value="">请选择反馈类型</option>
            <option value="bug">问题反馈</option>
            <option value="feature">功能建议</option>
            <option value="content">内容纠错</option>
            <option value="other">其他</option>
          </select>
        </div>
        
        <div class="form-group">
          <label>反馈内容</label>
          <textarea 
            v-model="form.content" 
            class="form-control" 
            rows="8"
            placeholder="请详细描述您的问题或建议..."
          ></textarea>
          <div class="char-count">{{ form.content.length }}/500</div>
        </div>
        
        <div class="form-actions">
          <button class="submit-btn" @click="submitFeedback" :disabled="submitting">
            {{ submitting ? '提交中...' : '提交反馈' }}
          </button>
        </div>
      </div>
      
      <div class="feedback-history">
        <h3>我的反馈记录</h3>
        
        <div v-if="feedbackHistory.length" class="history-list">
          <div 
            v-for="item in feedbackHistory" 
            :key="item.id" 
            class="history-item"
            :class="`status-${item.status}`"
          >
            <div class="item-header">
              <span class="type-badge">{{ getTypeLabel(item.type) }}</span>
              <span class="status-badge">{{ getStatusLabel(item.status) }}</span>
              <span class="date">{{ item.created_at }}</span>
            </div>
            <div class="item-content">{{ item.content }}</div>
            <div v-if="item.admin_reply" class="item-reply">
              <strong>管理员回复：</strong>
              <p>{{ item.admin_reply }}</p>
            </div>
          </div>
        </div>
        
        <div v-else class="empty-state">
          <p>暂无反馈记录</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import Navbar from '@/components/Navbar.vue'
import axios from '@/api/axios'

const form = reactive({
  type: '',
  content: ''
})

const submitting = ref(false)
const feedbackHistory = ref([])

const typeLabels = {
  'bug': '问题反馈',
  'feature': '功能建议',
  'content': '内容纠错',
  'other': '其他'
}

const statusLabels = {
  'pending': '待处理',
  'replied': '已回复'
}

const getTypeLabel = (type) => typeLabels[type] || type
const getStatusLabel = (status) => statusLabels[status] || status

const submitFeedback = async () => {
  if (!form.type) {
    ElMessage.error('请选择反馈类型')
    return
  }
  
  if (!form.content.trim()) {
    ElMessage.error('请输入反馈内容')
    return
  }
  
  if (form.content.length > 500) {
    ElMessage.error('反馈内容不能超过500字')
    return
  }
  
  submitting.value = true
  
  try {
    const response = await axios.post('/feedback', form)
    
    if (response.success) {
      ElMessage.success('反馈提交成功')
      form.type = ''
      form.content = ''
      loadFeedbackHistory()
    }
  } catch (error) {
    ElMessage.error('提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

const loadFeedbackHistory = async () => {
  try {
    const response = await axios.get('/feedback/my')
    if (response.success) {
      feedbackHistory.value = response.data || []
    }
  } catch (error) {
    console.error('Failed to load feedback history:', error)
  }
}

onMounted(() => {
  loadFeedbackHistory()
})
</script>

<style scoped>
.feedback-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding-bottom: 40px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-title {
  color: white;
  font-size: 2.5rem;
  margin-bottom: 10px;
  text-align: center;
}

.page-subtitle {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.1rem;
  text-align: center;
  margin-bottom: 40px;
}

.feedback-form {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  margin-bottom: 40px;
}

.form-group {
  margin-bottom: 25px;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.form-control {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s;
  font-family: inherit;
}

.form-control:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.char-count {
  text-align: right;
  color: #999;
  font-size: 0.85rem;
  margin-top: 5px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

.submit-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 40px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.feedback-history h3 {
  color: white;
  margin-bottom: 20px;
  font-size: 1.5rem;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.history-item {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.item-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.type-badge {
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

.status-badge {
  background: #fff3e0;
  color: #f57c00;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

.history-item.status-replied .status-badge {
  background: #e8f5e9;
  color: #388e3c;
}

.date {
  margin-left: auto;
  color: #999;
  font-size: 0.85rem;
}

.item-content {
  color: #555;
  line-height: 1.6;
  margin-bottom: 12px;
}

.item-reply {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 8px;
  border-left: 3px solid #667eea;
}

.item-reply strong {
  color: #667eea;
  display: block;
  margin-bottom: 5px;
}

.item-reply p {
  color: #666;
  margin: 0;
  line-height: 1.5;
}

.empty-state {
  background: white;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  color: #999;
}
</style>