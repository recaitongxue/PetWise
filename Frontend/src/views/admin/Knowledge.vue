<template>
  <AdminLayout>
    <div class="knowledge-page">
      <div class="page-header">
        <div class="header-title">
          <h1>📚 知识库管理</h1>
          <p class="subtitle">管理和维护宠物知识条目，支持文件导入构建RAG知识库</p>
        </div>
      </div>
        
        <div class="upload-section">
          <h3>📤 文件导入（RAG知识库搭建）</h3>
          <el-form :model="uploadForm" label-width="100px" class="upload-form">
            <el-form-item label="选择文件">
              <el-upload
                class="upload-demo"
                action="/api/admin/knowledge/upload"
                :on-success="handleUploadSuccess"
                :on-error="handleUploadError"
                :on-progress="handleUploadProgress"
                :on-change="handleFileChange"
                :before-upload="beforeUpload"
                :file-list="fileList"
                :auto-upload="false"
                ref="uploadRef"
              >
                <el-button size="small" type="primary">选择文件</el-button>
                <div slot="tip" class="el-upload__tip">
                  支持上传 <strong>.md</strong>、<strong>.docx</strong>、<strong>.pdf</strong>、<strong>.txt</strong> 格式文件
                </div>
              </el-upload>
            </el-form-item>
            <el-form-item label="目标分类">
              <el-select v-model="uploadForm.category" placeholder="选择分类" allow-create filterable>
                <el-option label="喂养指南" value="feeding" />
                <el-option label="健康护理" value="health" />
                <el-option label="训练技巧" value="training" />
                <el-option label="品种知识" value="breeds" />
                <el-option label="常见问题" value="faq" />
                <el-option label="其他" value="general" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button 
                type="primary" 
                @click="submitUpload" 
                :loading="uploading"
                :disabled="!fileList.length"
              >
                {{ uploading ? '导入中...' : '开始导入' }}
              </el-button>
              <el-button @click="clearFiles">清空文件</el-button>
            </el-form-item>
          </el-form>
          
          <div v-if="uploadProgress > 0 && uploadProgress < 100" class="upload-progress">
            <el-progress :percentage="uploadProgress" :status="uploadProgressStatus" />
          </div>
          
          <div v-if="uploadResult" class="upload-result" :class="uploadResult.success ? 'success' : 'error'">
            <div class="result-icon">{{ uploadResult.success ? '✓' : '✗' }}</div>
            <div class="result-content">
              <div class="result-title">{{ uploadResult.success ? '导入成功' : '导入失败' }}</div>
              <div class="result-message">{{ uploadResult.message }}</div>
              <div v-if="uploadResult.success && uploadResult.imported" class="result-detail">
                <span>成功导入 {{ uploadResult.imported }} 条知识</span>
                <span v-if="uploadResult.skipped">，跳过 {{ uploadResult.skipped }} 条</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="add-section">
          <h3>✏️ 添加知识条目</h3>
          <el-form :model="form" label-width="100px" class="knowledge-form">
            <el-form-item label="标题">
              <el-input v-model="form.title" placeholder="知识标题" />
            </el-form-item>
            <el-form-item label="分类">
              <el-select v-model="form.category" placeholder="选择分类" allow-create filterable>
                <el-option label="喂养指南" value="feeding" />
                <el-option label="健康护理" value="health" />
                <el-option label="训练技巧" value="training" />
                <el-option label="品种知识" value="breeds" />
                <el-option label="常见问题" value="faq" />
                <el-option label="其他" value="general" />
              </el-select>
            </el-form-item>
            <el-form-item label="内容">
              <el-input v-model="form.content" type="textarea" :rows="6" placeholder="知识内容" />
            </el-form-item>
            <el-form-item label="标签">
              <el-select v-model="form.tags" multiple placeholder="添加标签" allow-create filterable>
              </el-select>
            </el-form-item>
            <el-form-item label="来源">
              <el-input v-model="form.source" placeholder="知识来源（可选）" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleAdd" :loading="loading">
                {{ loading ? '添加中...' : '添加知识' }}
              </el-button>
            </el-form-item>
          </el-form>
        </div>
        
        <div class="filter-section">
          <h3>📋 知识列表</h3>
          <div class="filter-bar">
            <el-select v-model="categoryFilter" placeholder="筛选分类" clearable>
              <el-option label="全部" value="" />
              <el-option label="喂养指南" value="feeding" />
              <el-option label="健康护理" value="health" />
              <el-option label="训练技巧" value="training" />
              <el-option label="品种知识" value="breeds" />
              <el-option label="常见问题" value="faq" />
              <el-option label="其他" value="general" />
            </el-select>
            <el-button @click="handleSearch">搜索</el-button>
          </div>
        </div>
        
        <div v-if="knowledgeList.length" class="knowledge-list">
          <div 
            v-for="item in knowledgeList" 
            :key="item.id" 
            class="knowledge-item"
          >
            <div class="knowledge-header">
              <div class="knowledge-meta">
                <span class="category-badge">{{ getCategoryName(item.category) }}</span>
                <span class="date">{{ item.created_at }}</span>
              </div>
              <div class="knowledge-actions">
                <el-button size="small" @click="handleEdit(item)">编辑</el-button>
                <el-button size="small" type="danger" @click="handleDelete(item.id)">删除</el-button>
              </div>
            </div>
            <h4>{{ item.title }}</h4>
            <p class="knowledge-content">{{ truncateContent(item.content) }}</p>
            <div v-if="item.tags" class="tags">
              <span 
                v-for="tag in (typeof item.tags === 'string' ? item.tags.split(',') : item.tags)" 
                :key="tag" 
                class="tag"
              >
                {{ tag.trim() }}
              </span>
            </div>
          </div>
          
          <el-pagination
            v-if="total > pageSize"
            layout="prev, pager, next"
            :total="total"
            :page-size="pageSize"
            :current-page="currentPage"
            @current-change="handlePageChange"
            class="pagination"
          />
        </div>
        
        <div v-else class="empty-state">暂无知识条目</div>
        
        <el-dialog title="编辑知识" v-model="editDialogVisible" width="700px">
          <el-form :model="editForm" label-width="100px">
            <el-form-item label="标题">
              <el-input v-model="editForm.title" />
            </el-form-item>
            <el-form-item label="分类">
              <el-select v-model="editForm.category">
                <el-option label="喂养指南" value="feeding" />
                <el-option label="健康护理" value="health" />
                <el-option label="训练技巧" value="training" />
                <el-option label="品种知识" value="breeds" />
                <el-option label="常见问题" value="faq" />
                <el-option label="其他" value="general" />
              </el-select>
            </el-form-item>
            <el-form-item label="内容">
              <el-input v-model="editForm.content" type="textarea" :rows="8" />
            </el-form-item>
            <el-form-item label="标签">
              <el-input v-model="editForm.tags" placeholder="多个标签用逗号分隔" />
            </el-form-item>
            <el-form-item label="来源">
              <el-input v-model="editForm.source" />
            </el-form-item>
          </el-form>
          <div slot="footer">
            <el-button @click="editDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="handleSave">保存</el-button>
          </div>
        </el-dialog>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElProgress } from 'element-plus'
