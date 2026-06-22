<template>
  <AdminLayout>
    <div class="users-page">
      <div class="page-header">
        <div class="header-title">
          <h1>👥 用户管理</h1>
          <p class="subtitle">管理系统用户，包括管理员和普通用户</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="showAddModal = true" class="btn-primary">
            <span>+ 新增用户</span>
          </el-button>
          <el-button @click="handleExport" class="btn-secondary">
            <span>📥 导出用户</span>
          </el-button>
          <el-button @click="showImportModal = true" class="btn-secondary">
            <span>📤 导入用户</span>
          </el-button>
        </div>
      </div>
      
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-icon">👥</div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.total }}</span>
            <span class="stat-label">总用户数</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">👑</div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.admin }}</span>
            <span class="stat-label">管理员</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">✅</div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.active }}</span>
            <span class="stat-label">活跃用户</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🆕</div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.newToday }}</span>
            <span class="stat-label">今日新增</span>
          </div>
        </div>
      </div>
      
      <div class="filter-section">
        <div class="filter-bar">
          <el-input 
            v-model="searchQuery" 
            placeholder="搜索用户名或邮箱"
            class="search-input"
            @input="handleSearch"
          />
          <el-select v-model="roleFilter" placeholder="筛选角色" @change="loadUsers" class="filter-select">
            <el-option label="全部" value="" />
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
          <el-select v-model="statusFilter" placeholder="筛选状态" @change="loadUsers" class="filter-select">
            <el-option label="全部" value="" />
            <el-option label="正常" value="active" />
            <el-option label="禁用" value="disabled" />
          </el-select>
        </div>
      </div>
      
      <div class="table-container">
        <table class="data-table">
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
            <tr v-for="user in users" :key="user.id" class="table-row">
              <td class="col-id">{{ user.id }}</td>
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
                  <button class="action-btn btn-view" @click="viewUser(user)">查看</button>
                  <button class="action-btn btn-edit" @click="editUser(user)">编辑</button>
                  <button 
                    class="action-btn" 
                    :class="user.is_active ? 'btn-warning' : 'btn-success'"
                    @click="toggleUserStatus(user)"
                  >
                    {{ user.is_active ? '禁用' : '启用' }}
                  </button>
                  <button 
                    class="action-btn btn-danger" 
                    @click="deleteUser(user)"
                    :disabled="user.role === 'admin'"
                  >
                    删除
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="users.length === 0" class="empty-state">
          <div class="empty-icon">📭</div>
          <p>暂无用户数据</p>
        </div>
      </div>
      
      <div class="pagination-bar">
        <span class="total-count">共 {{ pagination.total }} 条记录</span>
        <el-pagination
          :current-page="pagination.current"
          :page-size="pagination.size"
          :total="pagination.total"
          @current-change="handlePageChange"
          layout="prev, pager, next, jumper"
          class="pagination"
        />
      </div>
      
      <!-- 添加用户弹窗 -->
      <el-dialog title="新增用户" v-model="showAddModal" width="450px">
        <el-form :model="addForm" label-width="80px" class="form-container">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="addForm.username" placeholder="请输入用户名" />
          </el-form-item>
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="addForm.email" placeholder="请输入邮箱" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input type="password" v-model="addForm.password" placeholder="请输入密码" />
          </el-form-item>
          <el-form-item label="角色">
            <el-select v-model="addForm.role">
              <el-option label="普通用户" value="user" />
              <el-option label="管理员" value="admin" />
            </el-select>
          </el-form-item>
        </el-form>
        
        <div slot="footer" class="dialog-footer">
          <el-button @click="showAddModal = false">取消</el-button>
          <el-button type="primary" @click="addUser">创建</el-button>
        </div>
      </el-dialog>
      
      <!-- 编辑用户弹窗 -->
      <el-dialog title="编辑用户" v-model="showEditModal" width="450px">
        <el-form :model="editForm" label-width="80px" class="form-container">
          <el-form-item label="用户名">
            <el-input v-model="editForm.username" disabled />
          </el-form-item>
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="editForm.email" placeholder="请输入邮箱" />
          </el-form-item>
          <el-form-item label="角色">
            <el-select v-model="editForm.role">
              <el-option label="普通用户" value="user" />
              <el-option label="管理员" value="admin" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="editForm.is_active">
              <el-option label="正常" :value="true" />
              <el-option label="禁用" :value="false" />
            </el-select>
          </el-form-item>
        </el-form>
        
        <div slot="footer" class="dialog-footer">
          <el-button @click="showEditModal = false">取消</el-button>
          <el-button type="primary" @click="saveUser">保存</el-button>
        </div>
      </el-dialog>
      
      <!-- 查看用户详情弹窗 -->
      <el-dialog title="用户详情" v-model="showViewModal" width="500px">
        <div class="user-detail-card" v-if="viewUserInfo">
          <div class="detail-header">
            <div class="detail-avatar">
              {{ viewUserInfo.username.charAt(0).toUpperCase() }}
            </div>
            <div class="detail-title">
              <h3>{{ viewUserInfo.username }}</h3>
              <p class="detail-email">{{ viewUserInfo.email }}</p>
            </div>
          </div>
          
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
      <el-dialog title="导入用户" v-model="showImportModal" width="450px">
        <el-form :model="importForm" label-width="80px" class="form-container">
          <el-form-item label="导入文件">
            <el-upload
              class="upload-demo"
              :action="uploadUrl"
              :auto-upload="false"
              :file-list="importFileList"
              accept=".csv,.xlsx"
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
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AdminLayout from '@/components/AdminLayout.vue'
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

