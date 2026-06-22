<template>
  <AdminLayout>
    <div class="sensitive-words-page">
      <div class="page-header">
        <div class="header-title">
          <h1>🛡️ 敏感词管理</h1>
          <p class="subtitle">管理和过滤敏感词汇内容</p>
        </div>
        <div class="header-actions">
          <button class="add-btn" @click="showAddModal = true">+ 添加敏感词</button>
        </div>
      </div>
      
      <div class="filter-bar">
        <select v-model="filterCategory" @change="loadWords">
          <option value="">全部类别</option>
          <option value="medical">医疗相关</option>
          <option value="safety">安全相关</option>
          <option value="legal">法律相关</option>
          <option value="other">其他</option>
        </select>
        <select v-model="filterSeverity" @change="loadWords">
          <option value="">全部严重程度</option>
          <option value="high">高</option>
          <option value="medium">中</option>
          <option value="low">低</option>
        </select>
        <input v-model="searchWord" placeholder="搜索敏感词" @keyup.enter="loadWords" />
      </div>
      
      <div class="words-list">
        <table>
          <thead>
            <tr>
              <th>敏感词</th>
              <th>类别</th>
              <th>严重程度</th>
              <th>状态</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="word in words" :key="word.id">
              <td>{{ word.word }}</td>
              <td>{{ getCategoryLabel(word.category) }}</td>
              <td>
                <span class="severity-badge" :class="word.severity">
                  {{ getSeverityLabel(word.severity) }}
                </span>
              </td>
              <td>
                <span class="status-badge" :class="{ active: word.is_enabled }">
                  {{ word.is_enabled ? '启用' : '禁用' }}
                </span>
              </td>
              <td>{{ word.created_at }}</td>
              <td>
                <button @click="toggleWordStatus(word)" class="toggle-btn">
                  {{ word.is_enabled ? '禁用' : '启用' }}
                </button>
                <button @click="deleteWord(word.id)" class="delete-btn">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="!words.length" class="empty-state">
          <p>暂无敏感词数据</p>
        </div>
      </div>
      
      <div v-if="pagination.pages > 1" class="pagination">
        <button @click="prevPage" :disabled="pagination.page <= 1">上一页</button>
        <span>{{ pagination.page }} / {{ pagination.pages }}</span>
        <button @click="nextPage" :disabled="pagination.page >= pagination.pages">下一页</button>
      </div>
    </div>
    
    <!-- 添加敏感词弹窗 -->
    <el-dialog title="添加敏感词" v-model="showAddModal" width="400px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="敏感词">
          <el-input v-model="form.word" placeholder="请输入敏感词" />
        </el-form-item>
        <el-form-item label="类别">
          <el-select v-model="form.category">
            <el-option label="医疗相关" value="medical" />
            <el-option label="安全相关" value="safety" />
            <el-option label="法律相关" value="legal" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="严重程度">
          <el-select v-model="form.severity">
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <div slot="footer" class="dialog-footer">
        <el-button @click="showAddModal = false">取消</el-button>
        <el-button type="primary" @click="submitWord">添加</el-button>
      </div>
    </el-dialog>
  </AdminLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import AdminLayout from '@/components/AdminLayout.vue'
import axios from '@/api/axios'

const words = ref([])
const filterCategory = ref('')
const filterSeverity = ref('')
const searchWord = ref('')
const showAddModal = ref(false)

const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0,
  pages: 0
})

const form = reactive({
  word: '',
  category: 'medical',
  severity: 'medium'
})

const categoryLabels = {
  medical: '医疗相关',
  safety: '安全相关',
  legal: '法律相关',
  other: '其他'
}

const severityLabels = {
  high: '高',
  medium: '中',
  low: '低'
}

const getCategoryLabel = (cat) => categoryLabels[cat] || cat
const getSeverityLabel = (sev) => severityLabels[sev] || sev

const loadWords = async () => {
  try {
    const response = await axios.get('/admin/sensitive-words', {
      params: {
        page: pagination.page,
        per_page: pagination.per_page,
        category: filterCategory.value,
        severity: filterSeverity.value,
        search: searchWord.value
      }
    })
    
    if (response.success) {
      words.value = response.data || []
      pagination.total = response.pagination?.total || 0
      pagination.pages = response.pagination?.pages || 0
    }
  } catch (error) {
    console.error('Failed to load sensitive words:', error)
  }
}

const submitWord = async () => {
  if (!form.word) {
    ElMessage.error('请输入敏感词')
    return
  }
  
  try {
    const response = await axios.post('/admin/sensitive-words', form)
    if (response.success) {
      ElMessage.success('添加成功')
      showAddModal.value = false
      resetForm()
      loadWords()
    }
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

const toggleWordStatus = async (word) => {
  try {
    const response = await axios.put(`/admin/sensitive-words/${word.id}`, {
      is_enabled: !word.is_enabled
    })
    if (response.success) {
      ElMessage.success('状态更新成功')
      loadWords()
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const deleteWord = async (wordId) => {
  if (!confirm('确定要删除这个敏感词吗？')) return
  
  try {
    const response = await axios.delete(`/admin/sensitive-words/${wordId}`)
    if (response.success) {
      ElMessage.success('删除成功')
      loadWords()
    }
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const resetForm = () => {
  form.word = ''
  form.category = 'medical'
  form.severity = 'medium'
}

const prevPage = () => {
  if (pagination.page > 1) {
    pagination.page--
    loadWords()
  }
}

const nextPage = () => {
  if (pagination.page < pagination.pages) {
    pagination.page++
    loadWords()
  }
}

onMounted(() => {
  loadWords()
})

const loadSensitiveWords = loadWords
const addSensitiveWord = submitWord
const updateSensitiveWord = toggleWordStatus
const deleteSensitiveWord = deleteWord
</script>

<style scoped>
.admin-page {
  min-height: 100vh;
  background: var(--color-bg);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
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
  background: var(--gradient-hero);
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

.words-list {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: var(--shadow-card);
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
  background: var(--color-bg);
  font-weight: 500;
}

.severity-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
}

.severity-badge.high {
  background: #fff2f0;
  color: #f56c6c;
}

.severity-badge.medium {
  background: #fff7e6;
  color: #fa8c16;
}

.severity-badge.low {
  background: #f0f9eb;
  color: #67c23a;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  background: var(--color-bg);
  color: #666;
}

.status-badge.active {
  background: #f0f9eb;
  color: #67c23a;
}

.toggle-btn, .delete-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  margin-right: 5px;
}

.toggle-btn {
  background: var(--color-bg);
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

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 20px;
}

.pagination button {
  padding: 8px 15px;
  background: var(--color-bg);
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>