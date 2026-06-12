<template>
  <AdminLayout>
    <div class="models-page">
      <div class="page-header">
        <div class="header-title">
          <h1>🤖 大模型管理</h1>
          <p class="subtitle">管理和配置AI大模型</p>
        </div>
      </div>
        
        <div class="add-section">
          <h3>添加新模型</h3>
          <el-form :model="form" label-width="120px" class="model-form">
            <el-form-item label="模型名称">
              <el-input v-model="form.name" placeholder="例如：GPT-4" />
            </el-form-item>
            <el-form-item label="提供商">
              <el-select v-model="form.provider" placeholder="选择提供商">
                <el-option label="OpenAI" value="openai" />
                <el-option label="SiliconFlow" value="siliconflow" />
                <el-option label="Anthropic" value="anthropic" />
                <el-option label="本地部署" value="local" />
              </el-select>
            </el-form-item>
            <el-form-item label="模型标识">
              <el-input v-model="form.model_name" placeholder="例如：gpt-4" />
            </el-form-item>
            <el-form-item label="API地址">
              <el-input v-model="form.base_url" placeholder="API Base URL（可选）" />
            </el-form-item>
            <el-form-item label="API密钥">
              <el-input v-model="form.api_key" type="password" placeholder="API Key（可选）" show-password />
            </el-form-item>
            <el-form-item label="最大Token数">
              <el-input-number v-model="form.max_tokens" :min="100" :max="100000" />
            </el-form-item>
            <el-form-item label="Temperature">
              <el-slider v-model="form.temperature" :min="0" :max="2" :step="0.1" show-input />
            </el-form-item>
            <el-form-item label="设为默认">
              <el-switch v-model="form.is_default" />
            </el-form-item>
            <el-form-item label="描述">
              <el-input v-model="form.description" type="textarea" placeholder="模型描述" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleAdd" :loading="loading">
                {{ loading ? '添加中...' : '添加模型' }}
              </el-button>
            </el-form-item>
          </el-form>
        </div>
        
        <div class="list-section">
          <h3>模型列表</h3>
          <div v-if="models.length" class="model-list">
            <div 
              v-for="model in models" 
              :key="model.id" 
              class="model-card"
              :class="{ 'is-default': model.is_default, 'is-active': model.is_active }"
            >
              <div class="model-header">
                <div class="model-icon">{{ getProviderIcon(model.provider) }}</div>
                <div class="model-info">
                  <h4>{{ model.name }}</h4>
                  <p class="model-id">{{ model.model_name }}</p>
                  <p class="provider">{{ getProviderName(model.provider) }}</p>
                </div>
                <div class="model-badges">
                  <span v-if="model.is_default" class="badge default">默认</span>
                  <span v-if="model.is_active" class="badge active">激活</span>
                </div>
              </div>
              <div class="model-stats">
                <div class="stat">
                  <span class="label">Temperature:</span>
                  <span class="value">{{ model.temperature }}</span>
                </div>
                <div class="stat">
                  <span class="label">Max Tokens:</span>
                  <span class="value">{{ model.max_tokens }}</span>
                </div>
              </div>
              <p v-if="model.description" class="model-desc">{{ model.description }}</p>
              <div class="model-actions">
                <el-button size="small" @click="handleEdit(model)">编辑</el-button>
                <el-button 
                  v-if="!model.is_default" 
                  size="small" 
                  type="primary"
                  @click="handleSetDefault(model.id)"
                >
                  设为默认
                </el-button>
                <el-button 
                  size="small" 
                  type="danger"
                  @click="handleDelete(model.id)"
                >
                  删除
                </el-button>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">暂无模型，请添加</div>
        </div>
        
        <el-dialog title="编辑模型" v-model="editDialogVisible" width="600px">
          <el-form :model="editForm" label-width="120px">
            <el-form-item label="模型名称">
              <el-input v-model="editForm.name" />
            </el-form-item>
            <el-form-item label="提供商">
              <el-select v-model="editForm.provider">
                <el-option label="OpenAI" value="openai" />
                <el-option label="SiliconFlow" value="siliconflow" />
                <el-option label="Anthropic" value="anthropic" />
                <el-option label="本地部署" value="local" />
              </el-select>
            </el-form-item>
            <el-form-item label="模型标识">
              <el-input v-model="editForm.model_name" />
            </el-form-item>
            <el-form-item label="API地址">
              <el-input v-model="editForm.base_url" />
            </el-form-item>
            <el-form-item label="API密钥">
              <el-input v-model="editForm.api_key" type="password" show-password />
            </el-form-item>
            <el-form-item label="最大Token数">
              <el-input-number v-model="editForm.max_tokens" :min="100" :max="100000" />
            </el-form-item>
            <el-form-item label="Temperature">
              <el-slider v-model="editForm.temperature" :min="0" :max="2" :step="0.1" show-input />
            </el-form-item>
            <el-form-item label="设为默认">
              <el-switch v-model="editForm.is_default" />
            </el-form-item>
            <el-form-item label="描述">
              <el-input v-model="editForm.description" type="textarea" />
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
import { ElMessage } from 'element-plus'
import AdminLayout from '@/components/AdminLayout.vue'
import { adminAPI } from '@/api/admin'

