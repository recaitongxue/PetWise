<template>
  <nav class="navbar">
    <div class="navbar-container">
      <div class="navbar-left">
        <router-link to="/" class="logo">
          <span class="logo-icon">🐾</span>
          <span class="logo-text">PetWise</span>
        </router-link>
        <button class="menu-toggle" @click="mobileMenuOpen = !mobileMenuOpen" aria-label="菜单">
          {{ mobileMenuOpen ? '✕' : '☰' }}
        </button>
      </div>

      <div class="navbar-center" :class="{ open: mobileMenuOpen }">
        <router-link to="/recognize" class="nav-link" @click="mobileMenuOpen = false">宠物识别</router-link>
        <router-link to="/batch-recognize" class="nav-link" @click="mobileMenuOpen = false" v-if="isLoggedIn">批量识别</router-link>
        <router-link to="/agent" class="nav-link" @click="mobileMenuOpen = false">AI助手</router-link>
        <router-link to="/breeds" class="nav-link" @click="mobileMenuOpen = false">品种百科</router-link>
        <template v-if="isLoggedIn">
          <router-link to="/pets" class="nav-link" @click="mobileMenuOpen = false">我的宠物</router-link>
          <router-link to="/health" class="nav-link" @click="mobileMenuOpen = false">健康记录</router-link>
          <router-link to="/schedule" class="nav-link" @click="mobileMenuOpen = false">日程提醒</router-link>
          <router-link to="/favorites" class="nav-link" @click="mobileMenuOpen = false">我的收藏</router-link>
          <router-link to="/announcements" class="nav-link" @click="mobileMenuOpen = false">系统公告</router-link>
          <router-link to="/feedback" class="nav-link" @click="mobileMenuOpen = false">意见反馈</router-link>
        </template>
      </div>

      <div class="navbar-right">
        <template v-if="isLoggedIn">
          <router-link v-if="currentUser?.role === 'admin'" to="/admin" class="nav-link admin-link">
            管理后台
          </router-link>
          <div class="user-dropdown">
            <button class="user-btn">
              <span class="avatar">👤</span>
              <span class="username">{{ currentUser?.username }}</span>
              <span class="arrow">▼</span>
            </button>
            <div class="dropdown-menu">
              <router-link to="/profile" class="dropdown-item" @click="mobileMenuOpen = false">个人中心</router-link>
              <router-link to="/pets" class="dropdown-item" @click="mobileMenuOpen = false">我的宠物</router-link>
              <router-link to="/favorites" class="dropdown-item" @click="mobileMenuOpen = false">我的收藏</router-link>
              <div class="dropdown-divider"></div>
              <button class="dropdown-item logout" @click="handleLogout">退出登录</button>
            </div>
          </div>
        </template>
        <template v-else>
          <router-link to="/login" class="nav-link">登录</router-link>
          <router-link to="/register" class="nav-link register-btn">注册</router-link>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '@/api/auth'
import { useStore } from '@/store'
import { ElMessage } from 'element-plus'

const router = useRouter()
const store = useStore()
const mobileMenuOpen = ref(false)

const isLoggedIn = computed(() => store.state.isLoggedIn)
const currentUser = computed(() => store.state.user)

const handleLogout = async () => {
  try {
    await authAPI.logout()
  } catch (error) {
    console.log('Logout error:', error)
  } finally {
    store.logout()
    mobileMenuOpen.value = false
    ElMessage.success('退出成功')
    router.push('/')
  }
}
</script>

<style scoped>
.navbar {
  background: var(--color-bg-card);
  box-shadow: var(--shadow-sm);
  border-bottom: 2px solid var(--color-border-light);
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
  height: 64px;
  position: relative;
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.navbar-left .logo {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: var(--color-text);
}

.logo-icon {
  font-size: 28px;
  margin-right: 8px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.menu-toggle {
  display: none;
  background: var(--color-primary-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 18px;
  cursor: pointer;
  color: var(--color-primary-dark);
  padding: 6px 10px;
}

.navbar-center {
  display: flex;
  gap: 22px;
  flex-wrap: wrap;
}

.nav-link {
  text-decoration: none;
  color: var(--color-text-secondary);
  font-size: 14px;
  font-weight: 500;
  transition: color 0.2s;
  white-space: nowrap;
  position: relative;
  padding: 4px 0;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background: var(--gradient-accent);
  border-radius: 1px;
  transition: width 0.25s ease;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: var(--color-primary-dark);
}

.nav-link:hover::after,
.nav-link.router-link-active::after {
  width: 100%;
}

.admin-link {
  color: var(--color-accent) !important;
  font-weight: 600;
}

.admin-link::after {
  background: var(--gradient-accent) !important;
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
  background: var(--color-primary-bg);
  border: 1px solid var(--color-border);
  padding: 8px 14px;
  border-radius: var(--radius-pill);
  cursor: pointer;
  font-size: 14px;
  color: var(--color-text);
  transition: all 0.2s;
}

.user-btn:hover {
  background: var(--color-primary-lighter);
  border-color: var(--color-primary-light);
}

.username {
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.arrow {
  font-size: 10px;
  color: var(--color-text-muted);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background: var(--color-bg-card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--color-border-light);
  min-width: 160px;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px);
  transition: all 0.2s;
  z-index: 1000;
  overflow: hidden;
}

.user-dropdown:hover .dropdown-menu {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.dropdown-item {
  display: block;
  padding: 10px 15px;
  color: var(--color-text);
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
  background: var(--color-primary-bg);
  color: var(--color-primary-dark);
}

.dropdown-divider {
  height: 1px;
  background: var(--color-border-light);
  margin: 5px 0;
}

.dropdown-item.logout {
  color: var(--color-danger);
}

.dropdown-item.logout:hover {
  background: var(--color-danger-bg);
}

.register-btn {
  background: var(--gradient-accent) !important;
  color: white !important;
  padding: 8px 18px;
  border-radius: var(--radius-pill);
  box-shadow: var(--shadow-orange);
}

.register-btn::after {
  display: none;
}

.register-btn:hover {
  opacity: 0.92;
  transform: translateY(-1px);
}

@media (max-width: 960px) {
  .menu-toggle {
    display: block;
  }

  .navbar-center {
    display: none;
    position: absolute;
    top: 64px;
    left: 0;
    right: 0;
    background: var(--color-bg-card);
    flex-direction: column;
    padding: 16px 20px;
    gap: 0;
    box-shadow: var(--shadow-md);
    border-top: 2px solid var(--color-border-light);
  }

  .navbar-center.open {
    display: flex;
  }

  .navbar-center .nav-link {
    padding: 12px 0;
    border-bottom: 1px solid var(--color-border-light);
  }

  .username {
    display: none;
  }
}
</style>
