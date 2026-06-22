<template>
  <div class="batch-recognize-page">
    <Navbar />
    <div class="container">
      <h1 class="page-title">📸 批量宠物识别</h1>
      
      <div class="upload-section">
        <div 
          class="upload-area" 
          :class="{ dragging: isDragging, hasImages: batchFiles.length > 0 }"
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
            multiple
            class="file-input"
            @change="handleFileSelect"
          />
          
          <div v-if="batchFiles.length > 0" class="files-preview">
            <div v-for="(file, index) in batchFiles" :key="index" class="file-item">
              <img :src="file.preview" :alt="file.name" class="file-thumbnail" />
              <span class="file-name">{{ file.name }}</span>
              <button @click.stop="removeFile(index)" class="remove-file">×</button>
            </div>
          </div>
          
          <div v-else class="upload-hint">
            <div class="upload-icon">📷</div>
            <p>点击或拖拽上传多张图片</p>
            <p class="hint">支持 JPG、PNG 格式</p>
          </div>
        </div>
        
        <div class="upload-actions">
          <el-button 
            type="primary" 
            @click="handleBatchRecognize" 
            :loading="batchRecognizing"
            :disabled="batchFiles.length === 0"
            class="recognize-btn"
          >
            {{ batchRecognizing ? '识别中...' : '开始批量识别' }}
          </el-button>
          <el-button 
            v-if="batchFiles.length > 0 || batchResults.length > 0"
            @click="clearResults"
          >
            清空
          </el-button>
        </div>
      </div>
      
      <div v-if="batchResults.length > 0" class="results-section">
        <div class="results-header">
          <h3>识别结果</h3>
          <span class="results-count">共 {{ batchResults.length }} 张</span>
        </div>
        <div class="results-grid">
          <div v-for="(result, index) in batchResults" :key="index" class="result-card">
            <img :src="result.image_url" :alt="result.breed" class="result-image" />
            <div class="result-info">
              <div class="breed-name">{{ result.breed }}</div>
              <div class="confidence">置信度: {{ (result.confidence * 100).toFixed(2) }}%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import Navbar from '@/components/Navbar.vue'
import { recognizeAPI } from '@/api/recognize'

const fileInput = ref(null)
const isDragging = ref(false)
const batchFiles = ref([])
const batchResults = ref([])
const batchRecognizing = ref(false)

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

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  addFiles(files)
}

const handleDrop = (event) => {
  isDragging.value = false
  const files = Array.from(event.dataTransfer.files)
  addFiles(files)
}

const addFiles = (files) => {
  const validFiles = files.filter(file => file.type.startsWith('image/'))
  
  if (validFiles.length !== files.length) {
    ElMessage.warning('只支持图片文件')
  }
  
  validFiles.forEach(file => {
    const reader = new FileReader()
    reader.onload = (e) => {
      batchFiles.value.push({
        file,
        preview: e.target.result,
        name: file.name
      })
    }
    reader.readAsDataURL(file)
  })
}

const removeFile = (index) => {
  batchFiles.value.splice(index, 1)
}

const handleBatchRecognize = async () => {
  if (batchFiles.value.length === 0) {
    ElMessage.error('请先上传图片')
    return
  }
  
  if (batchFiles.value.length > 10) {
    ElMessage.error('每次最多上传10张图片')
    return
  }
  
  batchRecognizing.value = true
  batchResults.value = []
  
  try {
    const files = batchFiles.value.map(item => item.file)
    const response = await recognizeAPI.recognizeBatch(files)
    
    if (response.success) {
      const results = response.results.map((result, index) => ({
        image_url: batchFiles.value[index].preview,
        breed: result.success ? result.result.breed : '识别失败',
        confidence: result.success ? result.result.confidence : 0,
        filename: result.filename
      }))
      
      batchResults.value = results
      ElMessage.success(`批量识别完成，成功 ${response.success_count}/${response.total}`)
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

const clearResults = () => {
  batchResults.value = []
  batchFiles.value = []
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}
</script>

<style scoped>
.batch-recognize-page {
  min-height: 100vh;
  background: var(--color-bg);
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

.upload-section {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: var(--shadow-card);
  margin-bottom: 30px;
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
  border-color: var(--color-primary);
  background: #f0f4ff;
}

.upload-area.hasImages {
  padding: 20px;
}

.file-input {
  display: none;
}

.files-preview {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 15px;
}

.file-item {
  position: relative;
}

.file-thumbnail {
  width: 100%;
  height: 100px;
  object-fit: cover;
  border-radius: 8px;
  border: 2px solid rgba(41, 182, 246, 0.3);
}

.file-name {
  display: block;
  font-size: 12px;
  margin-top: 5px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remove-file {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #ff6b6b;
  color: white;
  border: none;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
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

.results-section {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: var(--shadow-card);
}

.results-section h3 {
  margin: 0;
  font-size: 20px;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.results-count {
  color: #999;
  font-size: 14px;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.result-card {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #eee;
}

.result-image {
  width: 100%;
  height: 150px;
  object-fit: cover;
}

.result-info {
  padding: 12px;
  text-align: center;
}

.breed-name {
  font-weight: 600;
  margin-bottom: 5px;
}

.confidence {
  font-size: 12px;
  color: #999;
}
</style>
