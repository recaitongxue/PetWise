<template>
  <div class="admin-page">
    <Navbar />
    
    <div class="admin-container">
      <aside class="sidebar">
        <h2 class="sidebar-title">管理后台</h2>
        <nav class="sidebar-nav">
          <a href="/admin" class="nav-item active">📊 仪表盘</a>
          <a href="/admin/users" class="nav-item">👥 用户管理</a>
          <a href="/admin/stats" class="nav-item">📈 数据统计</a>
          <a href="/admin/feedback" class="nav-item">💬 用户反馈</a>
          <a href="/admin/announcements" class="nav-item">📢 公告管理</a>
        </nav>
      </aside>
      
      <main class="main-content">
        <h1>📊 管理仪表盘</h1>
        
        <div class="stats-cards">
          <div class="stat-card">
            <div class="stat-icon">👥</div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.total_users || 0 }}</span>
              <span class="stat-label">总用户数</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🐾</div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.total_pets || 0 }}</span>
              <span class="stat-label">宠物总数</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📸</div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.total_recognitions || 0 }}</span>
              <span class="stat-label">识别次数</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">💬</div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.pending_feedback || 0 }}</span>
              <span class="stat-label">待处理反馈</span>
            </div>
          </div>
        </div>
        
        <div class="quick-actions">
          <h3>快捷操作</h3>
          <div class="action-buttons">
            <button @click="goTo('/admin/users')" class="action-btn">管理用户</button>
            <button @click="goTo('/admin/announcements')" class="action-btn">发布公告</button>
            <button @click="goTo('/admin/feedback')" class="action-btn">查看反馈</button>
            <button @click="goTo('/admin/stats')" class="action-btn">查看统计</button>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Navbar from '@/components/Navbar.vue'
import { adminAPI } from '@/api/admin'

const stats = ref({})

const loadStats = async () => {
  try {
    const response = await adminAPI.getStats()
    if (response.success) {
      stats.value = response.data || {}
    }
  } catch (error) {
    console.log('Failed to load stats:', error)
  }
}

const goTo = (url) => {
  window.location.href = url
}

onMounted(() => {
  loadStats()
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

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.stat-icon {
  font-size: 36px;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.stat-label {
  font-size: 12px;
  color: #999;
}

.quick-actions {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.quick-actions h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
}

.action-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
}

.action-btn {
  padding: 12px;
  background: #f5f7fa;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #eee;
}
</style>