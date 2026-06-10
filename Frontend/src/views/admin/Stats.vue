<template>
  <AdminLayout>
    <div class="stats-page">
      <div class="page-header">
        <div class="header-title">
          <h1>📈 数据统计</h1>
          <p class="subtitle">查看系统运行数据和统计信息</p>
        </div>
        <el-button type="primary" @click="loadStats" :loading="loading" class="refresh-btn">
          🔄 刷新数据
        </el-button>
      </div>
        
      <!-- 实时监控卡片 -->
      <div class="monitoring-section">
        <h2>🔴 实时监控</h2>
        <div class="monitoring-grid">
          <div class="monitor-card">
            <div class="monitor-header">
              <span class="monitor-icon">👥</span>
              <span class="monitor-title">今日活跃用户</span>
            </div>
            <div class="monitor-value">{{ realtimeStats.today?.today_users || 0 }}</div>
            <div class="monitor-trend">
              <span class="trend-label">较昨日</span>
              <span :class="['trend-value', realtimeStats.today?.today_users >= 10 ? 'positive' : 'negative']">
                {{ realtimeStats.today?.today_users >= 10 ? '📈' : '📉' }}
              </span>
            </div>
          </div>
          
          <div class="monitor-card">
            <div class="monitor-header">
              <span class="monitor-icon">📸</span>
              <span class="monitor-title">今日识别次数</span>
            </div>
            <div class="monitor-value">{{ realtimeStats.today?.today_recognitions || 0 }}</div>
            <div class="monitor-subtitle">总请求: {{ realtimeStats.today?.today_requests || 0 }}</div>
          </div>
          
          <div class="monitor-card">
            <div class="monitor-header">
              <span class="monitor-icon">🤖</span>
              <span class="monitor-title">今日AI对话</span>
            </div>
            <div class="monitor-value">{{ realtimeStats.today?.today_chats || 0 }}</div>
            <div class="monitor-subtitle">次</div>
          </div>
          
          <div class="monitor-card">
            <div class="monitor-header">
              <span class="monitor-icon">💻</span>
              <span class="monitor-title">CPU使用率</span>
            </div>
            <div class="monitor-value">{{ realtimeStats.system?.cpu_usage || 0 }}%</div>
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: (realtimeStats.system?.cpu_usage || 0) + '%' }"
                :class="{ 'high': (realtimeStats.system?.cpu_usage || 0) > 80 }"
              ></div>
            </div>
          </div>
          
          <div class="monitor-card">
            <div class="monitor-header">
              <span class="monitor-icon">🧠</span>
              <span class="monitor-title">内存使用</span>
            </div>
            <div class="monitor-value">{{ realtimeStats.system?.memory_usage || 0 }}%</div>
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: (realtimeStats.system?.memory_usage || 0) + '%' }"
                :class="{ 'high': (realtimeStats.system?.memory_usage || 0) > 80 }"
              ></div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 基础统计卡片 -->
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
      
      <!-- 7天趋势图 -->
      <div class="section">
        <h3>📊 近7天请求趋势</h3>
        <div v-if="realtimeStats.weekly_trend?.length" class="chart-container">
          <div class="line-chart">
            <div class="chart-y-axis">
              <span v-for="n in 5" :key="n">{{ ((5 - n + 1) * maxWeeklyCount / 5).toFixed(0) }}</span>
            </div>
            <div class="chart-content">
              <svg class="chart-svg" viewBox="0 0 600 200" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="lineGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:#667eea;stop-opacity:0.3" />
                    <stop offset="100%" style="stop-color:#667eea;stop-opacity:0" />
                  </linearGradient>
                </defs>
                <path 
                  :d="areaPath" 
                  fill="url(#lineGradient)"
                />
                <path 
                  :d="linePath" 
                  fill="none"
                  stroke="#667eea"
                  stroke-width="2"
                />
                <circle 
                  v-for="(point, index) in chartPoints" 
                  :key="index"
                  :cx="point.x" 
                  :cy="point.y" 
                  r="4"
                  fill="#667eea"
                  class="chart-point"
                />
              </svg>
              <div class="chart-x-axis">
                <span v-for="(item, index) in realtimeStats.weekly_trend" :key="index">
                  {{ formatDate(item.date) }}
                </span>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">暂无数据</div>
      </div>
      
      <!-- 每日识别统计 -->
      <div class="section">
        <h3>📸 每日识别统计</h3>
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
              <span class="bar-label">{{ formatDate(item.date) }}</span>
              <span class="bar-value">{{ item.count }}</span>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">暂无数据</div>
      </div>
      
      <!-- 近期注册用户 -->
      <div class="section">
        <h3>👥 近期注册用户</h3>
        <div v-if="stats.recent_registrations?.length" class="user-list">
          <div 
            v-for="user in stats.recent_registrations" 
            :key="user.id" 
            class="user-item"
          >
            <div class="user-info">
              <span class="user-avatar">{{ user.username.charAt(0).toUpperCase() }}</span>
              <div>
                <div class="user-name">{{ user.username }}</div>
                <div class="user-email">{{ user.email }}</div>
              </div>
            </div>
            <span class="user-time">{{ formatDateTime(user.created_at) }}</span>
          </div>
        </div>
        <div v-else class="empty-state">暂无数据</div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import AdminLayout from '@/components/AdminLayout.vue'
