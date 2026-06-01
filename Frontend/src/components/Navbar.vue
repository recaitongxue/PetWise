<template>
  <nav class="navbar">
    <div class="navbar-container">
      <div class="navbar-left">
        <a href="/" class="logo">
          <span class="logo-icon">🐾</span>
          <span class="logo-text">PetWise</span>
        </a>
      </div>
      
      <div class="navbar-center">
        <a href="/recognize" class="nav-link">宠物识别</a>
        <a href="/agent" class="nav-link">AI助手</a>
        <a href="/pets" class="nav-link">我的宠物</a>
        <a href="/favorites" class="nav-link">我的收藏</a>
      </div>
      
      <div class="navbar-right">
        <template v-if="store.state.isLoggedIn">
          <template v-if="store.state.user?.role === 'admin'">
            <a href="/admin" class="nav-link admin-link">管理后台</a>
          </template>
          <a href="/profile" class="nav-link">
            <span class="avatar">👤</span>
            <span>{{ store.state.user?.username }}</span>
          </a>
          <button class="logout-btn" @click="handleLogout">退出</button>
        </template>
        <template v-else>
          <a href="/login" class="nav-link">登录</a>
          <a href="/register" class="nav-link register-btn">注册</a>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useStore } from '@/store'
import { authAPI } from '@/api/auth'
import { ElMessage } from 'element-plus'

const store = useStore()

const handleLogout = async () => {
  try {
    await authAPI.logout()
  } catch (error) {
    console.log('Logout error:', error)
  } finally {
    store.logout()
    ElMessage.success('退出成功')
    window.location.href = '/'
  }
}
</script>

<style scoped>
.navbar {
  background: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
}

.navbar-left .logo {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: #333;
}

.logo-icon {
  font-size: 28px;
  margin-right: 8px;
}

.logo-text {
  font-size: 20px;
  font-weight: 600;
}

.navbar-center {
  display: flex;
  gap: 30px;
}

.nav-link {
  text-decoration: none;
  color: #666;
  font-size: 14px;
  transition: color 0.2s;
  display: flex;
  align-items: center;
  gap: 5px;
}

.nav-link:hover {
  color: #667eea;
}

.admin-link {
  color: #f56c6c;
}

.admin-link:hover {
  color: #f56c6c;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.avatar {
  font-size: 20px;
}

.logout-btn {
  background: #f5f7fa;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  color: #666;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.logout-btn:hover {
  background: #eee;
}

.register-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white !important;
  padding: 8px 16px;
  border-radius: 8px;
}

.register-btn:hover {
  opacity: 0.9;
}
</style>