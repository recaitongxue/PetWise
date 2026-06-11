<template>
  <AdminLayout>
    <div class="logs-page">
      <div class="page-header">
        <div class="header-title">
          <h1>📋 系统日志</h1>
          <p class="subtitle">查看和管理系统操作日志</p>
        </div>
        <div class="header-actions">
          <button @click="loadLogs" class="refresh-btn">🔄 刷新</button>
          <button @click="exportLogs" class="export-btn">📥 导出</button>
        </div>
      </div>
      
      <div class="filter-section">
        <div class="filter-bar">
          <select v-model="filterAction" @change="loadLogs">
            <option value="">全部操作</option>
            <option value="login">登录</option>
            <option value="logout">退出</option>
            <option value="register">注册</option>
            <option value="recognize">识别</option>
            <option value="agent_chat">AI对话</option>
            <option value="add_pet">添加宠物</option>
            <option value="delete_pet">删除宠物</option>
            <option value="add_comment">添加评论</option>
            <option value="add_favorite">添加收藏</option>
          </select>
          <input v-model="searchUser" placeholder="搜索用户名" @keyup.enter="loadLogs" />
          <input v-model="searchIP" placeholder="搜索IP地址" @keyup.enter="loadLogs" />
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            @change="loadLogs"
          />
        </div>
        
        <div class="logs-list">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>用户</th>
                <th>操作</th>
                <th>详情</th>
                <th>IP地址</th>
                <th>时间</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in logs" :key="log.id">
                <td>{{ log.id }}</td>
                <td>{{ log.username || '匿名' }}</td>
                <td>
                  <span class="action-badge" :class="getActionClass(log.action)">
                    {{ getActionLabel(log.action) }}
                  </span>
                </td>
                <td>
                  <div class="details-cell">
                    <span class="details-preview">{{ getDetailsPreview(log.details) }}</span>
                    <button @click="viewDetails(log)" class="view-btn">查看</button>
                  </div>
                </td>
                <td>{{ log.ip_address || '未知' }}</td>
                <td>{{ log.created_at }}</td>
              </tr>
            </tbody>
          </table>
          
          <div v-if="!logs.length" class="empty-state">
            <p>暂无日志记录</p>
          </div>
        </div>
        
        <div v-if="pagination.pages > 1" class="pagination">
          <button @click="prevPage" :disabled="pagination.page <= 1">上一页</button>
          <span>{{ pagination.page }} / {{ pagination.pages }}</span>
          <button @click="nextPage" :disabled="pagination.page >= pagination.pages">下一页</button>
        </div>
      </div>
      
      <!-- 详情弹窗 -->
      <el-dialog title="日志详情" :visible.sync="showDetailModal" width="600px">
        <div v-if="selectedLog" class="log-detail">
          <div class="detail-item">
            <span class="label">ID:</span>
            <span class="value">{{ selectedLog.id }}</span>
          </div>
          <div class="detail-item">
            <span class="label">用户:</span>
            <span class="value">{{ selectedLog.username || '匿名' }}</span>
          </div>
          <div class="detail-item">
            <span class="label">操作:</span>
            <span class="value">{{ getActionLabel(selectedLog.action) }}</span>
          </div>
          <div class="detail-item">
            <span class="label">IP地址:</span>
            <span class="value">{{ selectedLog.ip_address || '未知' }}</span>
          </div>
          <div class="detail-item">
            <span class="label">时间:</span>
            <span class="value">{{ selectedLog.created_at }}</span>
          </div>
          <div class="detail-item full">
            <span class="label">详情:</span>
            <pre class="details-content">{{ formatDetails(selectedLog.details) }}</pre>
          </div>
        </div>
      </el-dialog>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import AdminLayout from '@/components/AdminLayout.vue'
import axios from '@/api/axios'

const logs = ref([])
const filterAction = ref('')
const searchUser = ref('')
const searchIP = ref('')
const dateRange = ref([])
const showDetailModal = ref(false)
const selectedLog = ref(null)

const pagination = reactive({
  page: 1,
  per_page: 50,
  total: 0,
  pages: 0
})

