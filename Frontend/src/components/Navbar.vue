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
        <template v-if="isLoggedIn">
          <a href="/recognize" class="nav-link">宠物识别</a>
          <a href="/agent" class="nav-link">AI助手</a>
          <a href="/pets" class="nav-link">我的宠物</a>
          <a href="/health" class="nav-link">健康记录</a>
          <a href="/schedule" class="nav-link">日程提醒</a>
          <a href="/favorites" class="nav-link">我的收藏</a>
          <a href="/announcements" class="nav-link">系统公告</a>
          <a href="/feedback" class="nav-link">意见反馈</a>
        </template>
        <template v-else>
          <a href="/recognize" class="nav-link">宠物识别</a>
          <a href="/agent" class="nav-link">AI助手</a>
          <a href="/breeds" class="nav-link">品种百科</a>
        </template>
      </div>
      
      <div class="navbar-right">
        <template v-if="isLoggedIn">
          <template v-if="currentUser?.role === 'admin'">
            <a href="/admin" class="nav-link admin-link">管理后台</a>
          </template>
          <div class="user-dropdown">
            <button class="user-btn">
              <span class="avatar">👤</span>
              <span class="username">{{ currentUser?.username }}</span>
              <span class="arrow">▼</span>
            </button>
            <div class="dropdown-menu">
              <a href="/profile" class="dropdown-item">个人中心</a>
              <a href="/pets" class="dropdown-item">我的宠物</a>
              <a href="/favorites" class="dropdown-item">我的收藏</a>
              <div class="dropdown-divider"></div>
              <button class="dropdown-item logout" @click="handleLogout">退出登录</button>
            </div>
          </div>
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
import { ref, computed, onMounted } from 'vue'
import { authAPI } from '@/api/auth'
import { ElMessage } from 'element-plus'

const currentUser = ref(null)

const isLoggedIn = computed(() => {
  return !!localStorage.getItem('token') && currentUser.value !== null
})

onMounted(() => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      currentUser.value = JSON.parse(userStr)
    } catch (e) {
      console.error('Failed to parse user from localStorage:', e)
    }
  }
})

const handleLogout = async () => {
  try {
    await authAPI.logout()
  } catch (error) {
    console.log('Logout error:', error)
  } finally {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    currentUser.value = null
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

.user-dropdown {
  position: relative;
}

.user-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f5f7fa;
  border: none;
  padding: 8px 12px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
  transition: all 0.2s;
}

.user-btn:hover {
  background: #e8eaf0;
}

.arrow {
  font-size: 10px;
  color: #999;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  min-width: 160px;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px);
  transition: all 0.2s;
  z-index: 1000;
}

.user-dropdown:hover .dropdown-menu {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.dropdown-item {
  display: block;
  padding: 10px 15px;
  color: #333;
  text-decoration: none;
  font-size: 14px;
  transition: background 0.2s;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
}

.dropdown-item:hover {
  background: #f5f7fa;
}

.dropdown-divider {
  height: 1px;
  background: #eee;
  margin: 5px 0;
}

.dropdown-item.logout {
  color: #f56c6c;
}

.dropdown-item.logout:hover {
  background: #fef0f0;
}

.register-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white !important;
  padding: 8px 16px;
  border-radius: 20px;
}

.register-btn:hover {
  opacity: 0.9;
}
</style>