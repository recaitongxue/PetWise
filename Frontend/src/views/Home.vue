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
            <router-link to="/recognize" class="btn-primary">开始识别</router-link>
            <router-link to="/login" class="btn-secondary">登录账号</router-link>
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
            <router-link to="/register" class="btn-cta">立即注册</router-link>
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
            <router-link to="/recognize" class="action-btn">
              <span class="action-icon">📸</span>
              <span>拍照识别</span>
            </router-link>
            <router-link to="/agent" class="action-btn">
              <span class="action-icon">💬</span>
              <span>AI咨询</span>
            </router-link>
            <router-link to="/pets" class="action-btn">
              <span class="action-icon">🐾</span>
              <span>我的宠物</span>
            </router-link>
            <router-link to="/health" class="action-btn">
              <span class="action-icon">📊</span>
              <span>健康记录</span>
            </router-link>
          </div>

          <div class="upcoming-reminders" v-if="reminders.length">
            <h3>待办提醒</h3>
            <div class="reminder-list">
              <div v-for="reminder in reminders.slice(0, 3)" :key="reminder.id" class="reminder-item">
                <span class="reminder-icon">{{ getReminderIcon(reminder.reminder_type) }}</span>
                <div class="reminder-info">
                  <span class="reminder-title">{{ reminder.title }}</span>
                  <span class="reminder-date">{{ formatDate(reminder.scheduled_date || reminder.remind_at) }}</span>
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
              <router-link to="/pets" class="view-all">查看全部</router-link>
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
            <router-link to="/pets" class="btn-add-pet">添加我的第一只宠物</router-link>
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
              <router-link to="/recognize" class="btn-start">开始识别</router-link>
            </div>
          </div>
        </div>
      </div>
    </template>

    <footer class="footer">
      <div class="container">
        <p>&copy; 2026 PetWise. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '@/components/Navbar.vue'
import { useStore } from '@/store'
import { authAPI } from '@/api/auth'
import { petsAPI } from '@/api/pets'
import { recognizeAPI } from '@/api/recognize'
import { breedAPI } from '@/api/breed'

const router = useRouter()
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
    vaccination: '💉',
    vaccine: '💉',
    deworming: '🛡️',
    checkup: '🏥',
    senior_checkup: '🏥',
    medication: '💊',
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
    const profileRes = await authAPI.getProfile()
    if (profileRes.success) {
      recognitionCount.value = profileRes.stats?.recognitions_count || 0
      favoriteCount.value = profileRes.stats?.favorites_count || 0
    }

    const petsRes = await petsAPI.getPets()
    if (petsRes.success) {
      myPets.value = petsRes.data || []
    }

    const remindersRes = await petsAPI.getUpcomingReminders(7)
    if (remindersRes.success) {
      reminders.value = remindersRes.data || []
    }

    const historyRes = await recognizeAPI.getHistory({ page: 1, per_page: 5 })
    if (historyRes.success) {
      recentActivity.value = (historyRes.data || []).map(item => ({
        id: item.id,
        type: 'recognize',
        description: `识别了 ${item.breed || '未知品种'}`,
        created_at: item.created_at
      }))
    }
  } catch (error) {
    console.log('Failed to load user data:', error)
  }
}

const loadBreeds = async () => {
  try {
    const response = await breedAPI.getPopularBreeds()
    if (response.success && response.breeds?.length) {
      breeds.value = response.breeds.slice(0, 6).map(b => ({
        name: b.breed,
        category: b.category === 'cat' ? '猫' : '狗',
        icon: b.category === 'cat' ? '🐱' : '🐶'
      }))
    } else {
      const classesRes = await breedAPI.getAllBreeds()
      if (classesRes.success) {
        const list = []
        ;(classesRes.categories?.dog || []).slice(0, 3).forEach(name => {
          list.push({ name, category: '狗', icon: '🐶' })
        })
        ;(classesRes.categories?.cat || []).slice(0, 3).forEach(name => {
          list.push({ name, category: '猫', icon: '🐱' })
        })
        breeds.value = list
      }
    }
  } catch (error) {
    console.log('Failed to load breeds:', error)
  }
}

