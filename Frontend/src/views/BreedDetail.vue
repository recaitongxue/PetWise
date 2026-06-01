<template>
  <div class="breed-detail-page">
    <Navbar />
    
    <div class="container">
      <div v-if="breedInfo" class="breed-content">
        <div class="breed-header">
          <div class="breed-icon">{{ breedInfo.category === 'cat' ? '🐱' : '🐶' }}</div>
          <div class="breed-title">
            <h1>{{ breedInfo.breed }}</h1>
            <p>{{ breedInfo.category === 'cat' ? '猫' : '狗' }} · {{ breedInfo.origin }}</p>
          </div>
          <div class="header-actions">
            <button 
              class="favorite-btn" 
              :class="{ favorited: isFavorited }"
              @click="toggleFavorite"
            >
              {{ isFavorited ? '❤️ 已收藏' : '🤍 收藏' }}
            </button>
          </div>
        </div>
        
        <div class="info-grid">
          <div class="info-card">
            <span class="info-label">性格特点</span>
            <span class="info-value">{{ breedInfo.personality }}</span>
          </div>
          <div class="info-card">
            <span class="info-label">寿命</span>
            <span class="info-value">{{ breedInfo.lifespan }}</span>
          </div>
          <div class="info-card">
            <span class="info-label">饲养建议</span>
            <span class="info-value">{{ breedInfo.feeding }}</span>
          </div>
          <div class="info-card">
            <span class="info-label">护理要点</span>
            <span class="info-value">{{ breedInfo.care }}</span>
          </div>
          <div class="info-card">
            <span class="info-label">常见问题</span>
            <span class="info-value">{{ breedInfo.common_issues }}</span>
          </div>
          <div class="info-card">
            <span class="info-label">适合人群</span>
            <span class="info-value">{{ breedInfo.suitable_for }}</span>
          </div>
        </div>
        
        <div class="stats-row">
          <div class="stat-item">
            <span class="stat-value">{{ breedInfo.views }}</span>
            <span class="stat-label">浏览次数</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ breedInfo.likes }}</span>
            <span class="stat-label">点赞数</span>
          </div>
        </div>
        
        <div class="comments-section">
          <h3>用户评论</h3>
          
          <div class="comment-form">
            <textarea 
              v-model="commentContent" 
              placeholder="写下您的评价..."
              rows="3"
            ></textarea>
            <div class="form-footer">
              <div class="rating">
                <span>评分：</span>
                <span 
                  v-for="star in 5" 
                  :key="star" 
                  class="star"
                  :class="{ active: star <= rating }"
                  @click="rating = star"
                >★</span>
              </div>
              <button @click="submitComment">发表评论</button>
            </div>
          </div>
          
          <div v-if="comments.length" class="comments-list">
            <div 
              v-for="comment in comments" 
              :key="comment.id" 
              class="comment-item"
            >
              <div class="comment-header">
                <span class="comment-author">{{ comment.username }}</span>
                <span class="comment-rating">
                  <span v-for="star in 5" :key="star">
                    {{ star <= comment.rating ? '★' : '☆' }}
                  </span>
                </span>
                <span class="comment-time">{{ comment.created_at }}</span>
              </div>
              <p class="comment-content">{{ comment.content }}</p>
              <div class="comment-actions">
                <button @click="likeComment(comment.id)">
                  👍 {{ comment.likes }}
                </button>
              </div>
            </div>
          </div>
          
          <div v-else class="empty-comments">
            <p>暂无评论，来发表第一条评论吧！</p>
          </div>
        </div>
      </div>
      
      <div v-else class="loading-state">
        <p>加载中...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import Navbar from '@/components/Navbar.vue'
import { otherAPI } from '@/api/other'
import { favoritesAPI } from '@/api/favorites'
import { commentsAPI } from '@/api/comments'

const breedInfo = ref(null)
const isFavorited = ref(false)
const comments = ref([])
const commentContent = ref('')
const rating = ref(5)

const breedName = window.location.pathname.split('/').pop()

