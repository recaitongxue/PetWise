<template>
  <div class="breed-detail-page">
    <Navbar />
    
    <div class="container">
      <div v-if="breedInfo" class="breed-content">
        <!-- 头部信息 -->
        <div class="breed-header">
          <div class="breed-icon">{{ breedInfo.category === 'cat' ? '🐱' : '🐶' }}</div>
          <div class="breed-title">
            <h1>{{ breedInfo.breed }}</h1>
            <p>{{ breedInfo.category === 'cat' ? '猫科动物' : '犬科动物' }} · {{ breedInfo.origin }}</p>
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
        
        <!-- 快速信息卡片 -->
        <div class="quick-info">
          <div class="quick-item">
            <span class="quick-icon">🐾</span>
            <span class="quick-label">动物类别</span>
            <span class="quick-value">{{ breedInfo.category === 'cat' ? '猫科 (Felidae)' : '犬科 (Canidae)' }}</span>
          </div>
          <div class="quick-item">
            <span class="quick-icon">🌍</span>
            <span class="quick-label">起源国家</span>
            <span class="quick-value">{{ breedInfo.origin }}</span>
          </div>
          <div class="quick-item">
            <span class="quick-icon">⏱️</span>
            <span class="quick-label">预期寿命</span>
            <span class="quick-value">{{ breedInfo.lifespan }}</span>
          </div>
          <div class="quick-item">
            <span class="quick-icon">🎯</span>
            <span class="quick-label">品种用途</span>
            <span class="quick-value">{{ breedInfo.category === 'cat' ? '伴侣宠物，捕鼠能手' : '伴侣犬、工作犬、护卫犬' }}</span>
          </div>
        </div>
        
        <!-- 详细信息网格 -->
        <div class="detail-section">
          <h2>🐕 品种详情</h2>
          <div class="detail-grid">
            <div class="detail-card">
              <div class="card-icon">💝</div>
              <div class="card-content">
                <h3>性格特点</h3>
                <p>{{ breedInfo.personality }}</p>
              </div>
            </div>
            <div class="detail-card">
              <div class="card-icon">🍽️</div>
              <div class="card-content">
                <h3>饮食建议</h3>
                <p>{{ breedInfo.feeding }}</p>
              </div>
            </div>
            <div class="detail-card">
              <div class="card-icon">🛁</div>
              <div class="card-content">
                <h3>护理要点</h3>
                <p>{{ breedInfo.care }}</p>
              </div>
            </div>
            <div class="detail-card">
              <div class="card-icon">🏠</div>
              <div class="card-content">
                <h3>适宜环境</h3>
                <p>{{ breedInfo.category === 'cat' ? '室内饲养，需要活动空间和攀爬设施，保持环境安静' : '室内外均可，需要充足运动空间，定期户外活动' }}</p>
              </div>
            </div>
            <div class="detail-card">
              <div class="card-icon">⚕️</div>
              <div class="card-content">
                <h3>常见健康问题</h3>
                <p>{{ breedInfo.common_issues }}</p>
              </div>
            </div>
            <div class="detail-card">
              <div class="card-icon">👨‍👩‍👧</div>
              <div class="card-content">
                <h3>适合人群</h3>
                <p>{{ breedInfo.suitable_for }}</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 统计数据 -->
        <div class="stats-row">
          <div class="stat-item">
            <span class="stat-icon">👁️</span>
            <span class="stat-value">{{ breedInfo.views }}</span>
            <span class="stat-label">浏览次数</span>
          </div>
          <div class="stat-item">
            <span class="stat-icon">❤️</span>
            <span class="stat-value">{{ breedInfo.likes }}</span>
            <span class="stat-label">点赞数</span>
          </div>
          <div class="stat-item">
            <span class="stat-icon">💬</span>
            <span class="stat-value">{{ comments.length }}</span>
            <span class="stat-label">用户评论</span>
          </div>
        </div>
        
        <!-- 饲养小贴士 -->
        <div class="tips-section">
          <h2>💡 饲养小贴士</h2>
          <div class="tips-content">
            <div class="tip-item">
              <span class="tip-num">01</span>
              <div class="tip-text">
                <h4>饮食管理</h4>
                <p>根据{{ breedInfo.breed }}的体型和活动量，合理安排饮食，定时定量喂食，避免过度喂养。</p>
              </div>
            </div>
            <div class="tip-item">
              <span class="tip-num">02</span>
              <div class="tip-text">
                <h4>健康检查</h4>
                <p>定期带{{ breedInfo.breed }}去宠物医院进行体检，及时接种疫苗，预防常见疾病。</p>
              </div>
            </div>
            <div class="tip-item">
              <span class="tip-num">03</span>
              <div class="tip-text">
                <h4>日常护理</h4>
                <p>定期为{{ breedInfo.breed }}梳理毛发、清洁耳朵、修剪指甲，保持良好的卫生习惯。</p>
              </div>
            </div>
            <div class="tip-item">
              <span class="tip-num">04</span>
              <div class="tip-text">
                <h4>互动陪伴</h4>
                <p>{{ breedInfo.breed }}是非常聪明的宠物，需要主人的关爱和陪伴，每天保持一定的互动时间。</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 用户评论 -->
        <div class="comments-section">
          <h3>💬 用户评论</h3>
          
          <div class="comment-form">
            <textarea 
              v-model="commentContent" 
              placeholder="写下您对{{ breedInfo.breed }}的评价和饲养心得..."
              rows="4"
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
                <span class="comment-avatar">👤</span>
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
            <p>暂无评论，来分享您的饲养经验吧！</p>
          </div>
        </div>
      </div>
      
      <div v-else class="loading-state">
        <div class="loading-spinner"></div>
        <p>正在加载品种信息...</p>
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
      breedInfo.value = response.breed
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
  background: linear-gradient(135deg, var(--color-bg) 0%, #e4e8f0 100%);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

/* 头部信息 */
.breed-header {
  background: var(--gradient-hero);
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 8px 32px rgba(41, 182, 246, 0.3);
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 24px;
}

.breed-icon {
  font-size: 72px;
  background: rgba(255, 255, 255, 0.2);
  padding: 16px;
  border-radius: 16px;
}

.breed-title h1 {
  margin: 0 0 8px 0;
  font-size: 32px;
  color: white;
}

.breed-title p {
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
  font-size: 16px;
}

.header-actions {
  margin-left: auto;
}

.favorite-btn {
  padding: 12px 24px;
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 30px;
  cursor: pointer;
  font-size: 15px;
  color: white;
  transition: all 0.3s ease;
}

.favorite-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.favorite-btn.favorited {
  background: rgba(255, 108, 108, 0.9);
  border-color: rgba(255, 108, 108, 0.9);
}

/* 快速信息卡片 */
.quick-info {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.quick-item {
  background: white;
  padding: 20px;
  border-radius: 16px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.06);
  text-align: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.quick-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.quick-icon {
  font-size: 28px;
  display: block;
  margin-bottom: 8px;
}

.quick-label {
  display: block;
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.quick-value {
  display: block;
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

/* 详细信息区域 */
.detail-section {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.06);
  margin-bottom: 24px;
}

.detail-section h2 {
  margin: 0 0 20px 0;
  font-size: 22px;
  color: #333;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.detail-card {
  background: linear-gradient(135deg, var(--color-bg) 0%, #f0f2f5 100%);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  gap: 16px;
  transition: transform 0.3s ease;
}

.detail-card:hover {
  transform: translateY(-4px);
}

.card-icon {
  font-size: 36px;
  flex-shrink: 0;
}

.card-content h3 {
  margin: 0 0 8px 0;
  font-size: 15px;
  color: #333;
}

.card-content p {
  margin: 0;
  font-size: 13px;
  color: #666;
  line-height: 1.6;
}

/* 统计数据 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-item {
  background: white;
  padding: 24px;
  border-radius: 16px;
  text-align: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.06);
}

.stat-icon {
  font-size: 24px;
  display: block;
  margin-bottom: 8px;
}

.stat-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: var(--color-primary);
}

.stat-label {
  font-size: 13px;
  color: #999;
}

/* 饲养小贴士 */
.tips-section {
  background: linear-gradient(135deg, #fef9c3 0%, #fde047 100%);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 24px;
}

.tips-section h2 {
  margin: 0 0 20px 0;
  font-size: 22px;
  color: #854d0e;
}

.tips-content {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.tip-item {
  display: flex;
  gap: 16px;
  background: rgba(255, 255, 255, 0.8);
  padding: 20px;
  border-radius: 12px;
}

.tip-num {
  font-size: 28px;
  font-weight: 700;
  color: #f59e0b;
  flex-shrink: 0;
}

.tip-text h4 {
  margin: 0 0 6px 0;
  font-size: 15px;
  color: #333;
}

.tip-text p {
  margin: 0;
  font-size: 13px;
  color: #666;
  line-height: 1.6;
}

/* 用户评论 */
.comments-section {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.06);
}

.comments-section h3 {
  margin: 0 0 20px 0;
  font-size: 20px;
  color: #333;
}

.comment-form textarea {
  width: 100%;
  padding: 16px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 14px;
  resize: none;
  transition: border-color 0.3s ease;
}

.comment-form textarea:focus {
  outline: none;
  border-color: var(--color-primary);
}

.form-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.rating {
  font-size: 24px;
}

.star {
  cursor: pointer;
  color: #ddd;
  transition: color 0.2s ease;
}

.star:hover,
.star.active {
  color: #ffc107;
}

.form-footer button {
  padding: 10px 28px;
  background: var(--gradient-hero);
  color: white;
  border: none;
  border-radius: 30px;
  cursor: pointer;
  font-size: 15px;
  transition: transform 0.2s ease;
}

.form-footer button:hover {
  transform: translateY(-2px);
}

.comments-list {
  margin-top: 24px;
}

.comment-item {
  padding: 20px;
  background: var(--color-bg);
  border-radius: 12px;
  margin-bottom: 12px;
}

.comment-item:last-child {
  margin-bottom: 0;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.comment-avatar {
  font-size: 24px;
}

.comment-author {
  font-weight: 600;
  color: #333;
}

.comment-rating {
  color: #ffc107;
  font-size: 16px;
}

.comment-time {
  margin-left: auto;
  font-size: 12px;
  color: #999;
}

.comment-content {
  margin: 0;
  color: #555;
  font-size: 14px;
  line-height: 1.6;
}

.comment-actions {
  margin-top: 12px;
}

.comment-actions button {
  padding: 6px 14px;
  background: #e5e7eb;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 13px;
  transition: background 0.2s ease;
}

.comment-actions button:hover {
  background: #d1d5db;
}

.empty-comments {
  text-align: center;
  padding: 40px;
  color: #999;
}

.empty-comments p {
  margin: 0;
}

/* 加载状态 */
.loading-state {
  text-align: center;
  padding: 80px;
  color: #999;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 900px) {
  .quick-info {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .detail-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .tips-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .quick-info {
    grid-template-columns: 1fr;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .breed-header {
    flex-direction: column;
    text-align: center;
  }
  
  .header-actions {
    margin-left: 0;
    margin-top: 16px;
  }
}
</style>