<template>
  <AdminLayout>
    <div class="samples-page">
      <div class="page-header">
        <div class="header-title">
          <h1>🔍 难样本管理</h1>
          <p class="subtitle">查看和分析识别困难的样本数据及用户纠错记录</p>
        </div>
      </div>
        
        <div class="stats-section">
          <div class="stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.total || 0 }}</span>
              <span class="stat-label">总数</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">⏳</div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.pending || 0 }}</span>
              <span class="stat-label">待审核</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">✅</div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.approved || 0 }}</span>
              <span class="stat-label">已通过</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">❌</div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.rejected || 0 }}</span>
              <span class="stat-label">已拒绝</span>
            </div>
          </div>
        </div>
        
        <div class="filter-section">
          <div class="filter-bar">
            <el-select v-model="statusFilter" placeholder="筛选状态" @change="handleFilter">
              <el-option label="全部" value="all" />
              <el-option label="待审核" value="pending" />
              <el-option label="已通过" value="approved" />
              <el-option label="已拒绝" value="rejected" />
            </el-select>
            <el-button type="primary" @click="handleExport" :loading="exporting">
              导出已审核样本
            </el-button>
          </div>
        </div>
        
        <div v-if="samples.length" class="sample-list">
          <div 
            v-for="sample in samples" 
            :key="sample.id" 
            class="sample-item"
            :class="`status-${sample.status}`"
          >
            <div class="sample-header">
              <div class="sample-info">
                <span class="status-badge">{{ getStatusName(sample.status) }}</span>
                <span v-if="sample.is_low_confidence" class="badge low-confidence">低置信度</span>
                <span v-if="sample.is_user_corrected" class="badge corrected">用户纠错</span>
              </div>
              <div class="sample-meta">
                <span>{{ sample.user_name || '匿名用户' }}</span>
                <span>{{ sample.created_at }}</span>
              </div>
            </div>
            
            <div class="sample-content">
              <div class="sample-image">
                <img v-if="sample.image_path" :src="getImageUrl(sample.image_path)" alt="样本图片" />
                <div v-else class="no-image">无图片</div>
              </div>
              <div class="sample-details">
                <div class="detail-row">
                  <span class="label">识别结果：</span>
                  <span class="value">{{ sample.predicted_breed }}</span>
                  <span class="confidence">({{ (sample.recognition_confidence * 100).toFixed(1) }}%)</span>
                </div>
                <div v-if="sample.corrected_breed" class="detail-row corrected">
                  <span class="label">正确品种：</span>
                  <span class="value">{{ sample.corrected_breed }}</span>
                </div>
                <div v-if="sample.collected_reason" class="detail-row">
                  <span class="label">收集原因：</span>
                  <span class="value">{{ sample.collected_reason }}</span>
                </div>
                <div v-if="sample.reason" class="detail-row">
                  <span class="label">纠错原因：</span>
                  <span class="value">{{ sample.reason }}</span>
                </div>
                <div v-if="sample.recognition_id" class="detail-row">
                  <span class="label">识别ID：</span>
                  <span class="value">{{ sample.recognition_id }}</span>
                </div>
                <div v-if="sample.user_id" class="detail-row">
                  <span class="label">用户ID：</span>
                  <span class="value">{{ sample.user_id }}</span>
                </div>
                <div v-if="sample.notes" class="detail-row">
                  <span class="label">备注：</span>
                  <span class="value">{{ sample.notes }}</span>
                </div>
              </div>
            </div>
            
            <div v-if="sample.status === 'pending'" class="sample-actions">
              <el-button size="small" type="success" @click="handleReview(sample.id, 'approve')">
                通过
              </el-button>
              <el-button size="small" type="danger" @click="handleReview(sample.id, 'reject')">
                拒绝
              </el-button>
              <el-button size="small" @click="handleRelabel(sample)">
                重新标注
              </el-button>
            </div>
            
            <div v-else-if="sample.status === 'approved'" class="sample-actions">
              <el-button size="small" type="danger" @click="handleReview(sample.id, 'reject')">
                拒绝
              </el-button>
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
        
        <div v-else class="empty-state">暂无数据</div>
        
        <el-dialog title="重新标注" v-model="relabelDialogVisible" width="500px">
          <el-form :model="relabelForm" label-width="100px">
            <el-form-item label="原始识别">
              <span>{{ relabelForm.predicted_breed }}</span>
            </el-form-item>
            <el-form-item label="正确品种">
              <el-select v-model="relabelForm.corrected_breed" placeholder="选择正确品种" filterable>
                <el-option
                  v-for="breed in breeds"
                  :key="breed"
                  :label="breed"
                  :value="breed"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="审核备注">
              <el-input v-model="relabelForm.notes" type="textarea" placeholder="可选备注" />
            </el-form-item>
          </el-form>
          <div slot="footer">
            <el-button @click="relabelDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="handleSaveLabel">保存</el-button>
          </div>
        </el-dialog>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import AdminLayout from '@/components/AdminLayout.vue'
import { adminAPI } from '@/api/admin'
import { recognizeAPI } from '@/api/recognize'

const samples = ref([])
const stats = ref({})
const statusFilter = ref('all')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const exporting = ref(false)
const breeds = ref([])
const relabelDialogVisible = ref(false)
const relabelingId = ref(null)

const relabelForm = reactive({
  predicted_breed: '',
  corrected_breed: '',
  notes: ''
})

const getStatusName = (status) => {
  const names = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝'
  }
  return names[status] || status
}

