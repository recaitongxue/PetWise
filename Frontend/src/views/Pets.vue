<template>
  <div class="pets-page">
    <Navbar />
    
    <div class="container">
      <div class="page-header">
        <h1 class="page-title">🐾 我的宠物</h1>
        <div class="header-actions">
          <button class="stats-btn" @click="showStatsModal = true">📊 统计</button>
          <button class="add-btn" @click="openAddModal">+ 添加宠物</button>
        </div>
      </div>
      
      <!-- 宠物统计卡片 -->
      <div class="stats-overview">
        <div class="stat-card">
          <div class="stat-icon">🐱</div>
          <div class="stat-info">
            <div class="stat-value">{{ catCount }}</div>
            <div class="stat-label">猫咪</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🐶</div>
          <div class="stat-info">
            <div class="stat-value">{{ dogCount }}</div>
            <div class="stat-label">狗狗</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🎂</div>
          <div class="stat-info">
            <div class="stat-value">{{ totalAge }}</div>
            <div class="stat-label">总年龄(岁)</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">💉</div>
          <div class="stat-info">
            <div class="stat-value">{{ vaccinatedCount }}</div>
            <div class="stat-label">已绝育</div>
          </div>
        </div>
      </div>
      
      <!-- 宠物列表 -->
      <div v-if="pets.length" class="pets-grid">
        <div 
          v-for="pet in pets" 
          :key="pet.id" 
          class="pet-card"
          @click="viewPetDetail(pet)"
        >
          <div class="pet-avatar" :class="pet.category">
            <img v-if="pet.avatar" :src="getAvatarUrl(pet.avatar)" :alt="pet.name" />
            <span v-else class="avatar-emoji">{{ pet.category === 'cat' ? '🐱' : '🐶' }}</span>
          </div>
          <div class="pet-info">
            <h3>{{ pet.name }}</h3>
            <p class="pet-breed">{{ pet.breed }}</p>
            <div class="pet-tags">
              <span class="tag">{{ pet.age }}岁</span>
              <span class="tag">{{ pet.gender === 'male' ? '公' : '母' }}</span>
              <span v-if="pet.neutered" class="tag success">已绝育</span>
            </div>
            <p v-if="pet.bio" class="pet-bio">{{ pet.bio }}</p>
          </div>
          <div class="pet-actions" @click.stop>
            <button class="action-btn view" @click="viewPetDetail(pet)" title="查看详情">👁️</button>
            <button class="action-btn edit" @click="editPet(pet)" title="编辑">✏️</button>
            <button class="action-btn delete" @click="deletePet(pet.id)" title="删除">🗑️</button>
          </div>
        </div>
      </div>
      
      <div v-else class="empty-state">
        <div class="empty-icon">🐾</div>
        <p>还没有添加宠物</p>
        <p class="empty-hint">添加您的第一个宠物，开始记录它的成长吧！</p>
        <button class="add-btn" @click="openAddModal">添加宠物</button>
      </div>
    </div>
    
    <!-- 添加/编辑宠物对话框 -->
    <el-dialog 
      :title="editingId ? '编辑宠物' : '添加宠物'" 
      v-model="showAddModal" 
      width="550px"
    >
      <el-form :model="form" label-width="100px" class="pet-form">
        <el-form-item label="宠物头像">
          <div class="avatar-upload">
            <div class="avatar-preview" @click="triggerAvatarUpload">
              <img v-if="avatarPreview" :src="avatarPreview" alt="头像预览" />
              <span v-else class="upload-placeholder">📷</span>
            </div>
            <input 
              ref="avatarInput" 
              type="file" 
              accept="image/*" 
              class="hidden-input"
              @change="handleAvatarChange"
            />
            <p class="avatar-hint">点击上传头像</p>
          </div>
        </el-form-item>
        
        <el-form-item label="宠物名称" required>
          <el-input v-model="form.name" placeholder="给宠物起个名字吧" />
        </el-form-item>
        
        <el-form-item label="品种" required>
          <el-input v-model="form.breed" placeholder="如：英短、金毛等" />
        </el-form-item>
        
        <el-form-item label="类别">
          <el-radio-group v-model="form.category">
            <el-radio value="cat">🐱 猫咪</el-radio>
            <el-radio value="dog">🐶 狗狗</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="性别">
          <el-radio-group v-model="form.gender">
            <el-radio value="male">公</el-radio>
            <el-radio value="female">母</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="出生日期">
          <el-date-picker 
            v-model="form.birthday" 
            type="date" 
            placeholder="选择出生日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
          <span v-if="calculatedAge" class="age-hint">（约 {{ calculatedAge }}）</span>
        </el-form-item>
        
        <el-form-item label="体重(kg)">
          <el-input-number v-model="form.weight" :min="0" :max="100" :precision="1" :step="0.1" />
        </el-form-item>
        
        <el-form-item label="毛色">
          <el-input v-model="form.color" placeholder="如：橘色、黑白等" />
        </el-form-item>
        
        <el-form-item label="绝育状态">
          <el-switch v-model="form.neutered" />
          <span class="switch-label">{{ form.neutered ? '已绝育' : '未绝育' }}</span>
        </el-form-item>
        
        <el-form-item label="宠物简介">
          <el-input 
            v-model="form.bio" 
            type="textarea" 
            :rows="3"
            placeholder="介绍一下您的宠物吧..."
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="closeAddModal">取消</el-button>
        <el-button type="primary" @click="submitPet">{{ editingId ? '保存' : '添加' }}</el-button>
      </template>
    </el-dialog>
    
    <!-- 宠物详情对话框 -->
    <el-dialog 
      :title="selectedPet?.name || '宠物详情'" 
      v-model="showDetailModal" 
      width="600px"
      class="pet-detail-dialog"
    >
      <div v-if="selectedPet" class="pet-detail">
        <div class="detail-header">
          <div class="detail-avatar" :class="selectedPet.category">
            <img v-if="selectedPet.avatar" :src="getAvatarUrl(selectedPet.avatar)" :alt="selectedPet.name" />
            <span v-else class="avatar-emoji">{{ selectedPet.category === 'cat' ? '🐱' : '🐶' }}</span>
          </div>
          <div class="detail-basic">
            <h2>{{ selectedPet.name }}</h2>
            <p class="detail-breed">{{ selectedPet.breed }}</p>
            <div class="detail-tags">
              <el-tag>{{ selectedPet.category === 'cat' ? '猫咪' : '狗狗' }}</el-tag>
              <el-tag type="info">{{ selectedPet.gender === 'male' ? '公' : '母' }}</el-tag>
              <el-tag v-if="selectedPet.neutered" type="success">已绝育</el-tag>
            </div>
          </div>
        </div>
        
        <el-divider />
        
        <div class="detail-info-grid">
          <div class="info-item">
            <span class="info-icon">🎂</span>
            <div class="info-content">
              <span class="info-label">年龄</span>
              <span class="info-value">{{ selectedPet.age || calculateAge(selectedPet.birthday) || '未知' }}岁</span>
            </div>
          </div>
          <div class="info-item">
            <span class="info-icon">📅</span>
            <div class="info-content">
              <span class="info-label">生日</span>
              <span class="info-value">{{ selectedPet.birthday || '未设置' }}</span>
            </div>
          </div>
          <div class="info-item">
            <span class="info-icon">⚖️</span>
            <div class="info-content">
              <span class="info-label">体重</span>
              <span class="info-value">{{ selectedPet.weight || '未记录' }} kg</span>
            </div>
          </div>
          <div class="info-item">
            <span class="info-icon">🎨</span>
            <div class="info-content">
              <span class="info-label">毛色</span>
              <span class="info-value">{{ selectedPet.color || '未记录' }}</span>
            </div>
          </div>
        </div>
        
        <div v-if="selectedPet.bio" class="detail-bio">
          <h4>📝 简介</h4>
          <p>{{ selectedPet.bio }}</p>
        </div>
        
        <div class="detail-actions">
          <el-button type="primary" @click="editPet(selectedPet); showDetailModal = false">
            ✏️ 编辑信息
          </el-button>
          <el-button @click="goToHealthRecords(selectedPet)">
            🏥 健康记录
          </el-button>
          <el-button @click="goToSchedule(selectedPet)">
            📅 日程提醒
          </el-button>
        </div>
      </div>
    </el-dialog>
    
    <!-- 统计对话框 -->
    <el-dialog title="📊 宠物统计" v-model="showStatsModal" width="500px">
      <div class="stats-content">
        <div class="stats-chart">
          <div class="chart-title">宠物类型分布</div>
          <div class="chart-bars">
            <div class="chart-bar">
              <div class="bar-label">🐱 猫咪</div>
              <div class="bar-container">
                <div class="bar-fill cat" :style="{ width: catPercentage + '%' }"></div>
              </div>
              <div class="bar-value">{{ catCount }}只</div>
            </div>
            <div class="chart-bar">
              <div class="bar-label">🐶 狗狗</div>
              <div class="bar-container">
                <div class="bar-fill dog" :style="{ width: dogPercentage + '%' }"></div>
              </div>
              <div class="bar-value">{{ dogCount }}只</div>
            </div>
          </div>
        </div>
        
        <el-divider />
        
        <div class="stats-list">
          <div class="stats-item">
            <span class="stats-icon">🐾</span>
            <span class="stats-label">宠物总数</span>
            <span class="stats-value">{{ pets.length }}只</span>
          </div>
          <div class="stats-item">
            <span class="stats-icon">🎂</span>
            <span class="stats-label">平均年龄</span>
            <span class="stats-value">{{ averageAge }}岁</span>
          </div>
          <div class="stats-item">
            <span class="stats-icon">⚖️</span>
            <span class="stats-label">总体重</span>
            <span class="stats-value">{{ totalWeight }}kg</span>
          </div>
          <div class="stats-item">
            <span class="stats-icon">💉</span>
            <span class="stats-label">绝育率</span>
            <span class="stats-value">{{ neuteredPercentage }}%</span>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import Navbar from '@/components/Navbar.vue'
