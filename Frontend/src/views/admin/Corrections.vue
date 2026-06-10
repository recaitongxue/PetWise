<template>
  <AdminLayout>
    <div class="corrections-page">
      <div class="page-header">
        <div class="header-title">
          <h1>🔄 用户纠错记录</h1>
          <p class="subtitle">审核和管理用户提交的识别纠错请求</p>
        </div>
      </div>
      
      <div class="filter-bar">
        <select v-model="filterStatus" @change="loadCorrections">
          <option value="">全部状态</option>
          <option value="pending">待审核</option>
          <option value="approved">已通过</option>
          <option value="rejected">已拒绝</option>
        </select>
        <input v-model="searchBreed" placeholder="搜索品种" @keyup.enter="loadCorrections" />
      </div>
      
      <div class="corrections-list">
        <table>
          <thead>
            <tr>
              <th>识别ID</th>
              <th>用户ID</th>
              <th>原品种</th>
              <th>纠正品种</th>
              <th>置信度</th>
              <th>原因</th>
              <th>状态</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="correction in corrections" :key="correction.id">
              <td>{{ correction.recognition_id }}</td>
              <td>{{ correction.user_id }}</td>
              <td>{{ correction.original_breed }}</td>
              <td>{{ correction.corrected_breed }}</td>
              <td>{{ correction.confidence }}%</td>
              <td>{{ correction.reason || '无' }}</td>
              <td>
                <span class="status-badge" :class="correction.status">
                  {{ getStatusLabel(correction.status) }}
                </span>
              </td>
              <td>{{ correction.created_at }}</td>
              <td>
                <button v-if="correction.status === 'pending'" 
                        @click="approveCorrection(correction)" class="approve-btn">
                  通过
                </button>
                <button v-if="correction.status === 'pending'" 
                        @click="rejectCorrection(correction)" class="reject-btn">
                  拒绝
                </button>
                <button @click="viewDetails(correction)" class="view-btn">详情</button>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="!corrections.length" class="empty-state">
          <p>暂无纠错记录</p>
        </div>
      </div>
      
      <div v-if="pagination.pages > 1" class="pagination">
        <button @click="prevPage" :disabled="pagination.page <= 1">上一页</button>
        <span>{{ pagination.page }} / {{ pagination.pages }}</span>
        <button @click="nextPage" :disabled="pagination.page >= pagination.pages">下一页</button>
      </div>
    </div>
    
    <!-- 详情弹窗 -->
    <el-dialog title="纠错详情" :visible.sync="showDetailModal" width="500px">
      <div v-if="selectedCorrection" class="correction-detail">
        <div class="detail-item">
          <span class="label">识别ID:</span>
          <span class="value">{{ selectedCorrection.recognition_id }}</span>
        </div>
        <div class="detail-item">
          <span class="label">用户ID:</span>
          <span class="value">{{ selectedCorrection.user_id }}</span>
        </div>
        <div class="detail-item">
          <span class="label">原品种:</span>
          <span class="value">{{ selectedCorrection.original_breed }}</span>
        </div>
        <div class="detail-item">
          <span class="label">纠正品种:</span>
          <span class="value">{{ selectedCorrection.corrected_breed }}</span>
        </div>
        <div class="detail-item">
          <span class="label">置信度:</span>
          <span class="value">{{ selectedCorrection.confidence }}%</span>
        </div>
        <div class="detail-item">
          <span class="label">原因:</span>
          <span class="value">{{ selectedCorrection.reason || '无' }}</span>
        </div>
        <div class="detail-item">
          <span class="label">状态:</span>
          <span class="value">{{ getStatusLabel(selectedCorrection.status) }}</span>
        </div>
        <div v-if="selectedCorrection.reviewed_by" class="detail-item">
          <span class="label">审核人:</span>
          <span class="value">{{ selectedCorrection.reviewed_by }}</span>
        </div>
        <div v-if="selectedCorrection.reviewed_at" class="detail-item">
          <span class="label">审核时间:</span>
          <span class="value">{{ selectedCorrection.reviewed_at }}</span>
        </div>
      </div>
    </el-dialog>
  </AdminLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import AdminLayout from '@/components/AdminLayout.vue'
import axios from '@/api/axios'

const corrections = ref([])
const filterStatus = ref('')
const searchBreed = ref('')
const showDetailModal = ref(false)
const selectedCorrection = ref(null)

const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0,
  pages: 0
})

const statusLabels = {
  pending: '待审核',
  approved: '已通过',
  rejected: '已拒绝'
}

const getStatusLabel = (status) => statusLabels[status] || status

const loadCorrections = async () => {
  try {
    const response = await axios.get('/admin/corrections', {
      params: {
        page: pagination.page,
        per_page: pagination.per_page,
        status: filterStatus.value,
        search: searchBreed.value
      }
    })
    
    if (response.success) {
      corrections.value = response.data || []
      pagination.total = response.pagination?.total || 0
      pagination.pages = response.pagination?.pages || 0
    }
  } catch (error) {
    console.error('Failed to load corrections:', error)
  }
}

const approveCorrection = async (correction) => {
  try {
    const response = await axios.put(`/admin/corrections/${correction.id}`, {
      status: 'approved'
    })
    if (response.success) {
      ElMessage.success('已通过')
      loadCorrections()
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const rejectCorrection = async (correction) => {
  try {
    const response = await axios.put(`/admin/corrections/${correction.id}`, {
      status: 'rejected'
    })
    if (response.success) {
      ElMessage.success('已拒绝')
      loadCorrections()
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const viewDetails = (correction) => {
  selectedCorrection.value = correction
  showDetailModal.value = true
}

const prevPage = () => {
  if (pagination.page > 1) {
    pagination.page--
    loadCorrections()
  }
}

const nextPage = () => {
  if (pagination.page < pagination.pages) {
    pagination.page++
    loadCorrections()
  }
}

onMounted(() => {
  loadCorrections()
})
</script>

<style scoped>
.corrections-page {
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

.filter-bar {
  display: flex;
  gap: 15px;
  margin-bottom: 25px;
  flex-wrap: wrap;
}

.filter-bar select, .filter-bar input {
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
  min-width: 160px;
}

.corrections-list {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background: #f9fafb;
  font-weight: 500;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
}

.status-badge.pending {
  background: #fff7e6;
  color: #fa8c16;
}

.status-badge.approved {
  background: #f0f9eb;
  color: #67c23a;
}

.status-badge.rejected {
  background: #fff2f0;
  color: #f56c6c;
}

.approve-btn, .reject-btn, .view-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  margin-right: 5px;
}

.approve-btn {
  background: #f0f9eb;
  color: #67c23a;
}

.reject-btn {
  background: #fff2f0;
  color: #f56c6c;
}

.view-btn {
  background: #e6f7ff;
  color: #1890ff;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 20px;
}

.pagination button {
  padding: 8px 15px;
  background: #f5f7fa;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.correction-detail .detail-item {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.correction-detail .label {
  color: #666;
}

.correction-detail .value {
  color: #333;
}
</style>