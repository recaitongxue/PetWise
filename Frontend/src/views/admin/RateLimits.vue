<template>
  <AdminLayout>
    <div class="rate-limits-page">
      <div class="page-header">
        <div class="header-title">
          <h1>⚡ 限流配置</h1>
          <p class="subtitle">管理API接口的限流规则，保护系统稳定性</p>
        </div>
        <div class="header-actions">
          <button class="add-btn" @click="showAddModal = true">+ 添加配置</button>
        </div>
      </div>
      
      <div class="configs-list">
        <table>
          <thead>
            <tr>
              <th>接口路径</th>
              <th>每日限制</th>
              <th>每小时限制</th>
              <th>每分钟限制</th>
              <th>状态</th>
              <th>描述</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="config in configs" :key="config.id">
              <td>{{ config.endpoint }}</td>
              <td>{{ config.daily_limit }}</td>
              <td>{{ config.hourly_limit }}</td>
              <td>{{ config.per_minute_limit }}</td>
              <td>
                <span class="status-badge" :class="{ active: config.is_enabled }">
                  {{ config.is_enabled ? '启用' : '禁用' }}
                </span>
              </td>
              <td>{{ config.description }}</td>
              <td>
                <button @click="editConfig(config)" class="edit-btn">编辑</button>
                <button @click="toggleConfigStatus(config)" class="toggle-btn">
                  {{ config.is_enabled ? '禁用' : '启用' }}
                </button>
                <button @click="deleteConfig(config.id)" class="delete-btn">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="!configs.length" class="empty-state">
          <p>暂无限流配置</p>
        </div>
      </div>
      
      <!-- 用户限流记录 -->
      <div class="rate-logs-section">
        <h3>用户限流记录</h3>
        <div class="filter-bar">
          <input v-model="searchUser" placeholder="搜索用户ID" @keyup.enter="loadRateLogs" />
          <select v-model="filterEndpoint" @change="loadRateLogs">
            <option value="">全部接口</option>
            <option v-for="config in configs" :key="config.endpoint" :value="config.endpoint">
              {{ config.endpoint }}
            </option>
          </select>
        </div>
        
        <table>
          <thead>
            <tr>
              <th>用户ID</th>
              <th>接口</th>
              <th>请求次数</th>
              <th>重置时间</th>
              <th>更新时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in rateLogs" :key="log.id">
              <td>{{ log.user_id }}</td>
              <td>{{ log.endpoint }}</td>
              <td>{{ log.request_count }}</td>
              <td>{{ log.reset_time }}</td>
              <td>{{ log.updated_at }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- 添加/编辑配置弹窗 -->
    <el-dialog :title="editingConfig ? '编辑限流配置' : '添加限流配置'" v-model="showAddModal" width="500px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="接口路径">
          <el-input v-model="form.endpoint" placeholder="/api/agent/chat" />
        </el-form-item>
        <el-form-item label="每日限制">
          <el-input-number v-model="form.daily_limit" :min="1" :max="10000" />
        </el-form-item>
        <el-form-item label="每小时限制">
          <el-input-number v-model="form.hourly_limit" :min="1" :max="1000" />
        </el-form-item>
        <el-form-item label="每分钟限制">
          <el-input-number v-model="form.per_minute_limit" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" placeholder="配置说明" />
        </el-form-item>
      </el-form>
      
      <div slot="footer" class="dialog-footer">
        <el-button @click="closeModal">取消</el-button>
        <el-button type="primary" @click="submitConfig">{{ editingConfig ? '更新' : '添加' }}</el-button>
      </div>
    </el-dialog>
  </AdminLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import AdminLayout from '@/components/AdminLayout.vue'
import axios from '@/api/axios'

const configs = ref([])
const rateLogs = ref([])
const searchUser = ref('')
const filterEndpoint = ref('')
const showAddModal = ref(false)
const editingConfig = ref(null)

const form = reactive({
  endpoint: '',
  daily_limit: 100,
  hourly_limit: 20,
  per_minute_limit: 5,
  description: ''
})

const loadConfigs = async () => {
  try {
    const response = await axios.get('/admin/rate-limits')
    if (response.success) {
      configs.value = response.data || []
    }
  } catch (error) {
    console.error('Failed to load rate limit configs:', error)
  }
}

const loadRateLogs = async () => {
  try {
    const response = await axios.get('/admin/rate-limits/logs', {
      params: {
        user_id: searchUser.value,
        endpoint: filterEndpoint.value
      }
    })
    if (response.success) {
      rateLogs.value = response.data || []
    }
  } catch (error) {
    console.error('Failed to load rate logs:', error)
  }
}

const submitConfig = async () => {
  if (!form.endpoint) {
    ElMessage.error('请输入接口路径')
    return
  }
  
  try {
    let response
    if (editingConfig.value) {
      response = await axios.put(`/admin/rate-limits/${editingConfig.value.id}`, form)
    } else {
      response = await axios.post('/admin/rate-limits', form)
    }
    
    if (response.success) {
      ElMessage.success(editingConfig.value ? '更新成功' : '添加成功')
      closeModal()
      loadConfigs()
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const editConfig = (config) => {
  editingConfig.value = config
  form.endpoint = config.endpoint
  form.daily_limit = config.daily_limit
  form.hourly_limit = config.hourly_limit
  form.per_minute_limit = config.per_minute_limit
  form.description = config.description || ''
  showAddModal.value = true
}

const toggleConfigStatus = async (config) => {
  try {
    const response = await axios.put(`/admin/rate-limits/${config.id}`, {
      is_enabled: !config.is_enabled
    })
    if (response.success) {
      ElMessage.success('状态更新成功')
      loadConfigs()
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const deleteConfig = async (configId) => {
  if (!confirm('确定要删除这个限流配置吗？')) return
  
  try {
    const response = await axios.delete(`/admin/rate-limits/${configId}`)
    if (response.success) {
      ElMessage.success('删除成功')
      loadConfigs()
    }
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const closeModal = () => {
  showAddModal.value = false
  editingConfig.value = null
  resetForm()
}

const resetForm = () => {
  form.endpoint = ''
  form.daily_limit = 100
  form.hourly_limit = 20
  form.per_minute_limit = 5
  form.description = ''
}

onMounted(() => {
  loadConfigs()
  loadRateLogs()
})
</script>

<style scoped>
.rate-limits-page {
  background: #f5f7fa;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
}

.add-btn {
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.configs-list, .rate-logs-section {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.rate-logs-section h3 {
  margin: 0 0 15px 0;
}

.filter-bar {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.filter-bar input, .filter-bar select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
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
  background: #f5f7fa;
  color: #666;
}

.status-badge.active {
  background: #f0f9eb;
  color: #67c23a;
}

.edit-btn, .toggle-btn, .delete-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  margin-right: 5px;
}

.edit-btn {
  background: #e6f7ff;
  color: #1890ff;
}

.toggle-btn {
  background: #f5f7fa;
  color: #666;
}

.delete-btn {
  background: #fff2f0;
  color: #f56c6c;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
}
</style>