import { petsAPI } from '@/api/pets'

const router = useRouter()
const pets = ref([])
const showAddModal = ref(false)
const showDetailModal = ref(false)
const showStatsModal = ref(false)
const editingId = ref(null)
const selectedPet = ref(null)
const avatarInput = ref(null)
const avatarPreview = ref('')
const avatarFile = ref(null)

const form = reactive({
  name: '',
  breed: '',
  category: 'cat',
  age: 1,
  gender: 'male',
  bio: '',
  birthday: '',
  weight: null,
  color: '',
  neutered: false,
  avatar: ''
})

// 计算属性
const catCount = computed(() => pets.value.filter(p => p.category === 'cat').length)
const dogCount = computed(() => pets.value.filter(p => p.category === 'dog').length)
const totalAge = computed(() => pets.value.reduce((sum, p) => sum + (p.age || 0), 0))
const vaccinatedCount = computed(() => pets.value.filter(p => p.neutered).length)
const averageAge = computed(() => {
  if (pets.value.length === 0) return 0
  return (totalAge.value / pets.value.length).toFixed(1)
})
const totalWeight = computed(() => {
  const total = pets.value.reduce((sum, p) => sum + (p.weight || 0), 0)
  return total.toFixed(1)
})
const neuteredPercentage = computed(() => {
  if (pets.value.length === 0) return 0
  return Math.round((vaccinatedCount.value / pets.value.length) * 100)
})
const catPercentage = computed(() => {
  if (pets.value.length === 0) return 0
  return (catCount.value / pets.value.length) * 100
})
const dogPercentage = computed(() => {
  if (pets.value.length === 0) return 0
  return (dogCount.value / pets.value.length) * 100
})
const calculatedAge = computed(() => {
  if (!form.birthday) return ''
  const birth = new Date(form.birthday)
  const now = new Date()
  const years = Math.floor((now - birth) / (365.25 * 24 * 60 * 60 * 1000))
  if (years < 1) {
    const months = Math.floor((now - birth) / (30 * 24 * 60 * 60 * 1000))
    return `${months}个月`
  }
  return `${years}岁`
})

