<template>
  <div class="profile-page">
    <Navbar />
    
    <div class="container">
      <div v-if="profile" class="profile-content">
        <div class="profile-header">
          <div class="avatar-section">
            <div class="avatar">👤</div>
            <h2>{{ profile.user.username }}</h2>
            <p>{{ profile.user.role === 'admin' ? '管理员' : '普通用户' }}</p>
          </div>
          
          <div class="stats-section">
            <div class="stat-item">
              <span class="stat-value">{{ profile.stats.pets_count }}</span>
              <span class="stat-label">我的宠物</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ profile.stats.recognitions_count }}</span>
              <span class="stat-label">识别次数</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ profile.stats.favorites_count }}</span>
              <span class="stat-label">收藏数</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ profile.stats.comments_count }}</span>
              <span class="stat-label">评论数</span>
            </div>
          </div>
        </div>
        
        <div class="info-section">
          <h3>个人信息</h3>
          
          <div class="info-item">
            <span class="label">用户名</span>
            <span class="value">{{ profile.user.username }}</span>
          </div>
          <div class="info-item">
            <span class="label">邮箱</span>
            <span class="value">{{ profile.user.email || '未设置' }}</span>
          </div>
          <div class="info-item">
            <span class="label">简介</span>
            <span class="value">{{ profile.user.bio || '未设置' }}</span>
          </div>
          <div class="info-item">
            <span class="label">注册时间</span>
            <span class="value">{{ profile.user.created_at }}</span>
          </div>
          <div class="info-item">
            <span class="label">最后登录</span>
            <span class="value">{{ profile.user.last_login }}</span>
          </div>
        </div>
        
        <div class="edit-section">
          <h3>编辑信息</h3>
          
          <el-form :model="form" label-width="100px">
            <el-form-item label="邮箱">
              <el-input v-model="form.email" placeholder="请输入邮箱" />
            </el-form-item>
            <el-form-item label="简介">
              <el-input v-model="form.bio" type="textarea" :rows="3" placeholder="请输入简介" />
            </el-form-item>
            <el-form-item label="新密码">
              <el-input v-model="form.password" type="password" placeholder="请输入新密码（留空则不修改）" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="updateProfile" :loading="updating">
                {{ updating ? '更新中...' : '保存修改' }}
              </el-button>
              <el-button v-if="form.password" @click="updatePassword" :loading="updating">
                仅更新密码
              </el-button>
            </el-form-item>
          </el-form>
        </div>
        
        <div class="feedback-section">
          <h3>意见反馈</h3>
          
          <el-form :model="feedbackForm">
            <el-form-item>
              <el-input
                v-model="feedbackForm.content"
                type="textarea"
                :rows="4"
                placeholder="请输入您的意见或建议"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="submitFeedback" :loading="submitting">
                {{ submitting ? '提交中...' : '提交反馈' }}
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
      
      <div v-else class="loading-state">
        <p>加载中...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import Navbar from '@/components/Navbar.vue'
import { authAPI } from '@/api/auth'
import { otherAPI } from '@/api/other'

const profile = ref(null)
const updating = ref(false)
const submitting = ref(false)

const form = reactive({
  email: '',
  bio: '',
  password: ''
})

const feedbackForm = reactive({
  content: ''
})

const loadProfile = async () => {
  try {
    const response = await authAPI.getProfile()
    if (response.success) {
      profile.value = response
      form.email = response.user.email || ''
      form.bio = response.user.bio || ''
    }
  } catch (error) {
    console.log('Failed to load profile:', error)
  }
}

const updateProfile = async () => {
  updating.value = true
  
  try {
    const data = {}
    if (form.email) data.email = form.email
    if (form.bio) data.bio = form.bio
    if (form.password) data.password = form.password
    
    const response = await authAPI.updateProfile(data)
    
    if (response.success) {
      ElMessage.success('更新成功')
      await loadProfile()
    }
  } catch (error) {
    ElMessage.error('更新失败')
  } finally {
    updating.value = false
  }
}

const updatePassword = async () => {
  if (!form.password || form.password.length < 6) {
    ElMessage.error('密码至少需要6位')
    return
  }

  updating.value = true
  try {
    const response = await authAPI.updateProfile({ password: form.password })
    if (response.success) {
      ElMessage.success('密码更新成功')
      form.password = ''
    }
  } catch (error) {
    ElMessage.error('密码更新失败')
  } finally {
    updating.value = false
  }
}

const submitFeedback = async () => {
  if (!feedbackForm.content.trim()) {
    ElMessage.error('请输入反馈内容')
    return
  }
  
  submitting.value = true
  
  try {
    const response = await otherAPI.submitFeedback({ content: feedbackForm.content })
    
    if (response.success) {
      ElMessage.success('反馈提交成功')
      feedbackForm.content = ''
    }
  } catch (error) {
    ElMessage.error('提交失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: var(--color-bg);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.profile-header {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: var(--shadow-card);
  text-align: center;
  margin-bottom: 20px;
}

.avatar {
  font-size: 72px;
  margin-bottom: 10px;
}

.avatar-section h2 {
  margin: 0 0 5px 0;
  font-size: 24px;
}

.avatar-section p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.stats-section {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 600;
  color: var(--color-primary);
}

.stat-label {
  font-size: 12px;
  color: #999;
}

.info-section,
.edit-section,
.feedback-section {
  background: white;
  border-radius: 16px;
  padding: 25px;
  box-shadow: var(--shadow-card);
  margin-bottom: 20px;
}

.info-section h3,
.edit-section h3,
.feedback-section h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #eee;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item .label {
  color: #999;
  font-size: 14px;
}

.info-item .value {
  color: #333;
  font-size: 14px;
}

.loading-state {
  text-align: center;
  padding: 60px;
  color: #999;
}
</style>