const loadBreedInfo = async () => {
  try {
    const response = await otherAPI.getBreedInfo(decodeURIComponent(breedName))
    if (response.success) {
      breedInfo.value = response.data
    }
  } catch (error) {
    console.log('Failed to load breed info:', error)
  }
}

const loadComments = async () => {
  try {
    const response = await commentsAPI.getComments(decodeURIComponent(breedName))
    if (response.success) {
      comments.value = response.data || []
    }
  } catch (error) {
    console.log('Failed to load comments:', error)
  }
}

const checkFavorite = async () => {
  try {
    const response = await favoritesAPI.getFavorites()
    if (response.success) {
      const breeds = response.data || []
      isFavorited.value = breeds.some(f => f.breed === decodeURIComponent(breedName))
    }
  } catch (error) {
    console.log('Failed to check favorites:', error)
  }
}

const toggleFavorite = async () => {
  try {
    if (isFavorited.value) {
      await favoritesAPI.deleteFavorite(decodeURIComponent(breedName))
      isFavorited.value = false
      ElMessage.success('已取消收藏')
    } else {
      await favoritesAPI.addFavorite({ breed: decodeURIComponent(breedName) })
      isFavorited.value = true
      ElMessage.success('收藏成功')
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const submitComment = async () => {
  if (!commentContent.value.trim()) {
    ElMessage.error('请输入评论内容')
    return
  }
  
  try {
    const response = await commentsAPI.addComment({
      breed: decodeURIComponent(breedName),
      content: commentContent.value,
      rating: rating.value
    })
    
    if (response.success) {
      ElMessage.success('评论成功')
      commentContent.value = ''
      rating.value = 5
      await loadComments()
    }
  } catch (error) {
    ElMessage.error('评论失败')
  }
}

const likeComment = async (id) => {
  try {
    const response = await commentsAPI.likeComment(id)
    if (response.success) {
      await loadComments()
    }
  } catch (error) {
    ElMessage.error('点赞失败')
  }
}

onMounted(() => {
  loadBreedInfo()
  loadComments()
  checkFavorite()
})
</script>

<style scoped>
.breed-detail-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 30px 20px;
}

.breed-header {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.breed-icon {
  font-size: 60px;
}

.breed-title h1 {
  margin: 0 0 5px 0;
  font-size: 28px;
}

.breed-title p {
  margin: 0;
  color: #666;
}

.header-actions {
  margin-left: auto;
}

.favorite-btn {
  padding: 10px 20px;
  background: #f5f7fa;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.favorite-btn.favorited {
  background: #fff2f0;
  color: #f56c6c;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.info-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.info-label {
  display: block;
  font-size: 12px;
  color: #999;
  margin-bottom: 8px;
}

.info-value {
  font-size: 14px;
  color: #333;
}

.stats-row {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
}

.stat-item {
  flex: 1;
  background: white;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 600;
  color: #667eea;
}

.stat-label {
  font-size: 12px;
  color: #999;
}

.comments-section {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.comments-section h3 {
  margin: 0 0 20px 0;
  font-size: 20px;
}

.comment-form textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  resize: none;
}

.form-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.rating {
  font-size: 20px;
}

.star {
  cursor: pointer;
  color: #ddd;
}

.star.active {
  color: #ffc107;
}

.form-footer button {
  padding: 8px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.comments-list {
  margin-top: 30px;
}

.comment-item {
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.comment-author {
  font-weight: 600;
}

.comment-rating {
  color: #ffc107;
  font-size: 14px;
}

.comment-time {
  margin-left: auto;
  font-size: 12px;
  color: #999;
}

.comment-content {
  margin: 0;
  color: #333;
  font-size: 14px;
}

.comment-actions {
  margin-top: 10px;
}

.comment-actions button {
  padding: 4px 10px;
  background: #f5f7fa;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.empty-comments {
  text-align: center;
  padding: 30px;
  color: #999;
}

.loading-state {
  text-align: center;
  padding: 60px;
  color: #999;
}
</style>