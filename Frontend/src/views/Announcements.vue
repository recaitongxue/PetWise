<template>
  <div class="announcements-page">
    <Navbar />
    
    <div class="container">
      <h1 class="page-title">📢 系统公告</h1>
      <p class="page-subtitle">了解最新的产品动态和重要通知</p>
      
      <div v-if="announcements.length" class="announcements-list">
        <div 
          v-for="item in announcements" 
          :key="item.id" 
          class="announcement-card"
          :class="{ pinned: item.is_pinned }"
        >
          <div v-if="item.is_pinned" class="pinned-badge">📌 置顶</div>
          
          <div class="card-header">
            <h2>{{ item.title }}</h2>
            <span class="date">{{ formatDate(item.created_at) }}</span>
          </div>
          
          <div class="card-content">
            {{ item.content }}
          </div>
        </div>
      </div>
      
      <div v-else class="empty-state">
        <div class="empty-icon">📭</div>
        <p>暂无公告</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Navbar from '@/components/Navbar.vue'
import axios from '@/api/axios'

const announcements = ref([])

const loadAnnouncements = async () => {
  try {
    const response = await axios.get('/announcements')
    if (response.success) {
      announcements.value = response.data || []
    }
  } catch (error) {
    console.error('Failed to load announcements:', error)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor(diff / (1000 * 60))
  
  if (days > 7) {
    return date.toLocaleDateString('zh-CN')
  } else if (days > 0) {
    return `${days}天前`
  } else if (hours > 0) {
    return `${hours}小时前`
  } else if (minutes > 0) {
    return `${minutes}分钟前`
  } else {
    return '刚刚'
  }
}

onMounted(() => {
  loadAnnouncements()
})
</script>

<style scoped>
.announcements-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding-bottom: 40px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-title {
  color: white;
  font-size: 2.5rem;
  margin-bottom: 10px;
  text-align: center;
}

.page-subtitle {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.1rem;
  text-align: center;
  margin-bottom: 40px;
}

.announcements-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.announcement-card {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  position: relative;
  transition: all 0.3s;
}

.announcement-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.announcement-card.pinned {
  border: 2px solid #667eea;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf3 100%);
}

.pinned-badge {
  position: absolute;
  top: 20px;
  right: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.card-header h2 {
  color: #333;
  font-size: 1.5rem;
  margin: 0;
  flex: 1;
  padding-right: 100px;
}

.date {
  color: #999;
  font-size: 0.9rem;
  white-space: nowrap;
}

.card-content {
  color: #555;
  line-height: 1.8;
  font-size: 1.05rem;
}

.empty-state {
  background: white;
  border-radius: 16px;
  padding: 60px;
  text-align: center;
  color: #999;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.empty-state p {
  font-size: 1.1rem;
  margin: 0;
}
</style>