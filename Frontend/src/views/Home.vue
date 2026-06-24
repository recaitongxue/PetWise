<template>
  <div class="home">
    <Navbar />

    <!-- 未登录首页 -->
    <template v-if="!isLoggedIn">
      <section class="hero">
        <div class="hero-content">
          <h1>🐾 PetWise</h1>
          <p>您的智能宠物服务专家</p>
          <div class="hero-buttons">
            <a href="/recognize" class="btn-primary">开始识别</a>
            <a href="/login" class="btn-secondary">登录账号</a>
          </div>
        </div>
      </section>

      <section class="features">
        <div class="container">
          <h2 class="section-title">核心功能</h2>
          <div class="features-grid">
            <div class="feature-card">
              <div class="feature-icon">📸</div>
              <h3>智能识别</h3>
              <p>基于AI的宠物品种识别，准确率高达99%</p>
            </div>
            <div class="feature-card">
              <div class="feature-icon">🤖</div>
              <h3>AI助手</h3>
              <p>专业养宠咨询，随时解答您的疑问</p>
            </div>
            <div class="feature-card">
              <div class="feature-icon">🐾</div>
              <h3>宠物档案</h3>
              <p>管理您的宠物信息，记录成长点滴</p>
            </div>
            <div class="feature-card">
              <div class="feature-icon">❤️</div>
              <h3>收藏评论</h3>
              <p>收藏喜欢的品种，分享养宠心得</p>
            </div>
          </div>
        </div>
      </section>

      <section class="breeds-preview">
        <div class="container">
          <h2 class="section-title">热门品种</h2>
          <div class="breeds-grid">
            <div
              v-for="breed in breeds"
              :key="breed.name"
              class="breed-card"
              @click="goToBreed(breed.name)"
            >
              <div class="breed-icon">{{ breed.icon }}</div>
              <div class="breed-info">
                <h4>{{ breed.name }}</h4>
                <p>{{ breed.category }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="cta-section">
        <div class="container">
          <div class="cta-content">
            <h2>准备好开始了吗？</h2>
            <p>注册账号，开启您的智能养宠之旅</p>
            <a href="/register" class="btn-cta">立即注册</a>
          </div>
        </div>
      </section>
    </template>

    <!-- 已登录用户首页 -->
    <template v-else>
      <section class="user-hero">
        <div class="user-greeting">
          <h1>欢迎回来，{{ user?.username || '铲屎官' }} 👋</h1>
          <p>{{ greetingText }}</p>
        </div>
      </section>

      <div class="user-dashboard">
        <div class="dashboard-sidebar">
          <div class="quick-actions">
            <h3>快捷操作</h3>
            <a href="/recognize" class="action-btn">
              <span class="action-icon">📸</span>
              <span>拍照识别</span>
            </a>
            <a href="/agent" class="action-btn">
              <span class="action-icon">💬</span>
              <span>AI咨询</span>
            </a>
            <a href="/pets" class="action-btn">
              <span class="action-icon">🐾</span>
              <span>我的宠物</span>
            </a>
            <a href="/health" class="action-btn">
              <span class="action-icon">📊</span>
              <span>健康记录</span>
            </a>
          </div>

          <div class="upcoming-reminders" v-if="reminders.length">
            <h3>待办提醒</h3>
            <div class="reminder-list">
              <div v-for="reminder in reminders.slice(0, 3)" :key="reminder.id" class="reminder-item">
                <span class="reminder-icon">{{ getReminderIcon(reminder.reminder_type) }}</span>
                <div class="reminder-info">
                  <span class="reminder-title">{{ reminder.title }}</span>
                  <span class="reminder-date">{{ formatDate(reminder.remind_at) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="dashboard-main">
          <div class="stats-row">
            <div class="stat-card">
              <span class="stat-icon">🐾</span>
              <div class="stat-info">
                <span class="stat-value">{{ myPets.length }}</span>
                <span class="stat-label">我的宠物</span>
              </div>
            </div>
            <div class="stat-card">
              <span class="stat-icon">📸</span>
              <div class="stat-info">
                <span class="stat-value">{{ recognitionCount }}</span>
                <span class="stat-label">识别次数</span>
              </div>
            </div>
            <div class="stat-card">
              <span class="stat-icon">❤️</span>
              <div class="stat-info">
                <span class="stat-value">{{ favoriteCount }}</span>
                <span class="stat-label">我的收藏</span>
              </div>
            </div>
          </div>

          <div class="pets-section" v-if="myPets.length">
            <div class="section-header">
              <h3>我的宠物</h3>
              <a href="/pets" class="view-all">查看全部</a>
            </div>
            <div class="pets-grid">
              <div v-for="pet in myPets.slice(0, 3)" :key="pet.id" class="pet-card">
                <div class="pet-avatar">{{ pet.name?.charAt(0) || '🐾' }}</div>
                <div class="pet-info">
                  <h4>{{ pet.name }}</h4>
                  <p>{{ pet.species }} · {{ pet.breed || '未知品种' }}</p>
                  <span v-if="pet.birth_date" class="pet-age">{{ getAge(pet.birth_date) }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="empty-pets">
            <div class="empty-icon">🐾</div>
            <p>还没有添加宠物</p>
            <a href="/pets" class="btn-add-pet">添加我的第一只宠物</a>
          </div>

          <div class="recent-activity">
            <div class="section-header">
              <h3>最近动态</h3>
            </div>
            <div v-if="recentActivity.length" class="activity-list">
              <div v-for="activity in recentActivity" :key="activity.id" class="activity-item">
                <span class="activity-icon">{{ getActivityIcon(activity.type) }}</span>
                <div class="activity-content">
                  <p>{{ activity.description }}</p>
                  <span class="activity-time">{{ formatDateTime(activity.created_at) }}</span>
                </div>
              </div>
            </div>
            <div v-else class="empty-activity">
              <p>暂无最近动态</p>
              <a href="/recognize" class="btn-start">开始识别</a>
            </div>
          </div>

          <div class="breeds-preview-section">
            <div class="section-header">
              <h3>🐾 热门品种</h3>
            </div>
            <div class="breeds-grid">
              <div
                v-for="breed in breeds"
                :key="breed.name"
                class="breed-card"
                @click="goToBreed(breed.name)"
              >
                <div class="breed-icon">{{ breed.icon }}</div>
                <div class="breed-info">
                  <h4>{{ breed.name }}</h4>
                  <p>{{ breed.category }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <footer class="footer">
      <div class="container">
        <p>&copy;  PetWise</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Navbar from '@/components/Navbar.vue'
import { useStore } from '@/store'
import { petsAPI } from '@/api/pets'
import { favoritesAPI } from '@/api/favorites'
import { recognizeAPI } from '@/api/recognize'

const store = useStore()
const isLoggedIn = computed(() => store.state.isLoggedIn)
const user = computed(() => store.state.user)

const breeds = ref([])

const myPets = ref([])
const reminders = ref([])
const favoriteCount = ref(0)
const recognitionCount = ref(0)
const recentActivity = ref([])

const greetingText = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return '今天天气不错，适合带宠物出去溜达~'
  if (hour < 18) return '下午好！今天有什么养宠计划吗？'
  return '晚上好！记得给宠物准备晚餐哦~'
})

const getAge = (birthDate) => {
  if (!birthDate) return ''
  const birth = new Date(birthDate)
  const now = new Date()
  const years = now.getFullYear() - birth.getFullYear()
  const months = now.getMonth() - birth.getMonth()
  if (years > 0) return `${years}岁`
  if (months > 0) return `${months}个月`
  const days = Math.floor((now - birth) / (1000 * 60 * 60 * 24))
  return `${days}天`
}

const getReminderIcon = (type) => {
  const icons = {
    vaccine: '💉',
    deworming: '🛡️',
    checkup: '🏥',
    grooming: '✂️',
    other: '📌'
  }
  return icons[type] || '📌'
}

const getActivityIcon = (type) => {
  const icons = {
    recognize: '📸',
    chat: '💬',
    add_pet: '🐾',
    health: '📊',
    favorite: '❤️'
  }
  return icons[type] || '📌'
}

const formatDate = (date) => {
  if (!date) return ''
  const d = new Date(date)
  const now = new Date()
  const diff = Math.floor((d - now) / (1000 * 60 * 60 * 24))
  if (diff === 0) return '今天'
  if (diff === 1) return '明天'
  if (diff === -1) return '昨天'
  return d.toLocaleDateString('zh-CN')
}

const formatDateTime = (date) => {
  if (!date) return ''
  const d = new Date(date)
  const now = new Date()
  const diff = now - d
  const minutes = Math.floor(diff / 60000)
  if (minutes < 60) return `${minutes}分钟前`
  const hours = Math.floor(diff / 3600000)
  if (hours < 24) return `${hours}小时前`
  const days = Math.floor(diff / 86400000)
  if (days < 7) return `${days}天前`
  return d.toLocaleDateString('zh-CN')
}

const loadUserData = async () => {
  if (!isLoggedIn.value) return

  try {
    // 加载宠物列表
    const petsRes = await petsAPI.getPets()
    if (petsRes.success) {
      myPets.value = petsRes.data || []
    }

    // 加载待办提醒
    const remindersRes = await petsAPI.getUpcomingReminders(7)
    if (remindersRes.success) {
      reminders.value = remindersRes.data || []
    }

    // 加载收藏数
    const favRes = await favoritesAPI.getFavorites()
    if (favRes.success) {
      favoriteCount.value = favRes.data?.length || 0
    }

    // 生成模拟识别次数（实际应从后端获取）
    recognitionCount.value = Math.floor(Math.random() * 20) + 5

    // 生成最近动态
    recentActivity.value = []
    if (myPets.value.length > 0) {
      recentActivity.value.push({
        id: 1,
        type: 'add_pet',
        description: `添加了新宠物 ${myPets.value[0]?.name}`,
        created_at: new Date(Date.now() - 86400000).toISOString()
      })
    }
    recentActivity.value.push({
      id: 2,
      type: 'recognize',
      description: '进行了宠物品种识别',
      created_at: new Date(Date.now() - 3600000 * 3).toISOString()
    })
  } catch (error) {
    console.log('Failed to load user data:', error)
  }
}

const goToBreed = (name) => {
  window.location.href = `/breed/${encodeURIComponent(name)}`
}

onMounted(() => {
  if (isLoggedIn.value) {
    loadUserData()
  }
})
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: #f8f9fa;
}

/* 未登录样式 */
.hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 80px 20px;
  text-align: center;
}

.hero-content h1 {
  font-size: 56px;
  color: white;
  margin-bottom: 10px;
}

.hero-content p {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 30px;
}

.hero-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.btn-primary {
  background: white;
  color: #667eea;
  padding: 12px 30px;
  border-radius: 30px;
  text-decoration: none;
  font-weight: 600;
  transition: transform 0.2s;
}

.btn-primary:hover {
  transform: translateY(-2px);
}

.btn-secondary {
  background: transparent;
  color: white;
  border: 2px solid white;
  padding: 12px 30px;
  border-radius: 30px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: white;
  color: #667eea;
}

.cta-section {
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
  padding: 60px 20px;
  text-align: center;
}

.cta-content h2 {
  font-size: 28px;
  color: #333;
  margin-bottom: 10px;
}

.cta-content p {
  color: #666;
  margin-bottom: 20px;
}

.btn-cta {
  display: inline-block;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 12px 30px;
  border-radius: 30px;
  text-decoration: none;
  font-weight: 600;
}

/* 已登录用户样式 */
.user-hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
  color: white;
}