// 方法
const getAvatarUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  if (path.includes(':') || path.includes('\\') || path.includes('/uploads/')) {
    const filename = path.split('/').pop().split('\\').pop()
    return `/uploads/${filename}`
  }
  return `/uploads/${path}`
}

const calculateAge = (birthday) => {
  if (!birthday) return null
  const birth = new Date(birthday)
  const now = new Date()
  return Math.floor((now - birth) / (365.25 * 24 * 60 * 60 * 1000))
}

const triggerAvatarUpload = () => {
  avatarInput.value?.click()
}

const handleAvatarChange = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  if (!file.type.startsWith('image/')) {
    ElMessage.error('请上传图片文件')
    return
  }
  
  avatarFile.value = file
  const reader = new FileReader()
  reader.onload = (e) => {
    avatarPreview.value = e.target.result
  }
  reader.readAsDataURL(file)
}

const openAddModal = () => {
  resetForm()
  showAddModal.value = true
}

const closeAddModal = () => {
  showAddModal.value = false
  resetForm()
}

const loadPets = async () => {
  try {
    const response = await petsAPI.getPets()
    if (response.success) {
      pets.value = response.data || []
    }
  } catch (error) {
    console.log('Failed to load pets:', error)
  }
}

const viewPetDetail = (pet) => {
  selectedPet.value = pet
  showDetailModal.value = true
}

