<template>
  <div class="login-container">
    <div class="login-box">
      <div class="logo-section">
        <div class="logo">🐾</div>
        <h1>PetWise</h1>
        <p>智能宠物服务平台</p>
      </div>
      
      <el-form ref="loginForm" :model="form" label-width="80px" @submit.prevent="handleLogin">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" autocomplete="off" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" autocomplete="new-password" @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading" class="login-btn">
            登录
          </el-button>
        </el-form-item>
      </el-form>
      
      <p class="register-link">
        还没有账号？<router-link to="/register">立即注册</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authAPI } from '@/api/auth'
import { useStore } from '@/store'

const route = useRoute()
const router = useRouter()
const store = useStore()
const loginForm = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

onMounted(() => {
  store.logout()
})

const handleLogin = async () => {
  if (!form.username || !form.password) {
    ElMessage.error('请填写完整信息')
    return
  }
  
  loading.value = true
  
  try {
    const response = await authAPI.login(form)
    if (response.success) {
      store.login(response.token, response.user)
      ElMessage.success('登录成功')
      const redirect = route.query.redirect || '/'
      router.push(typeof redirect === 'string' ? redirect : '/')
    } else {
      ElMessage.error(response.message || '登录失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.error || error.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--gradient-hero);
  position: relative;
  overflow: hidden;
}

.login-container::before {
  content: '';
  position: absolute;
  width: 400px;
  height: 400px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 50%;
  top: -100px;
  right: -100px;
}

.login-container::after {
  content: '';
  position: absolute;
  width: 300px;
  height: 300px;
  background: rgba(255, 152, 0, 0.15);
  border-radius: 50%;
  bottom: -80px;
  left: -80px;
}

.login-box {
  background: var(--color-bg-card);
  padding: 40px;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  width: 100%;
  max-width: 400px;
  position: relative;
  z-index: 1;
  border: 1px solid var(--color-border-light);
}

.logo-section {
  text-align: center;
  margin-bottom: 30px;
}

.logo {
  font-size: 60px;
  margin-bottom: 10px;
}

h1 {
  font-size: 28px;
  color: var(--color-text);
  margin-bottom: 5px;
}

.logo-section p {
  color: var(--color-text-secondary);
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
}

.register-link {
  text-align: center;
  margin-top: 20px;
  color: var(--color-text-secondary);
}

.register-link a {
  color: var(--color-accent);
  text-decoration: none;
  font-weight: 600;
}

.register-link a:hover {
  color: var(--color-accent-dark);
  text-decoration: underline;
}
</style>
