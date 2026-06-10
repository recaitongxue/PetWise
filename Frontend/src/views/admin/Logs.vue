<template>
  <div class="admin-page">
    <Navbar />
    
    <div class="admin-container">
      <aside class="sidebar">
        <h2 class="sidebar-title">管理后台</h2>
        <nav class="sidebar-nav">
          <a href="/admin" class="nav-item">📊 仪表盘</a>
          <a href="/admin/users" class="nav-item">👥 用户管理</a>
          <a href="/admin/models" class="nav-item">🤖 大模型管理</a>
          <a href="/admin/knowledge" class="nav-item">📚 知识库</a>
          <a href="/admin/samples" class="nav-item">🔍 难样本</a>
          <a href="/admin/stats" class="nav-item">📈 数据统计</a>
          <a href="/admin/logs" class="nav-item active">📋 系统日志</a>
          <a href="/admin/rate-limits" class="nav-item">⚡ 限流配置</a>
          <a href="/admin/sensitive-words" class="nav-item">🛡️ 敏感词</a>
          <a href="/admin/prompts" class="nav-item">💭 Prompt模板</a>
          <a href="/admin/feedback" class="nav-item">💬 用户反馈</a>
          <a href="/admin/announcements" class="nav-item">📢 公告管理</a>
        </nav>
      </aside>
      
      <main class="main-content">
        <div class="page-header">
          <h1>📋 系统日志</h1>
          <div class="header-actions">
            <button @click="loadLogs" class="refresh-btn">🔄 刷新</button>
            <button @click="exportLogs" class="export-btn">📥 导出</button>
          </div>
        </div>
        
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
      </main>
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
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import Navbar from '@/components/Navbar.vue'
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
  height: fit-content;
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

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
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
}

.refresh-btn {
  background: #f5f7fa;
  color: #666;
}

.export-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
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