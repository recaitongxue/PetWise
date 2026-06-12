<template>
  <div class="recognize-page">
    <Navbar />
    <div class="container">
      <h1 class="page-title">🐾 宠物品种识别</h1>
      
      <div class="recognize-content" :class="{ 'has-result': result }">
        <!-- 左侧面板：上传区域 + 品种详情 -->
        <div v-if="result" class="left-panel">
          <!-- 上传区域 -->
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
              <el-button @click="openBatchDialog">
                📸 批量识别
              </el-button>
            </div>
          </div>

          <!-- 品种详情 -->
          <div v-if="breedInfo" class="breed-info-section">
            <h3>品种详情</h3>
            <div class="breed-info-grid">
              <div class="info-column">
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
              </div>
              <div class="info-column">
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
            </div>
            <div class="info-actions">
              <el-button @click="addFavorite">❤️ 收藏</el-button>
              <el-button @click="goToBreedDetail">查看详情</el-button>
            </div>
          </div>
        </div>

        <!-- 没有识别结果时显示上传区域 -->
        <div v-if="!result" class="upload-section">
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
            <el-button @click="openBatchDialog">
              📸 批量识别
            </el-button>
          </div>
        </div>

        <!-- 右侧区域：识别结果 -->
        <div v-if="result" class="result-section">
          <h3>识别结果</h3>
          
          <!-- 识别卡片 -->
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

      <!-- 识别历史 -->
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
                <img :src="getImageUrl(item.image_path)" alt="识别图片" class="history-image" />
                <div class="history-detail">
                  <span class="history-breed">{{ item.breed }}</span>
                  <span v-if="isBatchRecord(item.image_path)" class="batch-badge">📸 批量</span>
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
    
    <!-- 批量识别对话框 -->
    <el-dialog title="📸 批量宠物识别" v-model="showBatchDialog" width="800px">
      <div class="batch-upload-section">
        <div 
          class="batch-upload-area" 
          :class="{ dragging: batchIsDragging, hasImages: batchFilesList.length > 0 }"
          @dragenter.prevent="batchIsDragging = true"
          @dragleave.prevent="batchIsDragging = false"
          @dragover.prevent
          @drop.prevent="handleBatchDrop"
          @click="triggerBatchFileInput"
        >
          <input 
            ref="batchFileInput" 
            type="file" 
            accept="image/*" 
            multiple
            class="batch-file-input"
            @change="handleBatchFileSelect"
          />
          
          <div v-if="batchFilesList.length > 0" class="batch-files-preview">
            <div v-for="(file, index) in batchFilesList" :key="index" class="batch-file-item">
              <img :src="file.preview" :alt="file.name" class="batch-file-thumbnail" />
              <span class="batch-file-name">{{ file.name }}</span>
              <button @click.stop="removeBatchFile(index)" class="batch-remove-file">×</button>
            </div>
          </div>
          
          <div v-else class="batch-upload-hint">
            <div class="batch-upload-icon">📷</div>
            <p>点击或拖拽上传多张图片</p>
            <p class="batch-hint">支持 JPG、PNG 格式，最多10张</p>
          </div>
        </div>
        
        <div class="batch-upload-actions">
          <el-button 
            type="primary" 
            @click="handleBatchRecognize" 
            :loading="batchRecognizing"
            :disabled="batchFilesList.length === 0"
          >
            {{ batchRecognizing ? '识别中...' : '开始批量识别' }}
          </el-button>
          <el-button @click="clearBatchResults" :disabled="batchFilesList.length === 0">
            清空
          </el-button>
        </div>
      </div>
      
      <div v-if="batchResultsList.length > 0" class="batch-results-section">
        <h3>识别结果</h3>
        <div class="batch-results-grid">
          <div v-for="(result, index) in batchResultsList" :key="index" class="batch-result-card">
            <img :src="result.image_url" :alt="result.breed" class="batch-result-image" />
            <div class="batch-result-info">
              <div class="batch-breed-name">{{ result.breed }}</div>
              <div class="batch-confidence">置信度: {{ (result.confidence * 100).toFixed(2) }}%</div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
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
const showHistory = ref(true)
const history = ref([])
const correctedBreed = ref('')
const correctionReason = ref('')
const customBreed = ref('')
const allBreeds = ref([])
const currentRecognitionId = ref(null)

