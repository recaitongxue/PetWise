<template>
  <div class="schedule-page">
    <Navbar />
    
    <div class="container">
      <div class="page-header">
        <h1 class="page-title">📅 日程提醒</h1>
        <div class="header-actions">
          <select v-model="selectedPet" class="pet-select" @change="loadReminders">
            <option value="">全部宠物</option>
            <option v-for="pet in pets" :key="pet.id" :value="pet.id">
              {{ pet.name }} ({{ pet.breed }})
            </option>
          </select>
          <button class="add-btn" @click="showAddModal = true">
            + 添加提醒
          </button>
          <button class="generate-btn" @click="generateSchedule" :disabled="!selectedPet">
            🤖 生成智能日程
          </button>
        </div>
      </div>

      <!-- 全部宠物统计概览 - 仅在选择全部宠物时显示 -->
      <div v-if="!selectedPet" class="all-pets-stats">
        <div class="stat-card total">
          <div class="stat-icon">🐾</div>
          <div class="stat-info">
            <div class="stat-value">{{ pets.length }}</div>
            <div class="stat-label">宠物总数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📊</div>
          <div class="stat-info">
            <div class="stat-value">{{ totalReminders }}</div>
            <div class="stat-label">总提醒数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">⏳</div>
          <div class="stat-info">
            <div class="stat-value">{{ pendingReminders }}</div>
            <div class="stat-label">待处理</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">✅</div>
          <div class="stat-info">
            <div class="stat-value">{{ completedReminders }}</div>
            <div class="stat-label">已完成</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">⏰</div>
          <div class="stat-info">
            <div class="stat-value">{{ upcomingReminders.length }}</div>
            <div class="stat-label">本周待办</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">💉</div>
          <div class="stat-info">
            <div class="stat-value">{{ vaccinationCount }}</div>
            <div class="stat-label">疫苗提醒</div>
          </div>
        </div>
      </div>
      
      <!-- 即将到来的提醒 -->
      <div class="upcoming-section">
        <h3>⏰ 即将到来的提醒</h3>
        <div v-if="upcomingReminders.length" class="upcoming-list">
          <div v-for="reminder in upcomingReminders" :key="reminder.id" class="upcoming-card">
            <div class="reminder-icon">{{ getReminderIcon(reminder.reminder_type) }}</div>
            <div class="reminder-info">
              <h4>{{ reminder.title }}</h4>
              <p>{{ reminder.pet_name }} - {{ reminder.scheduled_date }}</p>
              <p v-if="reminder.description" class="description">{{ reminder.description }}</p>
            </div>
            <button @click="completeReminder(reminder.id)" class="complete-btn">
              完成
            </button>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>近期没有待处理的提醒</p>
        </div>
      </div>
      
      <!-- 日程列表 - 全部宠物或单个宠物 -->
      <div class="schedule-content">
        <!-- 日程列表 -->
        <div class="reminders-section">
          <h3>📋 {{ selectedPet ? getPetName(selectedPet) + '的日程' : '全部宠物日程' }}</h3>
          <div class="filter-bar">
            <select v-model="reminderType" @change="loadReminders">
              <option value="">全部类型</option>
              <option value="vaccination">疫苗接种</option>
              <option value="deworming">驱虫</option>
              <option value="checkup">体检</option>
              <option value="senior_checkup">老龄体检</option>
              <option value="medication">用药</option>
              <option value="other">其他</option>
            </select>
            <select v-model="reminderStatus" @change="loadReminders">
              <option value="all">全部状态</option>
              <option value="pending">待处理</option>
              <option value="completed">已完成</option>
            </select>
          </div>
          
          <div v-if="displayReminders.length" class="reminders-list">
            <div v-for="reminder in displayReminders" :key="reminder.id" 
                 class="reminder-card"
                 :class="{ completed: reminder.is_completed }">
              <div class="reminder-header">
                <span class="reminder-type-icon">{{ getReminderIcon(reminder.reminder_type) }}</span>
                <span class="reminder-title">{{ reminder.title }}</span>
                <span class="reminder-status" :class="reminder.is_completed ? 'done' : 'pending'">
                  {{ reminder.is_completed ? '已完成' : '待处理' }}
                </span>
              </div>
              <div class="reminder-body">
                <div class="reminder-detail">
                  <span class="label">宠物:</span>
                  <span class="value">{{ reminder.pet_name }}</span>
                </div>
                <div class="reminder-detail">
                  <span class="label">类型:</span>
                  <span class="value">{{ getReminderTypeLabel(reminder.reminder_type) }}</span>
                </div>
                <div class="reminder-detail">
                  <span class="label">日期:</span>
                  <span class="value">{{ reminder.scheduled_date }}</span>
                </div>
                <div v-if="reminder.description" class="reminder-detail full">
                  <span class="label">描述:</span>
                  <span class="value">{{ reminder.description }}</span>
                </div>
                <div v-if="reminder.is_completed" class="reminder-detail">
                  <span class="label">完成时间:</span>
                  <span class="value">{{ reminder.completed_at }}</span>
                </div>
              </div>
              <div class="reminder-actions">
                <button v-if="!reminder.is_completed" 
                        @click="completeReminder(reminder.id)" 
                        class="complete-btn">
                  ✓ 完成
                </button>
                <button @click="deleteReminder(reminder.id)" class="delete-btn">
                  删除
                </button>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <p>暂无日程提醒</p>
          </div>
          
          <div v-if="pagination.pages > 1" class="pagination">
            <button @click="prevPage" :disabled="pagination.page <= 1">上一页</button>
            <span>{{ pagination.page }} / {{ pagination.pages }}</span>
            <button @click="nextPage" :disabled="pagination.page >= pagination.pages">下一页</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 添加提醒弹窗 -->
    <el-dialog title="添加日程提醒" v-model="showAddModal" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="提醒类型">
          <el-select v-model="form.reminder_type">
            <el-option label="疫苗接种" value="vaccination" />
            <el-option label="驱虫" value="deworming" />
            <el-option label="体检" value="checkup" />
            <el-option label="老龄体检" value="senior_checkup" />
            <el-option label="用药" value="medication" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="请输入提醒标题" />
        </el-form-item>
        
        <el-form-item label="日期">
          <el-date-picker v-model="form.scheduled_date" type="date" placeholder="选择日期" />
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" placeholder="详细描述" />
        </el-form-item>
      </el-form>
      
      <div slot="footer" class="dialog-footer">
        <el-button @click="showAddModal = false">取消</el-button>
        <el-button type="primary" @click="submitReminder">添加</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import Navbar from '@/components/Navbar.vue'
