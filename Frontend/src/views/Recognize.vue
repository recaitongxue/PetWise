<template>
  <div class="recognize-page">
    <Navbar />
    <div class="container">
      <h1 class="page-title">🐾 宠物品种识别</h1>
      
      <div class="recognize-content">
        <div class="upload-section">
          <div 
            class="upload-area" 
            :class="{ dragging: isDragging, hasImage: selectedFile }"
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
            
            <div v-if="imagePreview" class="image-preview">
              <img :src="imagePreview" alt="预览图片" class="preview-image" />
              <div class="preview-overlay">
                <span class="change-text">点击更换图片</span>
              </div>
            </div>
            
            <div v-else class="upload-hint">
              <div class="upload-icon">📷</div>
              <p>{{ selectedFile ? selectedFile.name : '点击或拖拽上传图片' }}</p>
              <p class="hint">支持 JPG、PNG 格式</p>
            </div>
          </div>
          
          <div class="upload-actions">
            <el-button 
              type="primary" 
              @click="handleRecognize" 
              :loading="recognizing"
              class="recognize-btn"
            >
              {{ recognizing ? '识别中...' : '开始识别' }}
            </el-button>
            <el-button @click="handleBatchRecognize">
              📸 批量识别
            </el-button>
          </div>
        </div>

        <div v-if="result" class="result-section">
          <h3>识别结果</h3>
          
          <div class="result-card">
            <!-- 原始图片展示 -->
            <div class="original-image-section">
              <h4>原始图片</h4>
              <img :src="imagePreview" alt="原始图片" class="original-image" />
            </div>

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

            <!-- 用户纠错 -->
            <div class="correction-section">
              <h4>识别结果不准确？</h4>
              <el-select v-model="correctedBreed" placeholder="请选择正确品种" filterable>
                <el-option 
                  v-for="breed in allBreeds" 
                  :key="breed" 
                  :label="breed" 
                  :value="breed"
                />
                <el-option label="🔄 其他（手动输入）" value="__custom__" />
              </el-select>
              
              <div v-if="correctedBreed === '__custom__'" class="custom-breed-input">
                <el-input 
                  v-model="customBreed"
                  placeholder="请输入实际品种名称"
                />
              </div>
              
              <el-input 
                v-model="correctionReason"
                type="textarea"
                :rows="2"
                placeholder="请说明原因"
              />
              <el-button @click="submitCorrection" type="primary">提交纠错</el-button>
            </div>
          </div>
        </div>

        <div class="history-section">
          <div class="section-header">
            <h3>识别历史</h3>
            <el-button @click="showHistory = !showHistory">
              {{ showHistory ? '隐藏' : '查看' }}
            </el-button>
          </div>
          
          <div v-if="showHistory" class="history-list">
            <div v-if="history.length > 0">
              <div 
                v-for="item in history" 
                :key="item.id" 
                class="history-item"
              >
                <div class="history-info">
                  <img :src="item.image_url" alt="识别图片" class="history-image" />
                  <div class="history-detail">
                    <span class="history-breed">{{ item.breed }}</span>
                    <span class="history-time">{{ item.created_at }}</span>
                  </div>
                </div>
                <div class="history-actions">
                  <el-button size="small" @click="deleteHistoryItem(item.id)">删除</el-button>
                </div>
              </div>
            </div>
            <div v-else class="empty-history">
              <p>暂无识别记录</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import Navbar from '@/components/Navbar.vue'
import { recognizeAPI } from '@/api/recognize'
import { favoritesAPI } from '@/api/favorites'
import { breedAPI } from '@/api/breed'

const fileInput = ref(null)
const isDragging = ref(false)
const selectedFile = ref(null)
const imagePreview = ref(null)
const recognizing = ref(false)
const result = ref(null)
const breedInfo = ref(null)
const showHistory = ref(false)
const history = ref([])
const correctedBreed = ref('')
const correctionReason = ref('')
const customBreed = ref('')
const allBreeds = ref([])
const currentRecognitionId = ref(null)

// 批量识别相关
const batchMode = ref(false)
const batchFiles = ref([])
const batchResults = ref([])
const batchRecognizing = ref(false)

// 加载所有品种列表
const loadAllBreeds = async () => {
  try {
    const dogBreeds = ['中华田园犬', '吉娃娃', '哈士奇', '德牧', '拉布拉多', '杜宾', '柴犬', '法国斗牛', '萨摩耶', '藏獒', '金毛']
    const catBreeds = ['阿比西尼亚猫', '埃及猫', '豹猫', '布偶猫', '波斯猫', '缅甸猫', '俄罗斯蓝猫', '孟买猫', '缅因猫', '无毛猫', '暹罗猫', '英国短毛猫']
    allBreeds.value = [...dogBreeds, ...catBreeds]
  } catch (error) {
    console.error('Failed to load breeds:', error)
  }
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  processFile(file)
}

const handleDrop = (event) => {
  isDragging.value = false
  const file = event.dataTransfer.files[0]
  processFile(file)
}

const processFile = (file) => {
  if (!file || !file.type.startsWith('image/')) {
    ElMessage.error('请上传有效的图片文件')
    return
  }
  
  selectedFile.value = file
  
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target.result
  }
  reader.readAsDataURL(file)
}

