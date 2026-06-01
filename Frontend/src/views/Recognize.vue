<template>
  <div class="recognize-page">
    <Navbar />
    
    <div class="container">
      <h1 class="page-title">🐾 宠物品种识别</h1>
      
      <div class="recognize-content">
        <div class="upload-section">
          <div 
            class="upload-area" 
            :class="{ dragging: isDragging }"
            @dragenter.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @dragover.prevent
            @drop.prevent="handleDrop"
            @click="triggerFileInput"
          >
            <input 
              ref="fileInput" 
              type="file" 
              accept="image/*" 
              class="file-input"
              @change="handleFileSelect"
            />
            <div class="upload-icon">📷</div>
            <p>{{ selectedFile ? selectedFile.name : '点击或拖拽上传图片' }}</p>
            <p class="hint">支持 JPG、PNG 格式</p>
          </div>
          
          <div class="upload-actions">
            <el-button type="primary" @click="handleRecognize" :loading="recognizing" class="recognize-btn">
              {{ recognizing ? '识别中...' : '开始识别' }}
            </el-button>
          </div>
        </div>
        
        <div v-if="result" class="result-section">
          <h3>识别结果</h3>
          
          <div class="result-card">
            <div class="result-header">
              <div class="breed-icon">🐾</div>
              <div class="breed-name">{{ result.breed }}</div>
              <div class="confidence">置信度: {{ (result.confidence * 100).toFixed(2) }}%</div>
            </div>
            
            <div v-if="result.top5" class="top5-section">
              <h4>TOP 5 候选</h4>
              <div class="top5-list">
                <div 
                  v-for="(item, index) in result.top5" 
                  :key="index" 
                  class="top5-item"
                >
                  <span class="rank">{{ index + 1 }}</span>
                  <span class="class-name">{{ item.class }}</span>
                  <span class="conf-value">{{ (item.confidence * 100).toFixed(2) }}%</span>
                </div>
              </div>
            </div>
          </div>
          
          <div v-if="breedInfo" class="breed-info-card">
            <h3>品种详情</h3>
            <div class="info-grid">
              <div class="info-item">
                <span class="label">类别</span>
                <span class="value">{{ breedInfo.category === 'cat' ? '🐱 猫' : '🐶 狗' }}</span>
              </div>
              <div class="info-item">
                <span class="label">起源</span>
                <span class="value">{{ breedInfo.origin }}</span>
              </div>
              <div class="info-item">
                <span class="label">性格</span>
                <span class="value">{{ breedInfo.personality }}</span>
              </div>
              <div class="info-item">
                <span class="label">寿命</span>
                <span class="value">{{ breedInfo.lifespan }}</span>
              </div>
              <div class="info-item">
                <span class="label">饲养建议</span>
                <span class="value">{{ breedInfo.feeding }}</span>
              </div>
              <div class="info-item">
                <span class="label">护理要点</span>
                <span class="value">{{ breedInfo.care }}</span>
              </div>
              <div class="info-item">
                <span class="label">常见问题</span>
                <span class="value">{{ breedInfo.common_issues }}</span>
              </div>
              <div class="info-item">
                <span class="label">适合人群</span>
                <span class="value">{{ breedInfo.suitable_for }}</span>
              </div>
            </div>
            <div class="info-actions">
              <el-button @click="addFavorite">❤️ 收藏</el-button>
              <el-button @click="goToBreedDetail">查看详情</el-button>
            </div>
          </div>
        </div>
        
        <div class="history-section">
          <h3>识别历史</h3>
          <div v-if="history.length" class="history-list">
            <div 
              v-for="item in history" 
              :key="item.id" 
              class="history-item"
            >
              <div class="history-info">
                <span class="history-breed">{{ item.breed }}</span>
                <span class="history-time">{{ item.created_at }}</span>
              </div>
              <button class="delete-btn" @click="deleteHistoryItem(item.id)">删除</button>
            </div>
          </div>
          <div v-else class="empty-history">
            <p>暂无识别记录</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import Navbar from '@/components/Navbar.vue'
import { recognizeAPI } from '@/api/recognize'
import { favoritesAPI } from '@/api/favorites'