import { petsAPI } from '@/api/pets'

const pets = ref([])
const selectedPet = ref('')
const reminders = ref([])
const allReminders = ref([])
const upcomingReminders = ref([])
const reminderType = ref('')
const reminderStatus = ref('all')
const showAddModal = ref(false)

const pagination = reactive({
  page: 1,
  per_page: 10,
  total: 0,
  pages: 0
})

const form = reactive({
  reminder_type: 'vaccination',
  title: '',
  scheduled_date: '',
  description: ''
})

// 全部宠物统计计算
const totalReminders = computed(() => allReminders.value.length)

const pendingReminders = computed(() => 
  allReminders.value.filter(r => !r.is_completed).length
)

const completedReminders = computed(() => 
  allReminders.value.filter(r => r.is_completed).length
)

const vaccinationCount = computed(() => 
  allReminders.value.filter(r => r.reminder_type === 'vaccination').length
)

// 根据选择显示对应的提醒列表
const displayReminders = computed(() => {
  if (selectedPet.value) {
    return reminders.value
  }
  return allReminders.value
})

const getPetName = (petId) => {
  const pet = pets.value.find(p => p.id === petId)
  return pet ? pet.name : ''
}

const reminderTypeLabels = {
  vaccination: '疫苗接种',
  deworming: '驱虫',
  checkup: '体检',
  senior_checkup: '老龄体检',
  medication: '用药',
  other: '其他'
}

const reminderIcons = {
  vaccination: '💉',
  deworming: '🐛',
  checkup: '🏥',
  senior_checkup: '👴',
  medication: '💊',
  other: '📌'
}

const getReminderTypeLabel = (type) => reminderTypeLabels[type] || type
const getReminderIcon = (type) => reminderIcons[type] || '📌'

const loadPets = async () => {
  try {
    const response = await petsAPI.getPets()
    if (response.success) {
      pets.value = response.data || []
    }
  } catch (error) {
    console.error('Failed to load pets:', error)
  }
}

const loadReminders = async () => {
  if (!selectedPet.value) {
    // 加载所有宠物的提醒用于统计
    try {
      const response = await petsAPI.getAllReminders()
      if (response.success) {
        allReminders.value = response.data || []
      }
    } catch (error) {
      console.error('Failed to load all reminders:', error)
    }
    return
  }
  
  try {
    const response = await petsAPI.getReminders(selectedPet.value, {
      page: pagination.page,
      per_page: pagination.per_page,
      reminder_type: reminderType.value,
      status: reminderStatus.value
    })
    
    if (response.success) {
      reminders.value = response.data || []
      pagination.total = response.pagination?.total || 0
      pagination.pages = response.pagination?.pages || 0
    }
  } catch (error) {
    console.error('Failed to load reminders:', error)
  }
}

const loadAllReminders = async () => {
  try {
    const response = await petsAPI.getAllReminders()
    if (response.success) {
      allReminders.value = response.data || []
    }
  } catch (error) {
    console.error('Failed to load all reminders:', error)
  }
}

const loadUpcomingReminders = async () => {
  try {
    const response = await petsAPI.getUpcomingReminders(7)
    if (response.success) {
      upcomingReminders.value = response.data || []
    }
  } catch (error) {
    console.error('Failed to load upcoming reminders:', error)
  }
}