import { adminAPI } from '@/api/admin'

const stats = ref({})
const realtimeStats = ref({})
const loading = ref(false)
let refreshInterval = null

const loadStats = async () => {
  loading.value = true
  try {
    const [basicRes, realtimeRes] = await Promise.all([
      adminAPI.getStats(),
      adminAPI.getRealtimeStats()
    ])
    
    if (basicRes.success) {
      // getStats() 没有 data 包装层，直接使用响应对象
      stats.value = basicRes
    }
    
    if (realtimeRes.success) {
      // getRealtimeStats() 有 data 包装层
      realtimeStats.value = realtimeRes.data || {}
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
  } finally {
    loading.value = false
  }
}

const maxWeeklyCount = computed(() => {
  const counts = realtimeStats.value.weekly_trend?.map(d => d.count) || [1]
  return Math.max(...counts)
})

const chartPoints = computed(() => {
  const data = realtimeStats.value.weekly_trend || []
  const width = 600
  const height = 200
  const padding = 20
  const points = []
  
  data.forEach((item, index) => {
    const x = padding + (index / (data.length - 1 || 1)) * (width - 2 * padding)
    const y = height - padding - (item.count / maxWeeklyCount.value) * (height - 2 * padding)
    points.push({ x, y })
  })
  
  return points
})

const linePath = computed(() => {
  const points = chartPoints.value
  if (points.length === 0) return ''
  
  return points.map((p, i) => 
    `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`
  ).join(' ')
})

const areaPath = computed(() => {
  const points = chartPoints.value
  if (points.length === 0) return ''
  
  const line = points.map((p, i) => 
    `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`
  ).join(' ')
  
  const lastX = points[points.length - 1]?.x || 0
  const firstX = points[0]?.x || 0
  
  return `${line} L ${lastX} 200 L ${firstX} 200 Z`
})

const getBarHeight = (count) => {
  const maxCount = Math.max(...(stats.value.daily_recognitions?.map(d => d.count) || [1]))
  return (count / maxCount) * 100
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
}

onMounted(() => {
  loadStats()
  // 每30秒自动刷新实时数据
  refreshInterval = setInterval(() => {
    loadStats()
  }, 30000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.stats-page {
  background: #f5f7fa;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 15px;
}

.header-title h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #2c3e50;
}

.subtitle {
  margin: 0;
  color: #7f8c8d;
  font-size: 14px;
}

.refresh-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.monitoring-section {
  background: white;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 25px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.monitoring-section h2 {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.monitoring-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.monitor-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 12px;
  padding: 20px;
  transition: transform 0.2s;
}

.monitor-card:hover {
  transform: translateY(-2px);
}

.monitor-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.monitor-icon {
  font-size: 24px;
}

.monitor-title {
  font-size: 14px;
  color: #666;
}

.monitor-value {
  font-size: 32px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 5px;
}

.monitor-subtitle {
  font-size: 12px;
  color: #94a3b8;
}

.monitor-trend {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
}

.trend-label {
  color: #94a3b8;
}

.trend-value.positive {
  color: #22c55e;
}

.trend-value.negative {
  color: #ef4444;
}

.progress-bar {
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
  margin-top: 10px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 3px;
  transition: width 0.3s;
}

.progress-fill.high {
  background: linear-gradient(90deg, #ff4949, #ff6b6b);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
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
  margin-bottom: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.section h3 {
  margin: 0 0 20px 0;
  font-size: 16px;
  color: #333;
}

.chart-container {
  padding: 10px;
}

.line-chart {
  display: flex;
  height: 250px;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
}

.chart-y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding-right: 10px;
  font-size: 12px;
  color: #999;
}

.chart-content {
  flex: 1;
  position: relative;
}

.chart-svg {
  width: 100%;
  height: 200px;
}

.chart-point {
  transition: all 0.2s;
}

.chart-point:hover {
  r: 6;
}

.chart-x-axis {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  font-size: 12px;
  color: #666;
}

.bar-chart {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 200px;
  padding: 20px;
  background: #f8f9fa;
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

.user-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.user-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
}

.user-name {
  font-weight: 500;
  color: #333;
}

.user-email {
  font-size: 12px;
  color: #999;
}

.user-time {
  font-size: 12px;
  color: #999;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #999;
  background: #f8f9fa;
  border-radius: 8px;
}
</style>