const fileInput = ref(null)
const isDragging = ref(false)
const selectedFile = ref(null)
const recognizing = ref(false)
const result = ref(null)
const breedInfo = ref(null)
const history = ref([])

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
  }
}

const handleDrop = (event) => {
  isDragging.value = false
  const file = event.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    selectedFile.value = file
  }
}

const handleRecognize = async () => {
  if (!selectedFile.value) {
    ElMessage.error('请先上传图片')
    return
  }
  
  recognizing.value = true
  
  try {
    const formData = new FormData()
    formData.append('image', selectedFile.value)
    
    const response = await recognizeAPI.recognize(formData)
    
    if (response.success) {
      result.value = response.result
      breedInfo.value = response.breed_info
      await loadHistory()
    } else {
      ElMessage.error(response.message || '识别失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '识别失败')
  } finally {
    recognizing.value = false
  }
}

const loadHistory = async () => {
  try {
    const response = await recognizeAPI.getHistory()
    if (response.success) {
      history.value = response.data || []
    }
  } catch (error) {
    console.log('Failed to load history:', error)
  }
}

const deleteHistoryItem = async (id) => {
  try {
    const response = await recognizeAPI.deleteHistory(id)
    if (response.success) {
      ElMessage.success('删除成功')
      await loadHistory()
    }
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const addFavorite = async () => {
  if (!breedInfo.value) return
  
  try {
    const response = await favoritesAPI.addFavorite({ breed: breedInfo.value.breed })
    if (response.success) {
      ElMessage.success('收藏成功')
    }
  } catch (error) {
    ElMessage.error('收藏失败')
  }
}

const goToBreedDetail = () => {
  if (breedInfo.value) {
    window.location.href = `/breed/${encodeURIComponent(breedInfo.value.breed)}`
  }
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.recognize-page {
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

.recognize-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.upload-section {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.upload-area {
  border: 2px dashed #ddd;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.upload-area.dragging {
  border-color: #667eea;
  background: #f0f4ff;
}

.file-input {
  display: none;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.upload-area p {
  margin: 5px 0;
  color: #666;
}

.hint {
  font-size: 12px;
  color: #999;
}

.upload-actions {
  margin-top: 20px;
  text-align: center;
}

.recognize-btn {
  padding: 12px 40px;
  font-size: 16px;
}

.result-section {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.result-section h3 {
  margin-bottom: 20px;
  font-size: 20px;
}

.result-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 20px;
  color: white;
  margin-bottom: 20px;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.breed-icon {
  font-size: 36px;
}

.breed-name {
  font-size: 24px;
  font-weight: 600;
}

.confidence {
  margin-left: auto;
  opacity: 0.9;
}

.top5-section h4 {
  margin-bottom: 10px;
  font-size: 14px;
  opacity: 0.9;
}

.top5-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.top5-item {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.1);
  padding: 8px 12px;
  border-radius: 8px;
}

.rank {
  width: 24px;
  text-align: center;
  font-weight: 600;
}

.class-name {
  flex: 1;
}

.conf-value {
  opacity: 0.8;
}

.breed-info-card {
  background: #f9fafb;
  border-radius: 12px;
  padding: 20px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.info-item {
  background: white;
  padding: 12px;
  border-radius: 8px;
}

.info-item .label {
  display: block;
  font-size: 12px;
  color: #999;
  margin-bottom: 5px;
}

.info-item .value {
  font-size: 14px;
  color: #333;
}

.info-actions {
  display: flex;
  gap: 10px;
}

.history-section {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.history-section h3 {
  margin-bottom: 20px;
  font-size: 20px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px;
  background: #f9fafb;
  border-radius: 8px;
}

.history-info {
  display: flex;
  flex-direction: column;
}

.history-breed {
  font-weight: 600;
}

.history-time {
  font-size: 12px;
  color: #999;
}

.delete-btn {
  background: #fff2f0;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  color: #f56c6c;
  cursor: pointer;
  font-size: 12px;
}

.delete-btn:hover {
  background: #ffccc7;
}

.empty-history {
  text-align: center;
  padding: 30px;
  color: #999;
}
</style>