import AdminLayout from '@/components/AdminLayout.vue'
import { adminAPI } from '@/api/admin'

const knowledgeList = ref([])
const loading = ref(false)
const editDialogVisible = ref(false)
const editingId = ref(null)
const categoryFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const uploadRef = ref(null)
const fileList = ref([])
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadProgressStatus = ref('success')
const uploadResult = ref(null)

const form = reactive({
  title: '',
  category: 'general',
  content: '',
  tags: [],
  source: ''
})

const uploadForm = reactive({
  category: 'general'
})

const editForm = reactive({ ...form })

const getCategoryName = (category) => {
  const names = {
    feeding: '喂养指南',
    health: '健康护理',
    training: '训练技巧',
    breeds: '品种知识',
    faq: '常见问题',
    general: '其他'
  }
  return names[category] || category
}

const getKnowledgeList = async () => {
  try {
    const params = { page: currentPage.value, per_page: pageSize.value }
    if (categoryFilter.value) {
      params.category = categoryFilter.value
    }
    
    const response = await adminAPI.getKnowledge(params)
    if (response.success) {
      knowledgeList.value = response.data || []
      if (response.pagination) {
        total.value = response.pagination.total
      }
    }
  } catch (error) {
    console.error('Failed to load knowledge:', error)
  }
}

