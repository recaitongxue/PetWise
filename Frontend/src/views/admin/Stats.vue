<template>
  <div class="admin-page">
    <Navbar />
    
    <div class="admin-container">
      <aside class="sidebar">
        <h2 class="sidebar-title">管理后台</h2>
        <nav class="sidebar-nav">
          <a href="/admin" class="nav-item">📊 仪表盘</a>
          <a href="/admin/users" class="nav-item">👥 用户管理</a>
          <a href="/admin/stats" class="nav-item active">📈 数据统计</a>
          <a href="/admin/feedback" class="nav-item">💬 用户反馈</a>
          <a href="/admin/announcements" class="nav-item">📢 公告管理</a>
        </nav>
      </aside>
      
      <main class="main-content">
        <h1>📈 数据统计</h1>
        
        <div class="stats-grid">
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
            <div class="stat-icon">❤️</div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.total_favorites || 0 }}</span>
              <span class="stat-label">收藏总数</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">💬</div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.total_comments || 0 }}</span>
              <span class="stat-label">评论总数</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🤖</div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.total_chats || 0 }}</span>
              <span class="stat-label">AI对话次数</span>
            </div>
          </div>
        </div>
        
        <div class="section">
          <h3>近期注册用户</h3>
          <div v-if="stats.recent_registrations?.length" class="user-list">
            <div 
              v-for="user in stats.recent_registrations" 
              :key="user.id" 
              class="user-item"
            >
              <span class="user-name">{{ user.username }}</span>
              <span class="user-time">{{ user.created_at }}</span>
            </div>
          </div>
          <div v-else class="empty-state">暂无数据</div>
        </div>
        
        <div class="section">
          <h3>每日识别统计</h3>
          <div v-if="stats.daily_recognitions?.length" class="chart-container">
            <div class="bar-chart">
              <div 
                v-for="(item, index) in stats.daily_recognitions" 
                :key="index"
                class="bar-item"
              >
                <div 
                  class="bar" 
                  :style="{ height: getBarHeight(item.count) + '%' }"
                ></div>
                <span class="bar-label">{{ item.date }}</span>
                <span class="bar-value">{{ item.count }}</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">暂无数据</div>
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

const getBarHeight = (count) => {
  const maxCount = Math.max(...(stats.value.daily_recognitions?.map(d => d.count) || [1]))
  return (count / maxCount) * 100
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 15px;
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
  font-size: 32px;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 22px;
  font-weight: 600;
  color: #333;
}

.stat-label {
  font-size: 12px;
  color: #999;
}

.section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.section h3 {
  margin: 0 0 20px 0;
  font-size: 16px;
}

.user-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.user-item {
  display: flex;
  justify-content: space-between;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
}

.user-name {
  font-weight: 500;
}

.user-time {
  font-size: 12px;
  color: #999;
}

.bar-chart {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 200px;
  padding: 20px;
  background: #f9fafb;
  border-radius: 8px;
}

.bar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  width: 60px;
}

.bar {
  width: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px 4px 0 0;
  min-height: 10px;
  transition: height 0.3s;
}

.bar-label {
  font-size: 12px;
  color: #666;
}

.bar-value {
  font-size: 14px;
  font-weight: 600;
}

.empty-state {
  text-align: center;
  padding: 30px;
  color: #999;
}
</style>