const editPet = (pet) => {
  editingId.value = pet.id
  form.name = pet.name
  form.breed = pet.breed
  form.category = pet.category
  form.age = pet.age
  form.gender = pet.gender
  form.bio = pet.bio || ''
  form.birthday = pet.birthday || ''
  form.weight = pet.weight || null
  form.color = pet.color || ''
  form.neutered = pet.neutered || false
  form.avatar = pet.avatar || ''
  
  if (pet.avatar) {
    avatarPreview.value = getAvatarUrl(pet.avatar)
  } else {
    avatarPreview.value = ''
  }
  
  showAddModal.value = true
}

const deletePet = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个宠物吗？删除后无法恢复。', '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const response = await petsAPI.deletePet(id)
    if (response.success) {
      ElMessage.success('删除成功')
      await loadPets()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const submitPet = async () => {
  if (!form.name || !form.breed) {
    ElMessage.error('请填写宠物名称和品种')
    return
  }
  
  // 计算年龄
  if (form.birthday) {
    form.age = calculateAge(form.birthday) || 0
  }
  
  try {
    const formData = new FormData()
    Object.keys(form).forEach(key => {
      if (form[key] !== null && form[key] !== '') {
        formData.append(key, form[key])
      }
    })
    
    if (avatarFile.value) {
      formData.append('avatar', avatarFile.value)
    }
    
    if (editingId.value) {
      const response = await petsAPI.updatePet(editingId.value, formData)
      if (response.success) {
        ElMessage.success('更新成功')
      }
    } else {
      const response = await petsAPI.addPet(formData)
      if (response.success) {
        ElMessage.success('添加成功')
      }
    }
    
    showAddModal.value = false
    resetForm()
    await loadPets()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const resetForm = () => {
  editingId.value = null
  form.name = ''
  form.breed = ''
  form.category = 'cat'
  form.age = 1
  form.gender = 'male'
  form.bio = ''
  form.birthday = ''
  form.weight = null
  form.color = ''
  form.neutered = false
  form.avatar = ''
  avatarPreview.value = ''
  avatarFile.value = null
}

const goToHealthRecords = (pet) => {
  showDetailModal.value = false
  router.push(`/health?pet_id=${pet.id}`)
}

const goToSchedule = (pet) => {
  showDetailModal.value = false
  router.push(`/schedule?pet_id=${pet.id}`)
}

onMounted(() => {
  loadPets()
})
</script>

<style scoped>
.pets-page {
  min-height: 100vh;
  background: var(--color-bg);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.page-title {
  font-size: 28px;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.add-btn, .stats-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.add-btn {
  background: var(--gradient-hero);
  color: white;
}

.stats-btn {
  background: white;
  color: var(--color-primary);
  border: 1px solid var(--color-primary);
}

.add-btn:hover, .stats-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(41, 182, 246, 0.3);
}

/* 统计卡片 */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
  margin-bottom: 25px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.stat-icon {
  font-size: 32px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.stat-label {
  font-size: 13px;
  color: #999;
}

/* 宠物卡片 */
.pets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.pet-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: var(--shadow-card);
  cursor: pointer;
  transition: all 0.3s;
}

.pet-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.pet-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  margin: 0 auto 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.pet-avatar.cat {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
}

.pet-avatar.dog {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}

.pet-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-emoji {
  font-size: 40px;
}

.pet-info {
  text-align: center;
}

.pet-info h3 {
  margin: 0 0 5px 0;
  font-size: 18px;
  color: #333;
}

.pet-breed {
  color: #666;
  font-size: 14px;
  margin: 0 0 10px 0;
}

.pet-tags {
  display: flex;
  justify-content: center;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}

.tag {
  padding: 3px 10px;
  background: #f0f2f5;
  border-radius: 12px;
  font-size: 12px;
  color: #666;
}

.tag.success {
  background: #e6f7ed;
  color: #52c41a;
}

.pet-bio {
  font-size: 13px;
  color: #999;
  margin: 10px 0 0 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.pet-actions {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.action-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s;
}

.action-btn.view {
  background: #e6f7ff;
}

.action-btn.edit {
  background: #fff7e6;
}

.action-btn.delete {
  background: #fff1f0;
}

.action-btn:hover {
  transform: scale(1.1);
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px;
  background: white;
  border-radius: 16px;
  box-shadow: var(--shadow-card);
}

.empty-icon {
  font-size: 60px;
  margin-bottom: 15px;
}

.empty-state p {
  color: #666;
  margin: 0 0 5px 0;
}

.empty-hint {
  font-size: 14px;
  color: #999 !important;
  margin-bottom: 20px !important;
}

/* 表单样式 */
.pet-form {
  padding: 10px 20px;
}

.avatar-upload {
  display: flex;
  align-items: center;
  gap: 15px;
}

.avatar-preview {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--color-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  overflow: hidden;
  border: 2px dashed #ddd;
  transition: all 0.3s;
}

.avatar-preview:hover {
  border-color: var(--color-primary);
}

.avatar-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-placeholder {
  font-size: 28px;
}

.hidden-input {
  display: none;
}

.avatar-hint {
  font-size: 12px;
  color: #999;
  margin: 0;
}

.age-hint {
  margin-left: 10px;
  color: #999;
  font-size: 13px;
}

.switch-label {
  margin-left: 10px;
  color: #666;
}

/* 详情弹窗 */
.pet-detail {
  padding: 10px;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 20px;
}

.detail-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.detail-avatar.cat {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
}

.detail-avatar.dog {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}

.detail-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.detail-basic h2 {
  margin: 0 0 5px 0;
  font-size: 24px;
}

.detail-breed {
  color: #666;
  margin: 0 0 10px 0;
}

.detail-tags {
  display: flex;
  gap: 8px;
}

.detail-info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--color-bg);
  border-radius: 10px;
}

.info-icon {
  font-size: 24px;
}

.info-content {
  display: flex;
  flex-direction: column;
}

.info-label {
  font-size: 12px;
  color: #999;
}

.info-value {
  font-size: 15px;
  font-weight: 500;
  color: #333;
}

.detail-bio {
  margin-top: 20px;
  padding: 15px;
  background: var(--color-bg);
  border-radius: 10px;
}

.detail-bio h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #666;
}

.detail-bio p {
  margin: 0;
  color: #333;
  line-height: 1.6;
}

.detail-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

/* 统计弹窗 */
.stats-content {
  padding: 10px;
}

.chart-title {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 15px;
}

.chart-bars {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.chart-bar {
  display: flex;
  align-items: center;
  gap: 15px;
}

.bar-label {
  width: 70px;
  font-size: 14px;
}

.bar-container {
  flex: 1;
  height: 20px;
  background: #f0f2f5;
  border-radius: 10px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 10px;
  transition: width 0.5s ease;
}

.bar-fill.cat {
  background: linear-gradient(90deg, #ffecd2 0%, #fcb69f 100%);
}

.bar-fill.dog {
  background: linear-gradient(90deg, #a8edea 0%, #fed6e3 100%);
}

.bar-value {
  width: 50px;
  text-align: right;
  font-size: 14px;
  color: #666;
}

.stats-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.stats-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: var(--color-bg);
  border-radius: 10px;
}

.stats-icon {
  font-size: 20px;
}

.stats-label {
  flex: 1;
  font-size: 14px;
  color: #666;
}

.stats-value {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

/* 响应式 */
@media (max-width: 768px) {
  .stats-overview {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .detail-info-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-list {
    grid-template-columns: 1fr;
  }
}
</style>