const goToBreed = (name) => {
  router.push(`/breed/${encodeURIComponent(name)}`)
}

onMounted(() => {
  loadBreeds()
  if (isLoggedIn.value) {
    loadUserData()
  }
})
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: var(--color-bg);
}

/* 未登录样式 */
.hero {
  background: var(--gradient-hero);
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
  color: var(--color-primary-dark);
  padding: 12px 30px;
  border-radius: var(--radius-pill);
  text-decoration: none;
  font-weight: 600;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: var(--shadow-sm);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.btn-secondary {
  background: transparent;
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.85);
  padding: 12px 30px;
  border-radius: var(--radius-pill);
  text-decoration: none;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: white;
  color: var(--color-accent);
  border-color: white;
}

.cta-section {
  background: var(--gradient-soft);
  padding: 60px 20px;
  text-align: center;
}

.cta-content h2 {
  font-size: 28px;
  color: var(--color-text);
  margin-bottom: 10px;
}

.cta-content p {
  color: var(--color-text-secondary);
  margin-bottom: 20px;
}

.btn-cta {
  display: inline-block;
  background: var(--gradient-accent);
  color: white;
  padding: 12px 32px;
  border-radius: var(--radius-pill);
  text-decoration: none;
  font-weight: 600;
  box-shadow: var(--shadow-orange);
  transition: transform 0.2s;
}

.btn-cta:hover {
  transform: translateY(-2px);
}

/* 已登录用户样式 */
.user-hero {
  background: var(--gradient-hero);
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
  background: var(--color-bg-card);
  border-radius: var(--radius-md);
  padding: 20px;
  box-shadow: var(--shadow-card);
  border: 1px solid var(--color-border-light);
  margin-bottom: 20px;
}

.quick-actions h3, .upcoming-reminders h3 {
  font-size: 16px;
  margin-bottom: 15px;
  color: var(--color-text);
  border-left: 3px solid var(--color-accent);
  padding-left: 10px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--color-primary-bg);
  border-radius: var(--radius-sm);
  text-decoration: none;
  color: var(--color-text);
  margin-bottom: 10px;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.action-btn:hover {
  background: var(--gradient-primary);
  color: white;
  border-color: var(--color-primary-light);
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
  background: var(--color-bg-card);
  border-radius: var(--radius-md);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: var(--shadow-card);
  border: 1px solid var(--color-border-light);
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: var(--color-primary-dark);
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
  box-shadow: var(--shadow-sm);
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
  color: var(--color-primary);
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
  background: var(--color-bg);
  border-radius: 10px;
}

.pet-avatar {
  width: 50px;
  height: 50px;
  background: var(--gradient-hero);
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
  background: var(--color-primary-bg);
  color: var(--color-primary-dark);
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
  background: var(--gradient-accent);
  color: white;
  padding: 10px 20px;
  border-radius: var(--radius-pill);
  text-decoration: none;
  margin-top: 15px;
  font-size: 14px;
  box-shadow: var(--shadow-orange);
  transition: transform 0.2s;
}

.btn-add-pet:hover, .btn-start:hover {
  transform: translateY(-2px);
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
  background: var(--color-bg);
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
  background: var(--color-bg-card);
  padding: 30px;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  text-align: center;
  border: 1px solid var(--color-border-light);
  transition: transform 0.2s, box-shadow 0.2s;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
  border-color: var(--color-primary-lighter);
}

.feature-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.feature-card h3 {
  font-size: 18px;
  margin-bottom: 10px;
  color: var(--color-text);
}

.feature-card p {
  color: var(--color-text-secondary);
  font-size: 14px;
}

.breeds-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
}

.breed-card {
  background: var(--color-bg-card);
  padding: 20px;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: transform 0.2s, border-color 0.2s;
  border: 1px solid var(--color-border-light);
}

.breed-card:hover {
  transform: translateY(-5px);
  border-color: var(--color-accent-light);
  box-shadow: var(--shadow-orange);
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

.footer {
  background: var(--color-bg);
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