const handleUser = saveUser
</script>

<style scoped>
.users-page {
  background: var(--color-bg);
  min-height: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 20px;
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

.btn-primary {
  background: var(--gradient-hero);
  border: none;
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(41, 182, 246, 0.4);
}

.btn-secondary {
  background: white;
  border: 1px solid #e2e8f0;
  color: #334155;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #f8fafc;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 25px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: var(--gradient-hero);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
}

.stat-label {
  font-size: 13px;
  color: #7f8c8d;
  margin-top: 4px;
}

.filter-section {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 25px;
}

.filter-bar {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.search-input {
  width: 280px;
}

.filter-select {
  width: 150px;
}

.table-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  margin-bottom: 25px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background: #f8fafc;
  padding: 16px 20px;
  text-align: left;
  font-weight: 600;
  color: #475569;
  font-size: 14px;
  border-bottom: 2px solid #e2e8f0;
}

.data-table td {
  padding: 16px 20px;
  border-bottom: 1px solid #f1f5f9;
  font-size: 14px;
  color: #334155;
}

.table-row:hover {
  background: #fafafa;
}

.col-id {
  color: #94a3b8;
  font-size: 13px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--gradient-hero);
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
  color: #2c3e50;
}

.user-id {
  font-size: 12px;
  color: #94a3b8;
}

.role-badge, .status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
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
  background: #dcfce7;
  color: #22c55e;
}

.status-badge.disabled {
  background: #f5f5f5;
  color: #999;
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-view {
  background: #f1f5f9;
  color: #64748b;
}

.btn-view:hover {
  background: #e2e8f0;
}

.btn-edit {
  background: #dbeafe;
  color: #3b82f6;
}

.btn-edit:hover {
  background: #bfdbfe;
}

.btn-warning {
  background: #fef3c7;
  color: #f59e0b;
}

.btn-warning:hover {
  background: #fde68a;
}

.btn-success {
  background: #dcfce7;
  color: #22c55e;
}

.btn-success:hover {
  background: #bbf7d0;
}

.btn-danger {
  background: #fee2e2;
  color: #ef4444;
}

.btn-danger:hover:not(:disabled) {
  background: #fecaca;
}

.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state p {
  color: #94a3b8;
  font-size: 14px;
}

.pagination-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.total-count {
  color: #64748b;
  font-size: 14px;
}

.form-container {
  padding: 10px 0;
}

.dialog-footer {
  text-align: right;
}

.user-detail-card {
  padding: 20px;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 20px;
}

.detail-avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: var(--gradient-hero);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 28px;
}

.detail-title h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #2c3e50;
}

.detail-email {
  margin: 0;
  color: #64748b;
  font-size: 14px;
}

.detail-info {
  background: #f8fafc;
  border-radius: 12px;
  padding: 10px 20px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #e2e8f0;
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  color: #64748b;
  font-size: 14px;
}

.info-value {
  font-weight: 500;
  color: #2c3e50;
}

.info-badge {
  padding: 4px 10px;
  border-radius: 12px;
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
  background: #dcfce7;
  color: #22c55e;
}

.info-badge.disabled {
  background: #f5f5f5;
  color: #999;
}

.upload-demo {
  margin-bottom: 15px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: flex-start;
  }
  
  .search-input {
    width: 100%;
  }
  
  .filter-select {
    width: 120px;
  }
}
</style>