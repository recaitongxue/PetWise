<template>
  <AdminLayout>
    <div class="dashboard">
      <div class="page-header">
        <h1>📊 管理仪表盘</h1>
        <p class="page-subtitle">欢迎回来，管理员！查看系统概览数据</p>
      </div>
      
      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-icon bg-blue">👥</div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.total_users || 0 }}</span>
            <span class="stat-label">总用户数</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon bg-purple">🐾</div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.total_pets || 0 }}</span>
            <span class="stat-label">宠物总数</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon bg-green">📸</div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.total_recognitions || 0 }}</span>
            <span class="stat-label">识别次数</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon bg-orange">💬</div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.pending_feedback || 0 }}</span>
            <span class="stat-label">待处理反馈</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon bg-red">🔄</div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.pending_corrections || 0 }}</span>
            <span class="stat-label">待审核纠错</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon bg-cyan">📢</div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.active_announcements || 0 }}</span>
            <span class="stat-label">有效公告</span>
          </div>
        </div>
      </div>
      
      <div class="quick-actions">
        <h3>快捷操作</h3>
        <div class="action-buttons">
          <router-link to="/admin/users" class="action-btn">
            <span>👥 管理用户</span>
          </router-link>
          <router-link to="/admin/announcements" class="action-btn">
            <span>📢 发布公告</span>
          </router-link>
          <router-link to="/admin/feedback" class="action-btn">
            <span>💬 查看反馈</span>
          </router-link>
          <router-link to="/admin/stats" class="action-btn">
            <span>📈 查看统计</span>
          </router-link>
          <router-link to="/admin/corrections" class="action-btn">
            <span>🔄 审核纠错</span>
          </router-link>
          <router-link to="/admin/logs" class="action-btn">
            <span>📋 系统日志</span>
          </router-link>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AdminLayout from '@/components/AdminLayout.vue'
import { adminAPI } from '@/api/admin'

const stats = ref({})

const loadStats = async () => {
  try {
    const response = await adminAPI.getStats()
    if (response.success) {
      // 后端直接返回数据，没有 data 包装层
      const data = response.data || response
      stats.value = typeof data === 'object' && !Array.isArray(data) ? data : {}
    }
  } catch (error) {
    console.log('Failed to load stats:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.dashboard {
  background: var(--color-bg);
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #2c3e50;
}

.page-subtitle {
  margin: 0;
  color: #7f8c8d;
  font-size: 14px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.stat-icon.bg-blue {
  background: var(--gradient-hero);
}

.stat-icon.bg-purple {
  background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
}

.stat-icon.bg-green {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.stat-icon.bg-orange {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.stat-icon.bg-red {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.stat-icon.bg-cyan {
  background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #2c3e50;
}

.stat-label {
  font-size: 13px;
  color: #7f8c8d;
  margin-top: 4px;
}

.quick-actions {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.quick-actions h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.action-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
}

.action-btn {
  padding: 14px 20px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  text-decoration: none;
  color: #334155;
  font-size: 14px;
  font-weight: 500;
  text-align: center;
  transition: all 0.2s;
}

.action-btn:hover {
  background: var(--gradient-hero);
  color: white;
  border-color: transparent;
}
</style>