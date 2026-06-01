<template>
  <div class="admin-page">
    <Navbar />
    
    <div class="admin-container">
      <aside class="sidebar">
        <h2 class="sidebar-title">管理后台</h2>
        <nav class="sidebar-nav">
          <a href="/admin" class="nav-item">📊 仪表盘</a>
          <a href="/admin/users" class="nav-item">👥 用户管理</a>
          <a href="/admin/stats" class="nav-item">📈 数据统计</a>
          <a href="/admin/feedback" class="nav-item">💬 用户反馈</a>
          <a href="/admin/announcements" class="nav-item active">📢 公告管理</a>
        </nav>
      </aside>
      
      <main class="main-content">
        <h1>📢 公告管理</h1>
        
        <div class="add-section">
          <h3>发布新公告</h3>
          <el-form :model="form" label-width="80px">
            <el-form-item label="标题">
              <el-input v-model="form.title" placeholder="请输入公告标题" />
            </el-form-item>
            <el-form-item label="内容">
              <el-textarea v-model="form.content" placeholder="请输入公告内容" rows="4" />
            </el-form-item>
            <el-form-item>
              <el-checkbox v-model="form.is_pinned">置顶公告</el-checkbox>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="createAnnouncement">发布公告</el-button>
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
              </div>
              <p class="ann-content">{{ ann.content }}</p>
              <div class="ann-footer">
                <span class="ann-time">{{ ann.created_at }}</span>
              </div>
            </div>
          </div>
          
          <div v-else class="empty-state">暂无公告</div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import Navbar from '@/components/Navbar.vue'
import { adminAPI } from '@/api/admin'

const announcements = ref([])

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

const createAnnouncement = async () => {
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
      form.title = ''
      form.content = ''
      form.is_pinned = false
      await loadAnnouncements()
    }
  } catch (error) {
    ElMessage.error('发布失败')
  }
}

onMounted(() => {
  loadAnnouncements()
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

.add-section {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.add-section h3 {
  margin: 0 0 20px 0;
  font-size: 16px;
}

.list-section {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
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
  background: #f9fafb;
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