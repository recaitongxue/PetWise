<template>
  <div class="admin-page">
    <Navbar />
    
    <div class="container">
      <div class="page-header">
        <h1 class="page-title">📝 Prompt模板管理</h1>
        <button class="add-btn" @click="showAddModal = true">+ 添加模板</button>
      </div>
      
      <div class="filter-bar">
        <select v-model="filterType" @change="loadPrompts">
          <option value="">全部类型</option>
          <option value="chat">对话</option>
          <option value="consultation">问诊</option>
          <option value="emergency">紧急</option>
          <option value="advice">建议</option>
          <option value="recognition">识别</option>
        </select>
        <input v-model="searchName" placeholder="搜索模板名称" @keyup.enter="loadPrompts" />
      </div>
      
      <div class="prompts-list">
        <table>
          <thead>
            <tr>
              <th>名称</th>
              <th>类型</th>
              <th>版本</th>
              <th>状态</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="prompt in prompts" :key="prompt.id">
              <td>{{ prompt.name }}</td>
              <td>{{ getTypeLabel(prompt.prompt_type) }}</td>
              <td>v{{ prompt.version }}</td>
              <td>
                <span class="status-badge" :class="{ active: prompt.is_active }">
                  {{ prompt.is_active ? '启用' : '禁用' }}
                </span>
              </td>
              <td>{{ prompt.created_at }}</td>
              <td>
                <button @click="viewPrompt(prompt)" class="view-btn">查看</button>
                <button @click="editPrompt(prompt)" class="edit-btn">编辑</button>
                <button @click="togglePromptStatus(prompt)" class="toggle-btn">
                  {{ prompt.is_active ? '禁用' : '启用' }}
                </button>
                <button @click="deletePrompt(prompt.id)" class="delete-btn">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="!prompts.length" class="empty-state">
          <p>暂无Prompt模板</p>
        </div>
      </div>
    </div>
    
    <!-- 添加/编辑Prompt弹窗 -->
    <el-dialog :title="editingPrompt ? '编辑Prompt模板' : '添加Prompt模板'" :visible.sync="showAddModal" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="模板名称" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.prompt_type">
            <el-option label="对话" value="chat" />
            <el-option label="问诊" value="consultation" />
            <el-option label="紧急" value="emergency" />
            <el-option label="建议" value="advice" />
            <el-option label="识别" value="recognition" />
          </el-select>
        </el-form-item>
        <el-form-item label="版本">
          <el-input-number v-model="form.version" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="form.content" type="textarea" :rows="10" placeholder="Prompt内容" />
        </el-form-item>
        <el-form-item label="变量">
          <el-input v-model="form.variables" placeholder="可用变量，逗号分隔" />
        </el-form-item>
      </el-form>
      
      <div slot="footer" class="dialog-footer">
        <el-button @click="closeModal">取消</el-button>
        <el-button type="primary" @click="submitPrompt">{{ editingPrompt ? '更新' : '添加' }}</el-button>
      </div>
    </el-dialog>
    
    <!-- 查看Prompt详情弹窗 -->
    <el-dialog title="Prompt详情" :visible.sync="showViewModal" width="600px">
      <div class="prompt-detail">
        <h3>{{ viewingPrompt?.name }}</h3>
        <div class="detail-item">
          <span class="label">类型:</span>
          <span class="value">{{ getTypeLabel(viewingPrompt?.prompt_type) }}</span>
        </div>
        <div class="detail-item">
          <span class="label">版本:</span>
          <span class="value">v{{ viewingPrompt?.version }}</span>
        </div>
        <div class="detail-item">
          <span class="label">变量:</span>
          <span class="value">{{ viewingPrompt?.variables || '无' }}</span>
        </div>
        <div class="content-box">
          <h4>内容:</h4>
          <pre>{{ viewingPrompt?.content }}</pre>
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

const prompts = ref([])
const filterType = ref('')
const searchName = ref('')
const showAddModal = ref(false)
const showViewModal = ref(false)
const editingPrompt = ref(null)
const viewingPrompt = ref(null)

const form = reactive({
  name: '',
  prompt_type: 'chat',
  version: 1,
  content: '',
  variables: ''
})

const typeLabels = {
  chat: '对话',
  consultation: '问诊',
  emergency: '紧急',
  advice: '建议',
  recognition: '识别'
}

const getTypeLabel = (type) => typeLabels[type] || type

const loadPrompts = async () => {
  try {
    const response = await axios.get('/admin/prompts', {
      params: {
        prompt_type: filterType.value,
        search: searchName.value
      }
    })
    
    if (response.success) {
      prompts.value = response.data || []
    }
  } catch (error) {
    console.error('Failed to load prompts:', error)
  }
}

const submitPrompt = async () => {
  if (!form.name || !form.content) {
    ElMessage.error('请填写名称和内容')
    return
  }
  
  try {
    let response
    if (editingPrompt.value) {
      response = await axios.put(`/admin/prompts/${editingPrompt.value.id}`, form)
    } else {
      response = await axios.post('/admin/prompts', form)
    }
    
    if (response.success) {
      ElMessage.success(editingPrompt.value ? '更新成功' : '添加成功')
      closeModal()
      loadPrompts()
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const viewPrompt = (prompt) => {
  viewingPrompt.value = prompt
  showViewModal.value = true
}

const editPrompt = (prompt) => {
  editingPrompt.value = prompt
  form.name = prompt.name
  form.prompt_type = prompt.prompt_type
  form.version = prompt.version
  form.content = prompt.content
  form.variables = prompt.variables || ''
  showAddModal.value = true
}

const togglePromptStatus = async (prompt) => {
  try {
    const response = await axios.put(`/admin/prompts/${prompt.id}`, {
      is_active: !prompt.is_active
    })
    if (response.success) {
      ElMessage.success('状态更新成功')
      loadPrompts()
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const deletePrompt = async (promptId) => {
  if (!confirm('确定要删除这个Prompt模板吗？')) return
  
  try {
    const response = await axios.delete(`/admin/prompts/${promptId}`)
    if (response.success) {
      ElMessage.success('删除成功')
      loadPrompts()
    }
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const closeModal = () => {
  showAddModal.value = false
  editingPrompt.value = null
  resetForm()
}

const resetForm = () => {
  form.name = ''
  form.prompt_type = 'chat'
  form.version = 1
  form.content = ''
  form.variables = ''
}

onMounted(() => {
  loadPrompts()
})
</script>

<style scoped>
.admin-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 30px 20px;
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

.filter-bar {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.filter-bar select, .filter-bar input {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.prompts-list {
  background: white;
  border-radius: 16px;
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

.view-btn, .edit-btn, .toggle-btn, .delete-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  margin-right: 5px;
}

.view-btn {
  background: #e6f7ff;
  color: #1890ff;
}

.edit-btn {
  background: #f0f9eb;
  color: #67c23a;
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

.prompt-detail h3 {
  margin: 0 0 15px 0;
}

.detail-item {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.detail-item .label {
  color: #666;
}

.detail-item .value {
  color: #333;
}

.content-box {
  margin-top: 15px;
}

.content-box h4 {
  margin: 0 0 10px 0;
}

.content-box pre {
  background: #f9fafb;
  padding: 15px;
  border-radius: 8px;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>