<template>
  <div class="admin-page">
    <Navbar />
    
    <div class="admin-container">
      <aside class="sidebar">
        <h2 class="sidebar-title">管理后台</h2>
        <nav class="sidebar-nav">
          <a href="/admin" class="nav-item">📊 仪表盘</a>
          <a href="/admin/users" class="nav-item active">👥 用户管理</a>
          <a href="/admin/models" class="nav-item">🤖 大模型管理</a>
          <a href="/admin/knowledge" class="nav-item">📚 知识库</a>
          <a href="/admin/samples" class="nav-item">🔍 难样本</a>
          <a href="/admin/stats" class="nav-item">📈 数据统计</a>
          <a href="/admin/rate-limits" class="nav-item">⚡ 限流配置</a>
          <a href="/admin/sensitive-words" class="nav-item">🛡️ 敏感词</a>
          <a href="/admin/prompts" class="nav-item">💭 Prompt模板</a>
          <a href="/admin/feedback" class="nav-item">💬 用户反馈</a>
          <a href="/admin/announcements" class="nav-item">📢 公告管理</a>
        </nav>
      </aside>
      
      <main class="main-content">
        <div class="page-header">
          <h1>👥 用户管理</h1>
          <div class="header-actions">
            <el-button type="primary" @click="showAddModal = true">
              <span>+ 新增用户</span>
            </el-button>
            <el-button @click="handleExport">
              <span>📥 导出用户</span>
            </el-button>
            <el-button @click="showImportModal = true">
              <span>📤 导入用户</span>
            </el-button>
          </div>
        </div>
        
        <div class="filter-bar">
          <el-input 
            v-model="searchQuery" 
            placeholder="搜索用户名或邮箱"
            class="search-input"
            @input="handleSearch"
          />
          <el-select v-model="roleFilter" placeholder="筛选角色" @change="loadUsers">
            <el-option label="全部" value="" />
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
          <el-select v-model="statusFilter" placeholder="筛选状态" @change="loadUsers">
            <el-option label="全部" value="" />
            <el-option label="正常" value="active" />
            <el-option label="禁用" value="disabled" />
          </el-select>
        </div>
        
        <div class="stats-row">
          <div class="stat-card">
            <div class="stat-value">{{ stats.total }}</div>
            <div class="stat-label">总用户数</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ stats.admin }}</div>
            <div class="stat-label">管理员</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ stats.active }}</div>
            <div class="stat-label">活跃用户</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ stats.newToday }}</div>
            <div class="stat-label">今日新增</div>
          </div>
        </div>
        
        <div class="users-table">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>用户信息</th>
                <th>邮箱</th>
                <th>角色</th>
                <th>状态</th>
                <th>注册时间</th>
                <th>最后登录</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>{{ user.id }}</td>
                <td>
                  <div class="user-info">
                    <div class="avatar">
                      {{ user.username.charAt(0).toUpperCase() }}
                    </div>
                    <div class="user-detail">
                      <div class="username">{{ user.username }}</div>
                      <div class="user-id">#{{ user.id }}</div>
                    </div>
                  </div>
                </td>
                <td>{{ user.email || '-' }}</td>
                <td>
                  <span :class="['role-badge', user.role]">
                    {{ user.role === 'admin' ? '管理员' : '普通用户' }}
                  </span>
                </td>
                <td>
                  <span :class="['status-badge', user.is_active ? 'active' : 'disabled']">
                    {{ user.is_active ? '正常' : '禁用' }}
                  </span>
                </td>
                <td>{{ formatDate(user.created_at) }}</td>
                <td>{{ user.last_login ? formatDate(user.last_login) : '-' }}</td>
                <td>
                  <div class="action-buttons">
                    <el-button size="small" @click="viewUser(user)">查看</el-button>
                    <el-button size="small" @click="editUser(user)">编辑</el-button>
                    <el-button 
                      size="small" 
                      :type="user.is_active ? 'warning' : 'success'" 
                      @click="toggleUserStatus(user)"
                    >
                      {{ user.is_active ? '禁用' : '启用' }}
                    </el-button>
                    <el-button 
                      size="small" 
                      type="danger" 
                      @click="deleteUser(user)"
                      :disabled="user.role === 'admin'"
                    >
                      删除
                    </el-button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div class="pagination-bar">
          <span class="total-count">共 {{ pagination.total }} 条记录</span>
          <el-pagination
            :current-page="pagination.current"
            :page-size="pagination.size"
            :total="pagination.total"
            @current-change="handlePageChange"
            layout="prev, pager, next, jumper"
          />
        </div>
        
        <!-- 添加用户弹窗 -->
        <el-dialog title="新增用户" :visible.sync="showAddModal">
          <el-form :model="addForm" label-width="80px">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="addForm.username" />
            </el-form-item>
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="addForm.email" />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input type="password" v-model="addForm.password" />
            </el-form-item>
            <el-form-item label="角色">
              <el-select v-model="addForm.role">
                <el-option label="管理员" value="admin" />
                <el-option label="普通用户" value="user" />
              </el-select>
            </el-form-item>
          </el-form>
          
          <div slot="footer" class="dialog-footer">
            <el-button @click="showAddModal = false">取消</el-button>
            <el-button type="primary" @click="addUser">创建</el-button>
          </div>
        </el-dialog>
        
        <!-- 编辑用户弹窗 -->
        <el-dialog title="编辑用户" :visible.sync="showEditModal">
          <el-form :model="editForm" label-width="80px">
            <el-form-item label="用户名">
              <el-input v-model="editForm.username" disabled />
            </el-form-item>
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="editForm.email" />
            </el-form-item>
            <el-form-item label="角色">
              <el-select v-model="editForm.role">
                <el-option label="管理员" value="admin" />
                <el-option label="普通用户" value="user" />
              </el-select>
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="editForm.is_active">
                <el-option :label="true" :value="true" />
                <el-option :label="false" :value="false" />
              </el-select>
            </el-form-item>
          </el-form>
          
          <div slot="footer" class="dialog-footer">
            <el-button @click="showEditModal = false">取消</el-button>
            <el-button type="primary" @click="saveUser">保存</el-button>
          </div>
        </el-dialog>
        
        <!-- 查看用户详情弹窗 -->
        <el-dialog title="用户详情" :visible.sync="showViewModal" width="500px">
          <div class="user-detail-card" v-if="viewUserInfo">
            <div class="detail-avatar">
              {{ viewUserInfo.username.charAt(0).toUpperCase() }}
            </div>
            <h3>{{ viewUserInfo.username }}</h3>
            <p class="detail-email">{{ viewUserInfo.email }}</p>
            
            <div class="detail-info">
              <div class="info-row">
                <span class="info-label">用户ID</span>
                <span class="info-value">#{{ viewUserInfo.id }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">角色</span>
                <span :class="['info-badge', viewUserInfo.role]">
                  {{ viewUserInfo.role === 'admin' ? '管理员' : '普通用户' }}
                </span>
              </div>
              <div class="info-row">
                <span class="info-label">状态</span>
                <span :class="['info-badge', viewUserInfo.is_active ? 'active' : 'disabled']">
                  {{ viewUserInfo.is_active ? '正常' : '禁用' }}
                </span>
              </div>
              <div class="info-row">
                <span class="info-label">注册时间</span>
                <span class="info-value">{{ formatDate(viewUserInfo.created_at) }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">最后登录</span>
                <span class="info-value">{{ viewUserInfo.last_login ? formatDate(viewUserInfo.last_login) : '-' }}</span>
              </div>
            </div>
          </div>
          
          <div slot="footer" class="dialog-footer">
            <el-button @click="showViewModal = false">关闭</el-button>
          </div>
        </el-dialog>
        
        <!-- 导入用户弹窗 -->
        <el-dialog title="导入用户" :visible.sync="showImportModal">
          <el-form :model="importForm" label-width="80px">
            <el-form-item label="导入文件">
              <el-upload
                class="upload-demo"
                :action="uploadUrl"
                :auto-upload="false"
                :file-list="importFileList"
                :accept=".csv,.xlsx"
                @change="handleFileChange"
              >
                <el-button size="small" type="primary">选择文件</el-button>
                <div slot="tip" class="el-upload__tip">支持 CSV 或 Excel 文件</div>
              </el-upload>
            </el-form-item>
          </el-form>
          
          <div slot="footer" class="dialog-footer">
            <el-button @click="showImportModal = false">取消</el-button>
            <el-button type="primary" @click="handleImport">导入</el-button>
          </div>
        </el-dialog>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import Navbar from '@/components/Navbar.vue'
import { adminAPI } from '@/api/admin'

const users = ref([])
const searchQuery = ref('')
const roleFilter = ref('')
const statusFilter = ref('')
const showAddModal = ref(false)
const showEditModal = ref(false)
const showViewModal = ref(false)
const showImportModal = ref(false)
const editingUserId = ref(null)
const viewUserInfo = ref(null)
const importFileList = ref([])
const uploadUrl = '/admin/users/import'

const stats = reactive({
  total: 0,
  admin: 0,
  active: 0,
  newToday: 0
})

const pagination = reactive({
  current: 1,
  size: 10,
  total: 0
})

const addForm = reactive({
  username: '',
  email: '',
  password: '',
  role: 'user'
})

const editForm = reactive({
  username: '',
  email: '',
  role: 'user',
  is_active: true
})

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const loadUsers = async (page = 1) => {
  try {
    const params = {
      page: page,
      size: pagination.size,
      role: roleFilter.value,
      status: statusFilter.value
    }
    
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    
    const response = await adminAPI.getUsers(params)
    if (response.success) {
      users.value = response.data.data || []
      pagination.total = response.data.total || 0
      pagination.current = page
      
      // 更新统计数据
      const statsResponse = await adminAPI.getUserStats()
      if (statsResponse.success) {
        stats.total = statsResponse.data.total || 0
        stats.admin = statsResponse.data.admin || 0
        stats.active = statsResponse.data.active || 0
        stats.newToday = statsResponse.data.new_today || 0
      }
    }
  } catch (error) {
    console.log('Failed to load users:', error)
  }
}

const handleSearch = () => {
  pagination.current = 1
  loadUsers(1)
}

const handlePageChange = (page) => {
  loadUsers(page)
}

const addUser = async () => {
  try {
    if (!addForm.username || !addForm.email || !addForm.password) {
      ElMessage.error('请填写完整信息')
      return
    }
    
    const response = await adminAPI.createUser({
      username: addForm.username,
      email: addForm.email,
      password: addForm.password,
      role: addForm.role
    })
    
    if (response.success) {
      ElMessage.success('用户创建成功')
      showAddModal.value = false
      addForm.username = ''
      addForm.email = ''
      addForm.password = ''
      addForm.role = 'user'
      await loadUsers()
    }
  } catch (error) {
    ElMessage.error('创建失败')
  }
}

const editUser = (user) => {
  editingUserId.value = user.id
  editForm.username = user.username
  editForm.email = user.email || ''
  editForm.role = user.role
  editForm.is_active = user.is_active
  showEditModal.value = true
}

const viewUser = (user) => {
  viewUserInfo.value = user
  showViewModal.value = true
}

const saveUser = async () => {
  try {
    const response = await adminAPI.updateUser(editingUserId.value, {
      email: editForm.email,
      role: editForm.role,
      is_active: editForm.is_active
    })
    
    if (response.success) {
      ElMessage.success('更新成功')
      showEditModal.value = false
      await loadUsers()
    }
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

const toggleUserStatus = async (user) => {
  try {
    const response = await adminAPI.updateUser(user.id, {
      is_active: !user.is_active
    })
    
    if (response.success) {
      ElMessage.success(user.is_active ? '用户已禁用' : '用户已启用')
      await loadUsers()
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const deleteUser = async (user) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除该用户吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await adminAPI.deleteUser(user.id)
    
    if (response.success) {
      ElMessage.success('删除成功')
      await loadUsers()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleExport = async () => {
  try {
    const response = await adminAPI.exportUsers()
    if (response.success) {
      // 下载文件
      const blob = new Blob([response.data], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `users_${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
      ElMessage.success('导出成功')
    }
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const handleFileChange = (file) => {
  importFileList.value = file
}

const handleImport = async () => {
  try {
    if (!importFileList.value.length) {
      ElMessage.error('请选择文件')
      return
    }
    
    const formData = new FormData()
    formData.append('file', importFileList.value[0].raw)
    
    const response = await adminAPI.importUsers(formData)
    
    if (response.success) {
      ElMessage.success(`成功导入 ${response.data.count} 个用户`)
      showImportModal.value = false
      importFileList.value = []
      await loadUsers()
    }
  } catch (error) {
    ElMessage.error('导入失败')
  }
}

onMounted(() => {
  loadUsers()
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

.filter-bar {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.search-input {
  width: 250px;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #999;
}

.users-table {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.users-table table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th,
.users-table td {
  padding: 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.users-table th {
  background: #f9fafb;
  font-weight: 600;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 16px;
}

.user-detail {
  display: flex;
  flex-direction: column;
}

.username {
  font-weight: 600;
}

.user-id {
  font-size: 12px;
  color: #999;
}

.role-badge, .status-badge {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
}

.role-badge.admin {
  background: #fff2f0;
  color: #f56c6c;
}

.role-badge.user {
  background: #f0f9ff;
  color: #67c23a;
}

.status-badge.active {
  background: #f0f9ff;
  color: #67c23a;
}

.status-badge.disabled {
  background: #f5f5f5;
  color: #999;
}

.action-buttons {
  display: flex;
  gap: 5px;
}

.pagination-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  padding: 15px;
  background: white;
  border-radius: 12px;
}

.total-count {
  color: #666;
}

.user-detail-card {
  text-align: center;
}

.detail-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 32px;
  margin: 0 auto 15px;
}

.user-detail-card h3 {
  margin: 0 0 5px;
  font-size: 20px;
}

.detail-email {
  color: #999;
  margin: 0 0 20px;
}

.detail-info {
  text-align: left;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.info-label {
  color: #999;
}

.info-value {
  font-weight: 500;
}

.info-badge {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
}

.info-badge.admin {
  background: #fff2f0;
  color: #f56c6c;
}

.info-badge.user {
  background: #f0f9ff;
  color: #67c23a;
}

.info-badge.active {
  background: #f0f9ff;
  color: #67c23a;
}

.info-badge.disabled {
  background: #f5f5f5;
  color: #999;
}

.dialog-footer {
  text-align: right;
}

.upload-demo {
  margin-bottom: 15px;
}
</style>