const handleRecognize = async () => {
    if (!selectedFile.value) {
      ElMessage.error('请先上传图片')
      return
    }
    
    recognizing.value = true
    result.value = null
    breedInfo.value = null
    currentRecognitionId.value = null
    
    try {
      const response = await recognizeAPI.recognize(selectedFile.value)
      if (response.success) {
        result.value = response.result
        result.value.recognition_id = response.recognition_id
        currentRecognitionId.value = response.recognition_id
        
        if (response.breed_info) {
          breedInfo.value = response.breed_info
        }
      } else {
        ElMessage.error(response.message || '识别失败，请稍后重试')
      }
    } catch (error) {
      console.error('Recognize error:', error)
      ElMessage.error(error.response?.data?.error || '网络错误，请稍后重试')
    } finally {
      recognizing.value = false
    }
  }

const handleBatchRecognize = () => {
  // 跳转到批量识别页面，或者打开批量识别对话框
  ElMessage.info('批量识别功能即将上线')
  // router.push('/batch-recognize') // 将来可以添加路由
}

const submitCorrection = async () => {
  let actualBreed = ''
  
  if (correctedBreed.value === '__custom__') {
    if (!customBreed.value.trim()) {
      ElMessage.error('请输入实际品种名称')
      return
    }
    actualBreed = customBreed.value.trim()
  } else if (!correctedBreed.value) {
    ElMessage.error('请选择正确品种')
    return
  } else {
    actualBreed = correctedBreed.value
  }
  
  if (!currentRecognitionId.value) {
    ElMessage.error('无法获取识别记录ID')
    return
  }
  
  try {
    const response = await recognizeAPI.correctRecognition(
      currentRecognitionId.value,
      actualBreed,
      correctionReason.value
    )
    
    if (response.success) {
      ElMessage.success('感谢您的反馈！')
      correctedBreed.value = ''
      customBreed.value = ''
      correctionReason.value = ''
    } else {
      ElMessage.error(response.message || '提交失败，请稍后重试')
    }
  } catch (error) {
    console.error('Correction error:', error)
    ElMessage.error(error.response?.data?.error || '提交失败，请稍后重试')
  }
}

const loadHistory = async () => {
  try {
    const response = await recognizeAPI.getHistory()
    if (response.success) {
      history.value = response.data || []
    }
  } catch (error) {
    console.error('Failed to load history:', error)
  }
}

const deleteHistoryItem = async (id) => {
  try {
    const response = await recognizeAPI.deleteHistory(id)
    if (response.success) {
      ElMessage.success('删除成功')
      history.value = history.value.filter(item => item.id !== id)
    }
  } catch (error) {
    ElMessage.error('删除失败，请稍后重试')
  }
}

const addFavorite = async () => {
  if (!breedInfo.value) return
  
  try {
    const response = await favoritesAPI.addFavorite({ breed: breedInfo.value.breed })
    if (response.success) {
      ElMessage.success('收藏成功')
    } else {
      ElMessage.error(response.message || '收藏失败')
    }
  } catch (error) {
    ElMessage.error('收藏失败，请稍后重试')
  }
}

const goToBreedDetail = () => {
  if (breedInfo.value) {
    window.location.href = `/breed/${encodeURIComponent(breedInfo.value.breed)}`
  }
}

onMounted(() => {
  loadAllBreeds()
  const token = localStorage.getItem('token')
  if (token) {
    loadHistory()
  }
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
  position: relative;
}

.upload-area.dragging {
  border-color: #667eea;
  background: #f0f4ff;
}

.upload-area.hasImage {
  border-style: solid;
  border-color: #667eea;
}

.file-input {
  display: none;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.upload-hint p {
  color: #333;
  font-size: 16px;
  margin-bottom: 5px;
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

.image-preview {
  position: relative;
  width: 100%;
  max-height: 400px;
  overflow: hidden;
}

.preview-image {
  width: 100%;
  height: auto;
  max-height: 400px;
  object-fit: contain;
  border-radius: 8px;
}

.preview-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.upload-area:hover .preview-overlay {
  opacity: 1;
}

.change-text {
  color: white;
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
  border-radius: 12px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  margin-bottom: 20px;
}

.original-image-section {
  margin-bottom: 20px;
}

.original-image-section h4 {
  margin-bottom: 10px;
}

.original-image {
  width: 100%;
  max-height: 300px;
  object-fit: contain;
  border-radius: 8px;
  border: 2px solid rgba(255, 255, 255, 0.3);
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

.top5-section {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
}

.top5-section h4 {
  margin-bottom: 10px;
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
  opacity: 0.9;
}

.breed-info-card {
  background: #f9fafb;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}

.breed-info-card h3 {
  margin-bottom: 15px;
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
  color: #333;
}

.info-actions {
  display: flex;
  gap: 10px;
}

.correction-section {
  background: #fff9f9;
  border-radius: 12px;
  padding: 15px;
  border: 1px solid #f5d8d8;
}

.correction-section h4 {
  margin-bottom: 10px;
  color: #c0392b;
}

.correction-section > *:not(:last-child) {
  margin-bottom: 10px;
}

.history-section {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.history-list {
  max-height: 400px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.history-item:last-child {
  border-bottom: none;
}

.history-image {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  object-fit: cover;
}

.history-info {
  flex: 1;
  display: flex;
  gap: 15px;
  align-items: center;
}

.history-detail {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.history-breed {
  font-weight: 600;
  color: #333;
}

.history-time {
  font-size: 12px;
  color: #999;
}

.empty-history {
  text-align: center;
  color: #999;
  padding: 20px;
}
</style>
