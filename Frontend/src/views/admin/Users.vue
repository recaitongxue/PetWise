<template>
  <div class="admin-page">
    <Navbar />
    
    <div class="admin-container">
      <aside class="sidebar">
        <h2 class="sidebar-title">管理后台</h2>
        <nav class="sidebar-nav">
          <a href="/admin" class="nav-item">📊 仪表盘</a>
          <a href="/admin/users" class="nav-item active">👥 用户管理</a>
          <a href="/admin/stats" class="nav-item">📈 数据统计</a>
          <a href="/admin/feedback" class="nav-item">💬 用户反馈</a>
          <a href="/admin/announcements" class="nav-item">📢 公告管理</a>
        </nav>
      </aside>
      
      <main class="main-content">
        <h1>👥 用户管理</h1>
        
        <div class="filter-bar">
          <el-input 
            v-model="searchQuery" 
            placeholder="搜索用户名"
            class="search-input"
          />
          <el-select v-model="roleFilter" placeholder="筛选角色">
            <el-option label="全部" value="" />
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </div>
        
        <div class="users-table">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>用户名</th>
                <th>邮箱</th>
                <th>角色</th>
                <th>注册时间</th>
                <th>最后登录</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>{{ user.id }}</td>
                <td>{{ user.username }}</td>
                <td>{{ user.email || '-' }}</td>
                <td>
                  <span :class="['role-badge', user.role]">
                    {{ user.role === 'admin' ? '管理员' : '普通用户' }}
                  </span>
                </td>
                <td>{{ user.created_at }}</td>
                <td>{{ user.last_login || '-' }}</td>
                <td>
                  <button @click="editUser(user)">编辑</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <el-dialog title="编辑用户" :visible.sync="showEditModal">
          <el-form :model="editForm" label-width="80px">
            <el-form-item label="用户名">
              <el-input v-model="editForm.username" disabled />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="editForm.email" />
            </el-form-item>
            <el-form-item label="角色">
              <el-select v-model="editForm.role">
                <el-option label="管理员" value="admin" />
                <el-option label="普通用户" value="user" />
              </el-select>
            </el-form-item>
          </el-form>
          
          <div slot="footer" class="dialog-footer">
            <el-button @click="showEditModal = false">取消</el-button>
            <el-button type="primary" @click="saveUser">保存</el-button>
          </div>
        </el-dialog>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import Navbar from '@/components/Navbar.vue'
import { adminAPI } from '@/api/admin'

const users = ref([])
const searchQuery = ref('')
const roleFilter = ref('')
const showEditModal = ref(false)
const editingUserId = ref(null)

const editForm = reactive({
  username: '',
  email: '',
  role: 'user'
})

const loadUsers = async () => {
  try {
    const response = await adminAPI.getUsers({ role: roleFilter.value })
    if (response.success) {
      users.value = response.data || []
      
      if (searchQuery.value) {
        users.value = users.value.filter(u => 
          u.username.toLowerCase().includes(searchQuery.value.toLowerCase())
        )
      }
    }
  } catch (error) {
    console.log('Failed to load users:', error)
  }
}

const editUser = (user) => {
  editingUserId.value = user.id
  editForm.username = user.username
  editForm.email = user.email || ''
  editForm.role = user.role
  showEditModal.value = true
}

const saveUser = async () => {
  try {
    const response = await adminAPI.updateUser(editingUserId.value, {
      email: editForm.email,
      role: editForm.role
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

.main-content h1 {
  margin: 0 0 20px 0;
  font-size: 24px;
}

.filter-bar {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.search-input {
  width: 200px;
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

.role-badge {
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

.users-table button {
  padding: 6px 12px;
  background: #f5f7fa;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}

.users-table button:hover {
  background: #eee;
}

.dialog-footer {
  text-align: right;
}
</style>