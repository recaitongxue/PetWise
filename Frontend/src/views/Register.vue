<template>
  <div class="register-container">
    <div class="register-box">
      <div class="logo-section">
        <div class="logo">🐾</div>
        <h1>PetWise</h1>
        <p>创建您的账号</p>
      </div>
      
      <el-form ref="registerForm" :model="form" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码（至少6位）" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" placeholder="请确认密码" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱（可选）" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleRegister" :loading="loading" class="register-btn">
            注册
          </el-button>
        </el-form-item>
      </el-form>
      
      <p class="login-link">
        已有账号？<a href="/login">立即登录</a>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { authAPI } from '@/api/auth'

const registerForm = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  email: ''
})

const handleRegister = async () => {
  if (!form.username || !form.password) {
    ElMessage.error('请填写用户名和密码')
    return
  }
  
  if (form.password.length < 6) {
    ElMessage.error('密码至少需要6位')
    return
  }
  
  if (form.password !== form.confirmPassword) {
    ElMessage.error('两次输入的密码不一致')
    return
  }
  
  loading.value = true
  
  try {
    const response = await authAPI.register({
      username: form.username,
      password: form.password,
      email: form.email
    })
    
    if (response.success) {
      ElMessage.success('注册成功，请登录')
      window.location.href = '/login'
    } else {
      ElMessage.error(response.message || '注册失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-box {
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 450px;
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
  color: #333;
  margin-bottom: 5px;
}

.logo-section p {
  color: #666;
}

.register-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
}

.login-link {
  text-align: center;
  margin-top: 20px;
  color: #666;
}

.login-link a {
  color: #666;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>