const getStats = async () => {
  try {
    const response = await adminAPI.getHardExamplesStats()
    if (response.success) {
      stats.value = response.stats || {}
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

const getSamples = async () => {
  try {
    const params = { page: currentPage.value, per_page: pageSize.value }
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    
    const response = await adminAPI.getHardExamples(params)
    if (response.success) {
      samples.value = response.data || []
      if (response.pagination) {
        total.value = response.pagination.total
      }
    }
  } catch (error) {
    console.error('Failed to load samples:', error)
  }
}

const getBreeds = async () => {
  try {
    const response = await recognizeAPI.getClasses()
    if (response.success) {
      const allBreeds = []
      if (response.categories) {
        if (response.categories.dog) allBreeds.push(...response.categories.dog)
        if (response.categories.cat) allBreeds.push(...response.categories.cat)
      }
      breeds.value = allBreeds
    }
  } catch (error) {
    console.error('Failed to load breeds:', error)
  }
}

const handleFilter = () => {
  currentPage.value = 1
  getSamples()
}

const handleTabChange = (type) => {
  typeFilter.value = type
  currentPage.value = 1
  getSamples()
}

const handlePageChange = (page) => {
  currentPage.value = page
  getSamples()
}

const handleReview = async (id, action) => {
  try {
    const response = await adminAPI.reviewHardExample(id, { action })
    if (response.success) {
      ElMessage.success(`样本${action === 'approve' ? '通过' : '拒绝'}成功`)
      await getSamples()
      await getStats()
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleRelabel = (sample) => {
  relabelingId.value = sample.id
  relabelForm.predicted_breed = sample.predicted_breed
  relabelForm.corrected_breed = sample.corrected_breed || ''
  relabelForm.notes = ''
  relabelDialogVisible.value = true
}

const handleSaveLabel = async () => {
  if (!relabelForm.corrected_breed) {
    ElMessage.error('请选择正确品种')
    return
  }

  try {
    const response = await adminAPI.reviewHardExample(relabelingId.value, {
      action: 'relabel',
      new_label: relabelForm.corrected_breed,
      notes: relabelForm.notes
    })
    if (response.success) {
      ElMessage.success('标注成功')
      relabelDialogVisible.value = false
      await getSamples()
      await getStats()
    }
  } catch (error) {
    ElMessage.error('标注失败')
  }
}

const handleExport = async () => {
  exporting.value = true
  try {
    const response = await adminAPI.exportHardExamples({ status: 'approved' })
    if (response) {
      ElMessage.success('导出成功')
      const url = window.URL.createObjectURL(new Blob([response]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'hard_examples.zip')
      document.body.appendChild(link)
      link.click()
      link.remove()
    }
  } catch (error) {
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

const getImageUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  
  if (path.includes(':') || path.includes('\\') || path.includes('/uploads/')) {
    const filename = path.split('/').pop().split('\\').pop()
    return `/uploads/${filename}`
  }
  
  if (path.startsWith('/')) {
    return `/uploads${path}`
  }
  
  return `/uploads/${path}`
}

onMounted(() => {
  getStats()
  getSamples()
  getBreeds()
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
  max-width: 1600px;
  margin: 0 auto;
  padding: 20px;
}

.sidebar {
  width: 220px;
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
  font-size: 14px;
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

.stats-section {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.stat-icon {
  font-size: 32px;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.stat-label {
  font-size: 12px;
  color: #999;
}

.filter-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.filter-bar {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-tabs {
  display: flex;
  gap: 5px;
  background: #f5f7fa;
  padding: 4px;
  border-radius: 8px;
  flex-shrink: 0;
}

.filter-tab {
  padding: 8px 16px;
  border: none;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  color: #666;
  transition: all 0.2s;
}

.filter-tab:hover {
  background: rgba(0, 0, 0, 0.05);
}

.filter-tab.active {
  background: white;
  color: #667eea;
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
}

.sample-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.sample-item {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  border-left: 4px solid #ddd;
}

.sample-item.status-pending {
  border-left-color: #e6a23c;
}

.sample-item.status-approved {
  border-left-color: #67c23a;
}

.sample-item.status-rejected {
  border-left-color: #f56c6c;
}

.sample-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.sample-info {
  display: flex;
  gap: 10px;
  align-items: center;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.status-pending .status-badge {
  background: #e6a23c;
  color: white;
}

.status-approved .status-badge {
  background: #67c23a;
  color: white;
}

.status-rejected .status-badge {
  background: #f56c6c;
  color: white;
}

.badge {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 11px;
}

.badge.low-confidence {
  background: #fff0f0;
  color: #f56c6c;
}

.badge.corrected {
  background: #f0f9ff;
  color: #409eff;
}

.sample-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #999;
}

.sample-content {
  display: flex;
  gap: 20px;
}

.sample-image {
  width: 150px;
  height: 150px;
  border-radius: 8px;
  overflow: hidden;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sample-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image {
  color: #999;
  font-size: 12px;
}

.sample-details {
  flex: 1;
}

.detail-row {
  display: flex;
  gap: 10px;
  margin-bottom: 8px;
  font-size: 14px;
}

.detail-row .label {
  color: #999;
  min-width: 80px;
}

.detail-row .value {
  color: #333;
  font-weight: 500;
}

.detail-row .confidence {
  color: #999;
  font-size: 12px;
}

.detail-row.corrected .value {
  color: #67c23a;
}

.sample-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
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
</style>