const actionLabels = {
  login: '登录',
  logout: '退出',
  register: '注册',
  recognize: '识别',
  agent_chat: 'AI对话',
  add_pet: '添加宠物',
  delete_pet: '删除宠物',
  update_pet: '更新宠物',
  add_comment: '添加评论',
  delete_comment: '删除评论',
  add_favorite: '添加收藏',
  remove_favorite: '移除收藏',
  get_advice: '获取建议',
  structured_consultation: '结构化问诊',
  add_health_record: '添加健康记录',
  add_reminder: '添加提醒',
  complete_reminder: '完成提醒'
}

const getActionLabel = (action) => actionLabels[action] || action

const getActionClass = (action) => {
  if (['login', 'register'].includes(action)) return 'auth'
  if (['recognize', 'agent_chat', 'get_advice', 'structured_consultation'].includes(action)) return 'ai'
  if (['add_pet', 'delete_pet', 'update_pet', 'add_comment', 'add_favorite'].includes(action)) return 'data'
  return 'other'
}

const getDetailsPreview = (details) => {
  if (!details) return '无'
  try {
    const data = JSON.parse(details)
    const preview = Object.entries(data).slice(0, 2).map(([k, v]) => `${k}: ${v}`).join(', ')
    return preview.length > 50 ? preview.substring(0, 50) + '...' : preview
  } catch {
    return details.length > 50 ? details.substring(0, 50) + '...' : details
  }
}

const formatDetails = (details) => {
  if (!details) return '无'
  try {
    return JSON.stringify(JSON.parse(details), null, 2)
  } catch {
    return details
  }
}

const loadLogs = async () => {
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page,
      action: filterAction.value,
      user: searchUser.value,
      ip: searchIP.value
    }
    
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0].toISOString().split('T')[0]
      params.end_date = dateRange.value[1].toISOString().split('T')[0]
    }
    
    const response = await axios.get('/admin/logs', { params })
    
    if (response.success) {
      logs.value = response.data || []
      pagination.total = response.pagination?.total || 0
      pagination.pages = response.pagination?.pages || 0
    }
  } catch (error) {
    console.error('Failed to load logs:', error)
  }
}

const viewDetails = (log) => {
  selectedLog.value = log
  showDetailModal.value = true
}

const exportLogs = async () => {
  try {
    const params = {
      action: filterAction.value,
      user: searchUser.value,
      ip: searchIP.value
    }
    
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0].toISOString().split('T')[0]
      params.end_date = dateRange.value[1].toISOString().split('T')[0]
    }
    
    const response = await axios.get('/admin/logs/export', { params })
    
    if (response.success) {
      // 创建下载链接
      const blob = new Blob([response.data], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `logs_${new Date().toISOString().split('T')[0]}.csv`
      a.click()
      window.URL.revokeObjectURL(url)
      ElMessage.success('导出成功')
    }
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const prevPage = () => {
  if (pagination.page > 1) {
    pagination.page--
    loadLogs()
  }
}

const nextPage = () => {
  if (pagination.page < pagination.pages) {
    pagination.page++
    loadLogs()
  }
}

onMounted(() => {
  loadLogs()
})
</script>

<style scoped>
.logs-page {
  background: #f5f7fa;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 15px;
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

.header-actions {
  display: flex;
  gap: 10px;
}

.refresh-btn, .export-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.refresh-btn {
  background: #f8fafc;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.refresh-btn:hover {
  background: #f1f5f9;
}

.export-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.export-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.filter-bar {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filter-bar select, .filter-bar input {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.logs-list {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
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

.action-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
}

.action-badge.auth {
  background: #e6f7ff;
  color: #1890ff;
}

.action-badge.ai {
  background: #fff7e6;
  color: #fa8c16;
}

.action-badge.data {
  background: #f0f9eb;
  color: #67c23a;
}

.action-badge.other {
  background: #f5f7fa;
  color: #666;
}

.details-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.details-preview {
  color: #666;
  font-size: 13px;
}

.view-btn {
  padding: 4px 10px;
  background: #e6f7ff;
  color: #1890ff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
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

.log-detail .detail-item {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.log-detail .detail-item.full {
  flex-direction: column;
}

.log-detail .label {
  color: #666;
  font-weight: 500;
}

.log-detail .value {
  color: #333;
}

.details-content {
  background: #f9fafb;
  padding: 15px;
  border-radius: 8px;
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
}
</style>