const handleAdd = async () => {
  if (!form.title || !form.content) {
    ElMessage.error('请填写标题和内容')
    return
  }

  loading.value = true
  try {
    const data = {
      ...form,
      tags: form.tags.join(',')
    }
    const response = await adminAPI.createKnowledge(data)
    if (response.success) {
      ElMessage.success('添加成功')
      await getKnowledgeList()
      resetForm()
    }
  } catch (error) {
    ElMessage.error('添加失败')
  } finally {
    loading.value = false
  }
}

const handleEdit = (item) => {
  editingId.value = item.id
  Object.assign(editForm, {
    title: item.title,
    category: item.category,
    content: item.content,
    tags: item.tags ? (typeof item.tags === 'string' ? item.tags : item.tags.join(',')) : '',
    source: item.source || ''
  })
  editDialogVisible.value = true
}

const handleSave = async () => {
  try {
    const data = {
      ...editForm,
      tags: typeof editForm.tags === 'string' ? editForm.tags : editForm.tags.join(',')
    }
    const response = await adminAPI.updateKnowledge(editingId.value, data)
    if (response.success) {
      ElMessage.success('更新成功')
      editDialogVisible.value = false
      await getKnowledgeList()
    }
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

const handleDelete = async (id) => {
  if (!confirm('确定要删除这条知识吗？')) return

  try {
    const response = await adminAPI.deleteKnowledge(id)
    if (response.success) {
      ElMessage.success('删除成功')
      await getKnowledgeList()
    }
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const handleSearch = () => {
  currentPage.value = 1
  getKnowledgeList()
}

const handlePageChange = (page) => {
  currentPage.value = page
  getKnowledgeList()
}

const resetForm = () => {
  form.title = ''
  form.category = 'general'
  form.content = ''
  form.tags = []
  form.source = ''
}

const truncateContent = (content) => {
  if (!content) return ''
  return content.length > 200 ? content.substring(0, 200) + '...' : content
}

const beforeUpload = (file) => {
  const allowedExtensions = ['.md', '.docx', '.doc', '.pdf', '.txt', '.json']
  const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase()
  
  if (!allowedExtensions.includes(ext)) {
    ElMessage.error(`不支持的文件格式: ${ext}，支持格式: ${allowedExtensions.join(', ')}`)
    return false
  }
  
  const maxSize = 10 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过10MB')
    return false
  }
  
  return true
}

const handleFileChange = (file, uploadFileList) => {
  fileList.value = uploadFileList
}

const handleUploadProgress = (event, file, fileList) => {
  uploadProgress.value = Math.round((event.loaded / event.total) * 100)
  uploadProgressStatus.value = 'success'
}

const handleUploadSuccess = (response, file, fileList) => {
  uploading.value = false
  uploadProgress.value = 100
  
  if (response.success) {
    uploadResult.value = {
      success: true,
      message: response.message,
      imported: response.imported,
      skipped: response.skipped
    }
    ElMessage.success(`文件导入成功，共导入 ${response.imported} 条知识`)
    getKnowledgeList()
    clearFiles()
  } else {
    uploadResult.value = {
      success: false,
      message: response.error || response.message || '导入失败'
    }
    ElMessage.error('文件导入失败: ' + (response.error || '未知错误'))
  }
  
  setTimeout(() => {
    uploadResult.value = null
    uploadProgress.value = 0
  }, 5000)
}

const handleUploadError = (error, file, fileList) => {
  uploading.value = false
  uploadProgress.value = 0
  uploadProgressStatus.value = 'exception'
  
  uploadResult.value = {
    success: false,
    message: error.message || '上传失败'
  }
  ElMessage.error('文件上传失败: ' + error.message)
  
  setTimeout(() => {
    uploadResult.value = null
  }, 5000)
}

const submitUpload = async () => {
  if (!fileList.value.length) {
    ElMessage.warning('请先选择文件')
    return
  }
  
  uploading.value = true
  uploadProgress.value = 0
  uploadResult.value = null
  
  const file = fileList.value[0]
  const formData = new FormData()
  formData.append('file', file.raw)
  formData.append('category', uploadForm.category)
  
  try {
    const response = await adminAPI.uploadKnowledgeFile(formData)
    handleUploadSuccess(response, file, fileList.value)
  } catch (error) {
    handleUploadError(error, file, fileList.value)
  }
}

const clearFiles = () => {
  fileList.value = []
  uploadProgress.value = 0
  uploadResult.value = null
}

onMounted(() => {
  getKnowledgeList()
})
</script>

<style scoped>
.knowledge-page {
  background: #f5f7fa;
}

.page-header {
  margin-bottom: 30px;
}

.header-title h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #2c3e50;
}

.subtitle {
  margin: 0;
  color: #7f8c8d;
  font-size: 14px;
}

.upload-section,
.add-section,
.filter-section,
.list-section {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 25px;
}

.upload-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.upload-section h3,
.add-section h3,
.filter-section h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
}

.upload-section h3 {
  color: white;
}

.upload-form {
  background: white;
  padding: 20px;
  border-radius: 12px;
}

.knowledge-form {
  max-width: 700px;
}

.filter-bar {
  display: flex;
  gap: 15px;
}

.knowledge-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.knowledge-item {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.knowledge-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.knowledge-meta {
  display: flex;
  gap: 15px;
  align-items: center;
}

.category-badge {
  padding: 4px 10px;
  background: #667eea;
  color: white;
  border-radius: 4px;
  font-size: 12px;
}

.date {
  font-size: 12px;
  color: #999;
}

.knowledge-actions {
  display: flex;
  gap: 10px;
}

.knowledge-item h4 {
  margin: 0 0 10px 0;
  font-size: 18px;
}

.knowledge-content {
  margin: 0 0 15px 0;
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  padding: 3px 10px;
  background: #f0f9ff;
  color: #409eff;
  border-radius: 12px;
  font-size: 12px;
}

.pagination {
  text-align: center;
  margin-top: 20px;
}

.empty-state {
  background: white;
  border-radius: 12px;
  padding: 60px;
  text-align: center;
  color: #999;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.upload-progress {
  margin-top: 15px;
}

.upload-result {
  margin-top: 15px;
  padding: 15px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.upload-result.success {
  background: #f0f9eb;
  border: 1px solid #b7eb8f;
}

.upload-result.error {
  background: #fff2f0;
  border: 1px solid #ffccc7;
}

.result-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  flex-shrink: 0;
}

.upload-result.success .result-icon {
  background: #b7eb8f;
  color: #52c41a;
}

.upload-result.error .result-icon {
  background: #ffccc7;
  color: #ff4d4f;
}

.result-content {
  flex: 1;
}

.result-title {
  font-weight: 600;
  font-size: 16px;
  margin-bottom: 4px;
}

.upload-result.success .result-title {
  color: #52c41a;
}

.upload-result.error .result-title {
  color: #ff4d4f;
}

.result-message {
  font-size: 14px;
  color: #666;
}

.result-detail {
  margin-top: 8px;
  font-size: 13px;
  color: #888;
}

.el-upload__tip {
  margin-top: 8px !important;
  color: #666 !important;
}
</style>