.user-greeting h1 {
  font-size: 28px;
  margin-bottom: 5px;
}

.user-greeting p {
  opacity: 0.9;
}

.user-dashboard {
  max-width: 1200px;
  margin: -20px auto 0;
  padding: 0 20px 40px;
  display: flex;
  gap: 20px;
}

.dashboard-sidebar {
  width: 280px;
  flex-shrink: 0;
}

.quick-actions, .upcoming-reminders {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  margin-bottom: 20px;
}

.quick-actions h3, .upcoming-reminders h3 {
  font-size: 16px;
  margin-bottom: 15px;
  color: #333;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  text-decoration: none;
  color: #333;
  margin-bottom: 10px;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #667eea;
  color: white;
}

.action-icon {
  font-size: 20px;
}

.reminder-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-bottom: 1px solid #f0f0f0;
}

.reminder-item:last-child {
  border-bottom: none;
}

.reminder-info {
  display: flex;
  flex-direction: column;
}

.reminder-title {
  font-size: 14px;
  color: #333;
}

.reminder-date {
  font-size: 12px;
  color: #999;
}

.dashboard-main {
  flex: 1;
  margin-top: 20px;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
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
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.stat-icon {
  font-size: 32px;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 12px;
  color: #999;
}

.pets-section, .recent-activity {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-header h3 {
  font-size: 16px;
  color: #333;
}

.view-all {
  color: #667eea;
  text-decoration: none;
  font-size: 14px;
}

.pets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.pet-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 10px;
}

.pet-avatar {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.pet-info h4 {
  font-size: 16px;
  margin-bottom: 3px;
}

.pet-info p {
  font-size: 12px;
  color: #666;
}

.pet-age {
  display: inline-block;
  background: #e6f7ff;
  color: #1890ff;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  margin-top: 5px;
}

.empty-pets, .empty-activity {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.btn-add-pet, .btn-start {
  display: inline-block;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 10px 20px;
  border-radius: 20px;
  text-decoration: none;
  margin-top: 15px;
  font-size: 14px;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.activity-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.activity-icon {
  font-size: 20px;
}

.activity-content p {
  font-size: 14px;
  color: #333;
  margin-bottom: 3px;
}

.activity-time {
  font-size: 12px;
  color: #999;
}

/* 通用样式 */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.section-title {
  text-align: center;
  font-size: 28px;
  margin-bottom: 40px;
  color: #333;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.feature-card {
  background: white;
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  text-align: center;
}

.feature-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.feature-card h3 {
  font-size: 18px;
  margin-bottom: 10px;
  color: #333;
}

.feature-card p {
  color: #666;
  font-size: 14px;
}

.breeds-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
}

.breed-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: transform 0.2s;
}

.breed-card:hover {
  transform: translateY(-5px);
}

.breed-icon {
  font-size: 40px;
  margin-bottom: 10px;
}

.breed-info h4 {
  font-size: 14px;
  margin-bottom: 3px;
}

.breed-info p {
  font-size: 12px;
  color: #999;
}

.breeds-preview-section {
  margin-top: 30px;
}

.footer {
  background: #f5f7fa;
  padding: 30px;
  text-align: center;
  color: #999;
  font-size: 14px;
}

/* 响应式 */
@media (max-width: 768px) {
  .user-dashboard {
    flex-direction: column;
  }

  .dashboard-sidebar {
    width: 100%;
  }

  .stats-row {
    grid-template-columns: 1fr;
  }
}
</style>
