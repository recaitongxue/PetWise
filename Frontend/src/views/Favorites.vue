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
        <router-link to="/breeds" class="action-link">浏览品种百科</router-link>
        <router-link to="/recognize" class="action-link secondary">去识别宠物品种</router-link>
      </div>

      <!-- 快速添加收藏 -->
      <div class="add-section">
        <h3>快速添加收藏</h3>
        <div class="add-form">
          <el-select
            v-model="selectedBreed"
            filterable
            placeholder="选择要收藏的品种"
            class="breed-select"
          >
            <el-option
              v-for="breed in availableBreeds"
              :key="breed"
              :label="breed"
              :value="breed"
            />
          </el-select>
          <el-button type="primary" @click="addFavorite" :disabled="!selectedBreed">
            添加收藏
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import Navbar from '@/components/Navbar.vue'
import { favoritesAPI } from '@/api/favorites'
import { breedAPI } from '@/api/breed'

const router = useRouter()
const favorites = ref([])
const allBreeds = ref([])
const selectedBreed = ref('')

const availableBreeds = computed(() => {
  const favorited = new Set(favorites.value.map(f => f.breed))
  return allBreeds.value.filter(b => !favorited.has(b))
})

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

const loadAllBreeds = async () => {
  try {
    const response = await breedAPI.getAllBreeds()
    if (response.success) {
      allBreeds.value = [
        ...(response.categories?.dog || []),
        ...(response.categories?.cat || [])
      ]
    }
  } catch (error) {
    console.log('Failed to load breeds:', error)
  }
}

const addFavorite = async (breed) => {
  const targetBreed = breed || selectedBreed.value
  if (!targetBreed) return

  try {
    const response = await favoritesAPI.addFavorite({ breed: targetBreed })
    if (response.success) {
      ElMessage.success('收藏成功')
      selectedBreed.value = ''
      await loadFavorites()
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '收藏失败')
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
  router.push(`/breed/${encodeURIComponent(breed)}`)
}

onMounted(() => {
  loadFavorites()
  loadAllBreeds()
})
</script>

<style scoped>
.favorites-page {
  min-height: 100vh;
  background: var(--color-bg);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-title {
  font-size: 28px;
  margin-bottom: 30px;
}

.favorites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.favorite-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: var(--shadow-card);
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
  background: var(--gradient-hero);
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
  box-shadow: var(--shadow-card);
  margin-bottom: 30px;
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
  background: var(--gradient-hero);
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-size: 14px;
  margin: 0 8px;
}

.action-link.secondary {
  background: white;
  color: var(--color-primary);
  border: 1px solid var(--color-primary);
}

.add-section {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: var(--shadow-card);
}

.add-section h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
}

.add-form {
  display: flex;
  gap: 12px;
  align-items: center;
}

.breed-select {
  flex: 1;
}
</style>