const generateSchedule = async () => {
  if (!selectedPet.value) return
  
  try {
    const response = await petsAPI.generateSchedule(selectedPet.value)
    if (response.success) {
      ElMessage.success(`已生成 ${response.count} 条智能日程`)
      loadReminders()
      loadUpcomingReminders()
    }
  } catch (error) {
    ElMessage.error('生成失败')
  }
}

const submitReminder = async () => {
  if (!selectedPet.value) {
    ElMessage.error('请先选择宠物')
    return
  }
  
  if (!form.title || !form.scheduled_date) {
    ElMessage.error('请填写标题和日期')
    return
  }
  
  try {
    const response = await petsAPI.addReminder(selectedPet.value, {
      ...form,
      scheduled_date: form.scheduled_date instanceof Date 
        ? form.scheduled_date.toISOString().split('T')[0] 
        : form.scheduled_date
    })
    if (response.success) {
      ElMessage.success('提醒添加成功')
      showAddModal.value = false
      resetForm()
      loadReminders()
      loadUpcomingReminders()
    }
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

const completeReminder = async (reminderId) => {
  try {
    const response = await petsAPI.completeReminder(reminderId)
    if (response.success) {
      ElMessage.success('已完成')
      loadReminders()
      loadUpcomingReminders()
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const deleteReminder = async (reminderId) => {
  if (!confirm('确定要删除这个提醒吗？')) return
  
  try {
    const response = await petsAPI.deleteReminder(reminderId)
    if (response.success) {
      ElMessage.success('删除成功')
      loadReminders()
      loadUpcomingReminders()
    }
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const resetForm = () => {
  form.reminder_type = 'vaccination'
  form.title = ''
  form.scheduled_date = ''
  form.description = ''
}

const prevPage = () => {
  if (pagination.page > 1) {
    pagination.page--
    loadReminders()
  }
}

const nextPage = () => {
  if (pagination.page < pagination.pages) {
    pagination.page++
    loadReminders()
  }
}

onMounted(() => {
  loadPets()
  loadAllReminders()
  loadUpcomingReminders()
})
</script>

<style scoped>
.schedule-page {
  min-height: 100vh;
  background: #f5f7fa;
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
  margin-bottom: 30px;
}

.page-title {
  font-size: 28px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.pet-select {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  min-width: 180px;
}

.add-btn, .generate-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.add-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.generate-btn {
  background: #f0f9ff;
  color: #667eea;
}

.add-btn:disabled, .generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 全部宠物统计概览 */
.all-pets-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 15px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-card.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-card.total .stat-label {
  color: rgba(255, 255, 255, 0.9);
}

.stat-icon {
  font-size: 28px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  line-height: 1.2;
}

.stat-value .unit {
  font-size: 14px;
  font-weight: normal;
}

.stat-label {
  font-size: 12px;
  color: #666;
}

.upcoming-section {
  background: white;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.upcoming-section h3 {
  margin-bottom: 15px;
}

.upcoming-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.upcoming-card {
  display: flex;
  align-items: center;
  gap: 15px;
  background: #fff7e6;
  border-radius: 12px;
  padding: 15px;
}

.reminder-icon {
  font-size: 32px;
}

.reminder-info {
  flex: 1;
}

.reminder-info h4 {
  margin: 0 0 5px 0;
  font-size: 16px;
}

.reminder-info p {
  margin: 0;
  color: #666;
  font-size: 13px;
}

.reminder-info .description {
  color: #999;
  margin-top: 5px;
}

.complete-btn {
  padding: 8px 20px;
  background: #67c23a;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.schedule-content {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.reminders-section h3 {
  margin-bottom: 15px;
}

.filter-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.filter-bar select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
}

.reminders-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.reminder-card {
  background: #f9fafb;
  border-radius: 12px;
  padding: 15px;
  transition: all 0.2s;
}

.reminder-card.completed {
  background: #f0f9eb;
  opacity: 0.8;
}

.reminder-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.reminder-type-icon {
  font-size: 24px;
}

.reminder-title {
  font-weight: 500;
  flex: 1;
}

.reminder-status {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
}

.reminder-status.pending {
  background: #fff7e6;
  color: #fa8c16;
}

.reminder-status.done {
  background: #f0f9eb;
  color: #67c23a;
}

.reminder-body {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.reminder-detail {
  display: flex;
  gap: 5px;
}

.reminder-detail.full {
  width: 100%;
}

.reminder-detail .label {
  color: #666;
}

.reminder-detail .value {
  color: #333;
}

.reminder-actions {
  margin-top: 10px;
  display: flex;
  gap: 10px;
}

.reminder-actions button {
  padding: 6px 15px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
}

.complete-btn {
  background: #67c23a;
  color: white;
}

.delete-btn {
  background: #fff2f0;
  color: #f56c6c;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 20px;
}

.pagination button {
  padding: 8px 15px;
  background: #f5f7fa;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.empty-state {
  text-align: center;
  padding: 40px;
}

.empty-icon {
  font-size: 60px;
  margin-bottom: 15px;
}

.empty-state p {
  color: #666;
}
</style>