const models = ref([])
const loading = ref(false)
const editDialogVisible = ref(false)
const editingId = ref(null)

const form = reactive({
  name: '',
  provider: 'openai',
  model_name: '',
  base_url: '',
  api_key: '',
  max_tokens: 2048,
  temperature: 0.7,
  is_default: false,
  description: ''
})

const editForm = reactive({ ...form })

const getModels = async () => {
  try {
    const response = await adminAPI.getLLMModels()
    if (response.success) {
      models.value = response.data || []
    }
  } catch (error) {
    console.error('Failed to load models:', error)
  }
}

const handleAdd = async () => {
  if (!form.name || !form.model_name) {
    ElMessage.error('请填写模型名称和标识')
    return
  }

  loading.value = true
  try {
    const response = await adminAPI.createLLMModel(form)
    if (response.success) {
      ElMessage.success('添加成功')
      await getModels()
      resetForm()
    }
  } catch (error) {
    ElMessage.error('添加失败')
  } finally {
    loading.value = false
  }
}

const handleEdit = (model) => {
  editingId.value = model.id
  Object.assign(editForm, model)
  editDialogVisible.value = true
}

const handleSave = async () => {
  try {
    const response = await adminAPI.updateLLMModel(editingId.value, editForm)
    if (response.success) {
      ElMessage.success('更新成功')
      editDialogVisible.value = false
      await getModels()
    }
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

const handleSetDefault = async (id) => {
  try {
    const response = await adminAPI.setDefaultModel(id)
    if (response.success) {
      ElMessage.success('设置成功')
      await getModels()
    }
  } catch (error) {
    ElMessage.error('设置失败')
  }
}

const handleDelete = async (id) => {
  if (!confirm('确定要删除这个模型吗？')) return

  try {
    const response = await adminAPI.deleteLLMModel(id)
    if (response.success) {
      ElMessage.success('删除成功')
      await getModels()
    }
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const resetForm = () => {
  Object.keys(form).forEach(key => {
    if (key === 'max_tokens') form[key] = 2048
    else if (key === 'temperature') form[key] = 0.7
    else if (key === 'is_default') form[key] = false
    else form[key] = ''
  })
}

const getProviderIcon = (provider) => {
  const icons = {
    openai: '🤖',
    siliconflow: '💎',
    anthropic: '🧠',
    local: '💻'
  }
  return icons[provider] || '🤖'
}

const getProviderName = (provider) => {
  const names = {
    openai: 'OpenAI',
    siliconflow: 'SiliconFlow',
    anthropic: 'Anthropic',
    local: '本地部署'
  }
  return names[provider] || provider
}

onMounted(() => {
  getModels()
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

.add-section,
.list-section {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.add-section h3,
.list-section h3 {
  margin: 0 0 20px 0;
  font-size: 16px;
}

.model-form {
  max-width: 600px;
}

.model-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.model-card {
  border: 2px solid #eee;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s;
}

.model-card.is-default {
  border-color: #67c23a;
  background: #f0f9ff;
}

.model-card.is-active {
  border-color: #409eff;
}

.model-header {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  margin-bottom: 15px;
}

.model-icon {
  font-size: 36px;
}

.model-info {
  flex: 1;
}

.model-info h4 {
  margin: 0 0 5px 0;
  font-size: 16px;
}

.model-id {
  margin: 0;
  font-size: 12px;
  color: #666;
  font-family: monospace;
}

.provider {
  margin: 5px 0 0 0;
  font-size: 12px;
  color: #999;
}

.model-badges {
  display: flex;
  gap: 5px;
}

.badge {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.badge.default {
  background: #67c23a;
  color: white;
}

.badge.active {
  background: #409eff;
  color: white;
}

.model-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
  padding: 10px;
  background: #f9fafb;
  border-radius: 6px;
}

.stat {
  display: flex;
  flex-direction: column;
}

.stat .label {
  font-size: 11px;
  color: #999;
}

.stat .value {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.model-desc {
  margin: 0 0 15px 0;
  font-size: 13px;
  color: #666;
  line-height: 1.5;
}

.model-actions {
  display: flex;
  gap: 10px;
}

.empty-state {
  text-align: center;
  padding: 60px;
  color: #999;
}
</style>
