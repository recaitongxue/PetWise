<template>
  <div class="home">
    <Navbar />
    
    <section class="hero">
      <div class="hero-content">
        <h1>🐾 PetWise</h1>
        <p>您的智能宠物服务专家</p>
        <div class="hero-buttons">
          <a href="/recognize" class="btn-primary">开始识别</a>
          <a href="/agent" class="btn-secondary">咨询AI</a>
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
    
    <section class="announcements">
      <div class="container">
        <h2 class="section-title">最新公告</h2>
        <div v-if="announcements.length" class="announcement-list">
          <div 
            v-for="ann in announcements" 
            :key="ann.id" 
            class="announcement-item"
          >
            <span v-if="ann.is_pinned" class="pin-badge">📌</span>
            <div class="ann-content">
              <h4>{{ ann.title }}</h4>
              <p>{{ ann.content }}</p>
            </div>
            <span class="ann-time">{{ ann.created_at }}</span>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>暂无公告</p>
        </div>
      </div>
    </section>
    
    <footer class="footer">
      <div class="container">
        <p>&copy; 2024 PetWise. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Navbar from '@/components/Navbar.vue'
import { adminAPI } from '@/api/admin'

const breeds = ref([
  { name: '英国短毛猫', category: '猫', icon: '🐱' },
  { name: '金毛寻回犬', category: '狗', icon: '🐶' },
  { name: '泰迪犬', category: '狗', icon: '🐩' },
  { name: '布偶猫', category: '猫', icon: '🐈' },
  { name: '哈士奇', category: '狗', icon: '🦮' },
  { name: '暹罗猫', category: '猫', icon: '🐱' }
])

const announcements = ref([])

onMounted(async () => {
  try {
    const response = await adminAPI.getAnnouncements()
    if (response.success) {
      announcements.value = response.data || []
    }
  } catch (error) {
    console.log('Failed to load announcements:', error)
  }
})

const goToBreed = (name) => {
  window.location.href = `/breed/${encodeURIComponent(name)}`
}
</script>

<style scoped>
.home {
  min-height: 100vh;
}

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

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 60px 20px;
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

.announcement-list {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.announcement-item {
  padding: 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.announcement-item:last-child {
  border-bottom: none;
}

.pin-badge {
  font-size: 16px;
}

.ann-content h4 {
  margin-bottom: 5px;
  color: #333;
}

.ann-content p {
  color: #666;
  font-size: 14px;
}

.ann-time {
  color: #999;
  font-size: 12px;
  margin-left: auto;
}

.empty-state {
  background: white;
  padding: 40px;
  border-radius: 12px;
  text-align: center;
  color: #999;
}

.footer {
  background: #f5f7fa;
  padding: 30px;
  text-align: center;
  color: #999;
  font-size: 14px;
}
</style>