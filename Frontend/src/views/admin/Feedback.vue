<template>
  <AdminLayout>
    <div class="feedback-page">
      <div class="page-header">
        <div class="header-title">
          <h1>💬 用户反馈</h1>
          <p class="subtitle">查看和回复用户反馈意见</p>
        </div>
      </div>
      
      <div class="filter-bar">
          <el-select v-model="statusFilter" placeholder="筛选状态">
            <el-option label="全部" value="" />
            <el-option label="待回复" value="pending" />
            <el-option label="已回复" value="replied" />
          </el-select>
        </div>
        
        <div v-if="feedbackList.length" class="feedback-list">
          <div 
            v-for="feedback in feedbackList" 
            :key="feedback.id" 
            class="feedback-item"
          >
            <div class="feedback-header">
              <span class="feedback-user">{{ feedback.username }}</span>
              <span :class="['status-badge', feedback.status]">
                {{ feedback.status === 'pending' ? '待回复' : '已回复' }}
              </span>
              <span class="feedback-time">{{ feedback.created_at }}</span>
            </div>
            <p class="feedback-content">{{ feedback.content }}</p>
            
            <div v-if="feedback.reply" class="reply-section">
              <div class="reply-label">管理员回复：</div>
              <p class="reply-content">{{ feedback.reply }}</p>
              <span class="reply-time">{{ feedback.replied_at }}</span>
            </div>
            
            <div v-if="feedback.status === 'pending'" class="reply-form">
              <textarea 
                v-model="replyContent" 
                placeholder="输入回复内容..."
                rows="3"
              ></textarea>
              <button @click="replyFeedback(feedback.id)">回复</button>
            </div>
          </div>
        </div>
        
        <div v-else class="empty-state">暂无反馈</div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import AdminLayout from '@/components/AdminLayout.vue'
import { adminAPI } from '@/api/admin'

const feedbackList = ref([])
const statusFilter = ref('')
const replyContent = ref('')

const loadFeedback = async () => {
  try {
    const response = await adminAPI.getFeedback()
    if (response.success) {
      feedbackList.value = response.data || []
      
      if (statusFilter.value) {
        feedbackList.value = feedbackList.value.filter(f => f.status === statusFilter.value)
      }
    }
  } catch (error) {
    console.log('Failed to load feedback:', error)
  }
}

const replyFeedback = async (id) => {
  if (!replyContent.value.trim()) {
    ElMessage.error('请输入回复内容')
    return
  }
  
  try {
    const response = await adminAPI.replyFeedback(id, { reply: replyContent.value })
    
    if (response.success) {
      ElMessage.success('回复成功')
      replyContent.value = ''
      await loadFeedback()
    }
  } catch (error) {
    ElMessage.error('回复失败')
  }
}

onMounted(() => {
  loadFeedback()
})
</script>

<style scoped>
.admin-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.admin-container {
  display: flex;
  gap: 20px;
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.sidebar {
  width: 200px;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.sidebar-title {
  font-size: 18px;
  margin: 0 0 20px 0;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.nav-item {
  padding: 10px 15px;
  text-decoration: none;
  color: #666;
  border-radius: 8px;
  transition: all 0.2s;
}

.nav-item:hover {
  background: #f5f7fa;
}

.nav-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.main-content {
  flex: 1;
}

.main-content h1 {
  margin: 0 0 20px 0;
  font-size: 24px;
}

.filter-bar {
  margin-bottom: 20px;
}

.feedback-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.feedback-item {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.feedback-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.feedback-user {
  font-weight: 600;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
}

.status-badge.pending {
  background: #fff7e6;
  color: #e6a23c;
}

.status-badge.replied {
  background: #f0f9ff;
  color: #67c23a;
}

.feedback-time {
  margin-left: auto;
  font-size: 12px;
  color: #999;
}

.feedback-content {
  margin: 0;
  color: #333;
  line-height: 1.6;
}

.reply-section {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px dashed #eee;
}

.reply-label {
  font-size: 12px;
  color: #999;
  margin-bottom: 5px;
}

.reply-content {
  margin: 0;
  color: #667eea;
  background: #f0f4ff;
  padding: 10px;
  border-radius: 6px;
}

.reply-time {
  display: block;
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.reply-form {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px dashed #eee;
}

.reply-form textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  resize: none;
  margin-bottom: 10px;
}

.reply-form button {
  padding: 8px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.empty-state {
  background: white;
  border-radius: 12px;
  padding: 60px;
  text-align: center;
  color: #999;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}
</style>