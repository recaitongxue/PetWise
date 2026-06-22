<template>
  <AdminLayout>
    <div class="announcements-page">
      <div class="page-header">
        <div class="header-title">
          <h1>📢 公告管理</h1>
          <p class="subtitle">发布和管理系统公告信息</p>
        </div>
      </div>
        
        <div class="add-section">
          <h3>{{ editingId ? '编辑公告' : '发布新公告' }}</h3>
          <el-form :model="form" label-width="80px">
            <el-form-item label="标题">
              <el-input v-model="form.title" placeholder="请输入公告标题" />
            </el-form-item>
            <el-form-item label="内容">
              <textarea v-model="form.content" placeholder="请输入公告内容" rows="4" class="custom-textarea" />
            </el-form-item>
            <el-form-item>
              <el-checkbox v-model="form.is_pinned">置顶公告</el-checkbox>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="editingId ? updateAnnouncement() : addAnnouncement()">
                {{ editingId ? '保存修改' : '发布公告' }}
              </el-button>
              <el-button v-if="editingId" @click="cancelEdit">取消编辑</el-button>
            </el-form-item>
          </el-form>
        </div>
        
        <div class="list-section">
          <h3>公告列表</h3>
          
          <div v-if="announcements.length" class="announcement-list">
            <div 
              v-for="ann in announcements" 
              :key="ann.id" 
              class="announcement-item"
            >
              <div class="ann-header">
                <span v-if="ann.is_pinned" class="pin-badge">📌</span>
                <span class="ann-title">{{ ann.title }}</span>
                <div class="ann-actions">
                  <el-button size="small" @click="editAnnouncement(ann)">编辑</el-button>
                  <el-button size="small" type="danger" @click="deleteAnnouncement(ann.id)">删除</el-button>
                </div>
              </div>
              <p class="ann-content">{{ ann.content }}</p>
              <div class="ann-footer">
                <span class="ann-time">{{ ann.created_at }}</span>
              </div>
            </div>
          </div>
          
          <div v-else class="empty-state">暂无公告</div>
        </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AdminLayout from '@/components/AdminLayout.vue'
import { adminAPI } from '@/api/admin'

const announcements = ref([])
const editingId = ref(null)

const form = reactive({
  title: '',
  content: '',
  is_pinned: false
})

const loadAnnouncements = async () => {
  try {
    const response = await adminAPI.getAnnouncements()
    if (response.success) {
      announcements.value = response.data || []
    }
  } catch (error) {
    console.log('Failed to load announcements:', error)
  }
}

const resetForm = () => {
  form.title = ''
  form.content = ''
  form.is_pinned = false
  editingId.value = null
}

const addAnnouncement = async () => {
  if (!form.title || !form.content) {
    ElMessage.error('请填写标题和内容')
    return
  }
  
  try {
    const response = await adminAPI.createAnnouncement({
      title: form.title,
      content: form.content,
      is_pinned: form.is_pinned ? 1 : 0
    })
    
    if (response.success) {
      ElMessage.success('发布成功')
      resetForm()
      await loadAnnouncements()
    }
  } catch (error) {
    ElMessage.error('发布失败')
  }
}

const editAnnouncement = (ann) => {
  editingId.value = ann.id
  form.title = ann.title
  form.content = ann.content
  form.is_pinned = !!ann.is_pinned
}

const cancelEdit = () => {
  resetForm()
}

const updateAnnouncement = async () => {
  if (!editingId.value || !form.title || !form.content) {
    ElMessage.error('请填写标题和内容')
    return
  }

  try {
    const response = await adminAPI.updateAnnouncement(editingId.value, {
      title: form.title,
      content: form.content,
      is_pinned: form.is_pinned ? 1 : 0
    })

    if (response.success) {
      ElMessage.success('更新成功')
      resetForm()
      await loadAnnouncements()
    }
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

const deleteAnnouncement = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这条公告吗？', '确认删除', { type: 'warning' })
    const response = await adminAPI.deleteAnnouncement(id)
    if (response.success) {
      ElMessage.success('删除成功')
      await loadAnnouncements()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const createAnnouncement = addAnnouncement

onMounted(() => {
  loadAnnouncements()
})
</script>

<style scoped>
.page-header {
  margin-bottom: 24px;
}

.header-title h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  color: #2c3e50;
}

.subtitle {
  margin: 0;
  color: #7f8c8d;
  font-size: 14px;
}

.add-section {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: var(--shadow-card);
  margin-bottom: 20px;
}

.add-section h3 {
  margin: 0 0 20px 0;
  font-size: 16px;
}

.custom-textarea {
  width: 100%;
  min-height: 120px;
  padding: 10px 15px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  resize: vertical;
  box-sizing: border-box;
  font-family: inherit;
}

.custom-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
}

.list-section {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: var(--shadow-card);
}

.list-section h3 {
  margin: 0 0 20px 0;
  font-size: 16px;
}

.announcement-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.announcement-item {
  padding: 20px;
  background: var(--color-bg);
  border-radius: 8px;
}

.ann-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.pin-badge {
  font-size: 16px;
}

.ann-title {
  font-weight: 600;
  font-size: 16px;
  flex: 1;
}

.ann-actions {
  display: flex;
  gap: 8px;
}

.ann-content {
  margin: 0;
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}

.ann-footer {
  margin-top: 10px;
}

.ann-time {
  font-size: 12px;
  color: #999;
}

.empty-state {
  text-align: center;
  padding: 60px;
  color: #999;
}
</style>
