<template>
  <div class="favorites-page">
    <Navbar />
    
    <div class="container">
      <h1 class="page-title">❤️ 我的收藏</h1>
      
      <div v-if="favorites.length" class="favorites-grid">
        <div 
          v-for="item in favorites" 
          :key="item.breed" 
          class="favorite-card"
        >
          <div class="breed-icon">{{ item.category === 'cat' ? '🐱' : '🐶' }}</div>
          <div class="breed-info">
            <h3>{{ item.breed }}</h3>
            <p>{{ item.origin }}</p>
            <p class="breed-desc">{{ item.personality }}</p>
          </div>
          <div class="card-actions">
            <button class="detail-btn" @click="goToDetail(item.breed)">查看详情</button>
            <button class="remove-btn" @click="removeFavorite(item.breed)">取消收藏</button>
          </div>
        </div>
      </div>
      
      <div v-else class="empty-state">
        <div class="empty-icon">💔</div>
        <p>还没有收藏任何品种</p>
        <a href="/recognize" class="action-link">去识别宠物品种</a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import Navbar from '@/components/Navbar.vue'
import { favoritesAPI } from '@/api/favorites'

const favorites = ref([])

const loadFavorites = async () => {
  try {
    const response = await favoritesAPI.getFavorites()
    if (response.success) {
      favorites.value = response.data || []
    }
  } catch (error) {
    console.log('Failed to load favorites:', error)
  }
}

const removeFavorite = async (breed) => {
  try {
    const response = await favoritesAPI.deleteFavorite(breed)
    if (response.success) {
      ElMessage.success('已取消收藏')
      await loadFavorites()
    }
  } catch (error) {
    ElMessage.error('取消失败')
  }
}

const goToDetail = (breed) => {
  window.location.href = `/breed/${encodeURIComponent(breed)}`
}

onMounted(() => {
  loadFavorites()
})
</script>

<style scoped>
.favorites-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 30px 20px;
}

.page-title {
  font-size: 28px;
  margin-bottom: 30px;
}

.favorites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.favorite-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.breed-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.breed-info h3 {
  margin: 0 0 5px 0;
  font-size: 18px;
}

.breed-info p {
  margin: 0 0 10px 0;
  color: #666;
  font-size: 14px;
}

.breed-desc {
  color: #999 !important;
  font-size: 12px !important;
}

.card-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.detail-btn {
  flex: 1;
  padding: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.remove-btn {
  padding: 8px 16px;
  background: #fff2f0;
  color: #f56c6c;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.empty-state {
  text-align: center;
  padding: 60px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.empty-icon {
  font-size: 60px;
  margin-bottom: 15px;
}

.empty-state p {
  color: #666;
  margin-bottom: 20px;
}

.action-link {
  display: inline-block;
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-size: 14px;
}
</style>