// 图片URL处理函数
const getImageUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  
  // 如果是完整路径（如 E:/PetWise/backend/uploads/xxx.jpg），提取文件名
  if (path.includes(':') || path.includes('\\') || path.includes('/uploads/')) {
    const filename = path.split('/').pop().split('\\').pop()
    return `/uploads/${filename}`
  }
  
  if (path.startsWith('/')) {
    return `/uploads${path}`
  }
  
  return `/uploads/${path}`
}

// 判断是否为批量识别记录
const isBatchRecord = (imagePath) => {
  return imagePath && imagePath.startsWith('batch_')
}

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

// 批量识别相关状态
const showBatchDialog = ref(false)
const batchFileInput = ref(null)
const batchIsDragging = ref(false)
const batchFilesList = ref([])
const batchResultsList = ref([])
const batchRecognizing = ref(false)

const openBatchDialog = () => {
  showBatchDialog.value = true
}

const closeBatchDialog = () => {
  showBatchDialog.value = false
  batchFilesList.value = []
  batchResultsList.value = []
}

const triggerBatchFileInput = () => {
  batchFileInput.value?.click()
}

const handleBatchFileSelect = (event) => {
  const files = Array.from(event.target.files)
  addBatchFiles(files)
}

const handleBatchDrop = (event) => {
  batchIsDragging.value = false
  const files = Array.from(event.dataTransfer.files)
  addBatchFiles(files)
}

const addBatchFiles = (files) => {
  const validFiles = files.filter(file => file.type.startsWith('image/'))
  
  if (validFiles.length !== files.length) {
    ElMessage.warning('只支持图片文件')
  }
  
  validFiles.forEach(file => {
    const reader = new FileReader()
    reader.onload = (e) => {
      batchFilesList.value.push({
        file,
        preview: e.target.result,
        name: file.name
      })
    }
    reader.readAsDataURL(file)
  })
}

const removeBatchFile = (index) => {
  batchFilesList.value.splice(index, 1)
}

const handleBatchRecognize = async () => {
  if (batchFilesList.value.length === 0) {
    ElMessage.error('请先上传图片')
    return
  }
  
  if (batchFilesList.value.length > 10) {
    ElMessage.error('每次最多上传10张图片')
    return
  }
  
  batchRecognizing.value = true
  batchResultsList.value = []
  
  try {
    const files = batchFilesList.value.map(item => item.file)
    const response = await recognizeAPI.recognizeBatch(files)
    
    if (response.success) {
      const results = response.results.map((result, index) => ({
        image_url: batchFilesList.value[index].preview,
        breed: result.success ? result.result.breed : '识别失败',
        confidence: result.success ? result.result.confidence : 0,
        filename: result.filename
      }))
      
      batchResultsList.value = results
      ElMessage.success(`批量识别完成，成功 ${response.success_count}/${response.total}`)
      loadHistory() // 刷新历史记录
    } else {
      ElMessage.error(response.message || '批量识别失败')
    }
  } catch (error) {
    console.error('Batch recognize error:', error)
    ElMessage.error(error.response?.data?.error || '网络错误，请稍后重试')
  } finally {
    batchRecognizing.value = false
  }
}

const clearBatchResults = () => {
  batchResultsList.value = []
  batchFilesList.value = []
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
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-title {
  text-align: center;
  font-size: 26px;
  font-weight: 600;
  color: #333;
  margin-bottom: 25px;
  letter-spacing: 2px;
}

.recognize-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.recognize-content.has-result {
  flex-direction: row;
  align-items: flex-start;
  justify-content: flex-start;
  gap: 20px;
}

.left-panel {
  display: flex;
  flex-direction: column;
  gap: 15px;
  width: 400px;
}

.upload-section {
  background: white;
  border-radius: 12px;
  padding: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.06);
  width: 100%;
  transition: all 0.3s ease;
}

.breed-info-section {
  background: white;
  border-radius: 12px;
  padding: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.06);
}

.result-section {
  flex: 1;
  min-width: 500px;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.06);
}

.upload-area {
  border: 2px dashed #ddd;
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  background: #fafbfc;
}

.upload-area:hover {
  border-color: #667eea;
  background: #f8f9ff;
}

.upload-area.dragging {
  border-color: #667eea;
  background: #f0f4ff;
  transform: scale(1.02);
}

.upload-area.hasImage {
  padding: 12px;
  border-style: solid;
  border-color: #667eea;
  background: white;
}

.file-input {
  display: none;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.7;
}

.upload-hint p {
  color: #555;
  font-size: 15px;
  margin-bottom: 5px;
}

.hint {
  font-size: 12px;
  color: #999;
}

.upload-actions {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 12px;
}

