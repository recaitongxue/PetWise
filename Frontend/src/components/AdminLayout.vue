<template>
  <div class="admin-layout">
    <header class="admin-header">
      <div class="header-left">
        <h1 class="header-title">PetWise 管理后台</h1>
      </div>
      <div class="header-right">
        <router-link to="/" class="back-link">🏠 返回用户端</router-link>
        <span class="admin-info">{{ adminName }}</span>
        <button class="logout-btn" @click="handleLogout">退出</button>
      </div>
    </header>
    
    <div class="admin-container">
      <aside class="sidebar">
        <div class="sidebar-header">
          <h2 class="sidebar-title">功能导航</h2>
        </div>
        <nav class="sidebar-nav">
          <router-link to="/admin" class="nav-item" :class="{ active: $route.path === '/admin' }">📊 仪表盘</router-link>
          <router-link to="/admin/users" class="nav-item" :class="{ active: $route.path === '/admin/users' }">👥 用户管理</router-link>
          <router-link to="/admin/models" class="nav-item" :class="{ active: $route.path === '/admin/models' }">🤖 大模型管理</router-link>
          <router-link to="/admin/knowledge" class="nav-item" :class="{ active: $route.path === '/admin/knowledge' }">📚 知识库</router-link>
          <router-link to="/admin/samples" class="nav-item" :class="{ active: $route.path === '/admin/samples' }">🔍 难样本</router-link>
          <router-link to="/admin/stats" class="nav-item" :class="{ active: $route.path === '/admin/stats' }">📈 数据统计</router-link>
          <router-link to="/admin/logs" class="nav-item" :class="{ active: $route.path === '/admin/logs' }">📋 系统日志</router-link>
          <router-link to="/admin/rate-limits" class="nav-item" :class="{ active: $route.path === '/admin/rate-limits' }">⚡ 限流配置</router-link>
          <router-link to="/admin/sensitive-words" class="nav-item" :class="{ active: $route.path === '/admin/sensitive-words' }">🛡️ 敏感词</router-link>
          <router-link to="/admin/prompts" class="nav-item" :class="{ active: $route.path === '/admin/prompts' }">💭 Prompt模板</router-link>
          <router-link to="/admin/corrections" class="nav-item" :class="{ active: $route.path === '/admin/corrections' }">🔄 纠错记录</router-link>
          <router-link to="/admin/feedback" class="nav-item" :class="{ active: $route.path === '/admin/feedback' }">💬 用户反馈</router-link>
          <router-link to="/admin/announcements" class="nav-item" :class="{ active: $route.path === '/admin/announcements' }">📢 公告管理</router-link>
        </nav>
      </aside>
      
      <main class="main-content">
        <slot></slot>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const adminName = ref('管理员')

onMounted(() => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      const user = JSON.parse(userStr)
      adminName.value = user.username || '管理员'
    } catch (e) {
      adminName.value = '管理员'
    }
  }
})

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  background: var(--color-bg);
  display: flex;
  flex-direction: column;
}

.admin-header {
  background: var(--color-admin-header);
  padding: 15px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-title {
  font-size: 20px;
  font-weight: 600;
  color: white;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.back-link {
  color: #bdc3c7;
  text-decoration: none;
  padding: 8px 15px;
  border-radius: 6px;
  transition: all 0.25s ease;
  font-size: 14px;
}

.back-link:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.admin-info {
  color: #bdc3c7;
  font-size: 14px;
}

.logout-btn {
  background: rgba(255, 255, 255, 0.1);
  color: #bdc3c7;
  border: none;
  padding: 8px 15px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.25s ease;
  font-size: 14px;
}

.logout-btn:hover {
  background: var(--color-accent);
  color: white;
}

.admin-container {
  display: flex;
  flex: 1;
  gap: 20px;
  max-width: 1600px;
  width: 100%;
  margin: 0 auto;
  padding: 20px;
  padding-top: 70px;
  box-sizing: border-box;
}

.sidebar {
  width: 220px;
  background: var(--color-admin-sidebar);
  border-radius: var(--radius-md);
  padding: 20px;
  box-shadow: var(--shadow-md);
  flex-shrink: 0;
  position: fixed;
  top: 70px;
  left: 20px;
  bottom: 20px;
  overflow-y: auto;
}

.sidebar-header {
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 20px;
}

.sidebar-title {
  font-size: 16px;
  font-weight: 600;
  color: white;
  margin: 0;
  text-align: center;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.nav-item {
  padding: 12px 15px;
  text-decoration: none;
  color: #bdc3c7;
  border-radius: 8px;
  transition: all 0.25s ease;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-item.active {
  background: var(--gradient-accent);
  color: white;
  box-shadow: var(--shadow-orange);
}

.main-content {
  flex: 1;
  min-width: 0;
  margin-left: 240px;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .admin-container {
    flex-direction: column;
    padding-top: 70px;
  }
  
  .sidebar {
    position: relative;
    width: 100%;
    top: 0;
    left: 0;
    bottom: 0;
    margin-bottom: 20px;
  }
  
  .main-content {
    margin-left: 0;
  }
  
  .sidebar-nav {
    flex-direction: row;
    flex-wrap: wrap;
  }
  
  .nav-item {
    flex: 1;
    min-width: 120px;
    justify-content: center;
  }
}
</style>