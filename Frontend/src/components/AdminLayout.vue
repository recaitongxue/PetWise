<template>
  <div class="admin-layout">
    <Navbar />
    
    <div class="admin-container">
      <aside class="sidebar">
        <div class="sidebar-header">
          <h2 class="sidebar-title">管理后台</h2>
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
import Navbar from '@/components/Navbar.vue'
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.admin-container {
  display: flex;
  flex: 1;
  gap: 20px;
  max-width: 1600px;
  width: 100%;
  margin: 0 auto;
  padding: 20px;
  box-sizing: border-box;
}

.sidebar {
  width: 220px;
  background: #2c3e50;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.main-content {
  flex: 1;
  min-width: 0;
}

@media (max-width: 768px) {
  .admin-container {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
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