.recognize-btn {
  padding: 10px 32px;
  font-size: 15px;
  border-radius: 25px;
  font-weight: 500;
}

.image-preview {
  position: relative;
  width: 100%;
  max-height: 320px;
  overflow: hidden;
  border-radius: 10px;
}

.preview-image {
  width: 100%;
  height: auto;
  max-height: 320px;
  object-fit: contain;
}

.preview-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  border-radius: 10px;
}

.upload-area:hover .preview-overlay {
  opacity: 1;
}

.change-text {
  color: white;
  font-size: 15px;
  font-weight: 500;
}

.result-section h3 {
  margin-bottom: 20px;
  font-size: 20px;
  font-weight: 600;
  color: #333;
  padding-bottom: 10px;
  border-bottom: 2px solid #f0f0f0;
}

.result-card {
  border-radius: 12px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  margin-bottom: 20px;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.result-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
}

.breed-icon {
  font-size: 36px;
}

.breed-name {
  font-size: 24px;
  font-weight: 700;
}

.confidence {
  margin-left: auto;
  opacity: 0.9;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 12px;
  border-radius: 20px;
}

.top5-section {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 10px;
  padding: 15px;
  margin-bottom: 18px;
}

.top5-section h4 {
  margin-bottom: 10px;
  font-size: 14px;
  font-weight: 600;
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
  background: rgba(255, 255, 255, 0.15);
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.top5-item:hover {
  background: rgba(255, 255, 255, 0.25);
}

.rank {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.25);
  border-radius: 50%;
  font-weight: 700;
  font-size: 12px;
}

.class-name {
  flex: 1;
}

.conf-value {
  font-weight: 600;
  opacity: 0.9;
}

.conf-value {
  opacity: 0.9;
  font-size: 12px;
}

.breed-info-section {
  background: #f9fafb;
  border-radius: 12px;
  padding: 20px;
  margin-top: 15px;
}

.breed-info-section h3 {
  margin-bottom: 15px;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.breed-info-grid {
  display: flex;
  gap: 20px;
}

.info-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-item {
  background: white;
  padding: 12px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.info-item .label {
  display: block;
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.info-item .value {
  color: #333;
  font-size: 14px;
}

.info-actions {
  display: flex;
  gap: 8px;
}

.correction-section {
  background: #fff9f9;
  border-radius: 8px;
  padding: 12px;
  border: 1px solid #f5d8d8;
}

.correction-section h4 {
  margin-bottom: 8px;
  color: #c0392b;
  font-size: 14px;
}

.correction-section > *:not(:last-child) {
  margin-bottom: 8px;
}

.history-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.06);
  width: 100%;
  margin-top: 15px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
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

.batch-badge {
  font-size: 11px;
  background: #e8f4ff;
  color: #1890ff;
  padding: 2px 6px;
  border-radius: 4px;
  margin-left: 5px;
}

.empty-history {
  text-align: center;
  color: #999;
  padding: 20px;
}

/* 批量识别对话框样式 */
.batch-upload-section {
  margin-bottom: 20px;
}

.batch-upload-area {
  border: 2px dashed #ddd;
  border-radius: 12px;
  padding: 30px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.batch-upload-area.dragging {
  border-color: #667eea;
  background: #f0f4ff;
}

.batch-upload-area.hasImages {
  padding: 20px;
}

.batch-file-input {
  display: none;
}

.batch-files-preview {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 12px;
}

.batch-file-item {
  position: relative;
}

.batch-file-thumbnail {
  width: 100%;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
  border: 2px solid rgba(102, 126, 234, 0.3);
}

.batch-file-name {
  display: block;
  font-size: 11px;
  margin-top: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.batch-remove-file {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #ff6b6b;
  color: white;
  border: none;
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.batch-upload-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.batch-upload-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

.batch-upload-hint p {
  color: #333;
  font-size: 14px;
  margin-bottom: 4px;
}

.batch-hint {
  font-size: 11px;
  color: #999;
}

.batch-upload-actions {
  margin-top: 16px;
  text-align: center;
}

.batch-results-section {
  margin-top: 20px;
}

.batch-results-section h3 {
  margin-bottom: 16px;
  font-size: 16px;
}

.batch-results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 15px;
}

.batch-result-card {
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid #eee;
}

.batch-result-image {
  width: 100%;
  height: 120px;
  object-fit: cover;
}

.batch-result-info {
  padding: 10px;
  text-align: center;
}

.batch-breed-name {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 4px;
}

.batch-confidence {
  font-size: 11px;
  color: #999;
}
</style>
