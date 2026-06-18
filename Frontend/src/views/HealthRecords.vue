<template>
  <div class="health-page">
    <Navbar />
    
    <div class="container">
      <div class="page-header">
        <h1 class="page-title">🏥 健康记录</h1>
        <div class="header-actions">
          <select v-model="selectedPet" class="pet-select" @change="loadAllData">
            <option value="">全部宠物</option>
            <option v-for="pet in pets" :key="pet.id" :value="pet.id">
              {{ pet.name }} ({{ pet.breed }})
            </option>
          </select>
          <button class="add-btn" @click="showAddModal = true" :disabled="!selectedPet">
            + 添加记录
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
            <div class="stat-value">{{ totalRecords }}</div>
            <div class="stat-label">总记录数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">⚖️</div>
          <div class="stat-info">
            <div class="stat-value">{{ overallLatestWeight || '--' }} <span class="unit">kg</span></div>
            <div class="stat-label">最新体重</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🍖</div>
          <div class="stat-info">
            <div class="stat-value">{{ totalFoodRecords }}</div>
            <div class="stat-label">饮食记录</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">😊</div>
          <div class="stat-info">
            <div class="stat-value">{{ totalHappyDays }}</div>
            <div class="stat-label">开心天数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🏃</div>
          <div class="stat-info">
            <div class="stat-value">{{ totalActiveDays }}</div>
            <div class="stat-label">活跃天数</div>
          </div>
        </div>
      </div>
      
      <div v-if="selectedPet" class="health-content">
        <!-- 健康统计概览 -->
        <div class="stats-overview">
          <div class="stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalRecords }}</div>
              <div class="stat-label">总记录数</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">⚖️</div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.latestWeight || '--' }} <span class="unit">kg</span></div>
              <div class="stat-label">最新体重</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📉</div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.avgWeight || '--' }} <span class="unit">kg</span></div>
              <div class="stat-label">平均体重</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🍖</div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalFoodRecords }}</div>
              <div class="stat-label">饮食记录</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">😊</div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.happyDays || 0 }}</div>
              <div class="stat-label">开心天数</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🏃</div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.activeDays || 0 }}</div>
              <div class="stat-label">活跃天数</div>
            </div>
          </div>
        </div>

        <!-- 记录类型分布 -->
        <div class="type-distribution">
          <h3>📈 记录类型分布</h3>
          <div class="distribution-bars">
            <div class="dist-item" v-for="(count, type) in stats.typeDistribution" :key="type">
              <div class="dist-label">
                <span>{{ getRecordTypeLabel(type) }}</span>
                <span class="dist-count">{{ count }}条</span>
              </div>
              <div class="dist-bar-container">
                <div 
                  class="dist-bar" 
                  :class="type"
                  :style="{ width: (count / stats.maxTypeCount * 100) + '%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 趋势图表 -->
        <div class="trends-section">
          <h3>📉 健康趋势</h3>
          <div class="trend-charts">
            <div class="chart-card">
              <div class="chart-header">
                <h4>⚖️ 体重变化</h4>
                <span v-if="weightTrends.length" class="trend-summary">
                  {{ weightTrends.length > 1 ? `变化: ${calculateWeightChange()}` : '数据不足' }}
                </span>
              </div>
              <div class="chart-placeholder">
                <div v-if="weightTrends.length" class="trend-data">
                  <div v-for="(item, idx) in weightTrends.slice(-7)" :key="idx" class="trend-item">
                    <span class="date">{{ formatDate(item.record_date) }}</span>
                    <span class="value">{{ item.weight }} kg</span>
                  </div>
                </div>
                <p v-else class="no-data">暂无体重记录</p>
              </div>
            </div>
            <div class="chart-card">
              <div class="chart-header">
                <h4>🍖 饮食记录</h4>
                <span v-if="foodTrends.length" class="trend-summary">
                  平均: {{ calculateAvgFood() }}g/天
                </span>
              </div>
              <div class="chart-placeholder">
                <div v-if="foodTrends.length" class="trend-data">
                  <div v-for="(item, idx) in foodTrends.slice(-7)" :key="idx" class="trend-item">
                    <span class="date">{{ formatDate(item.record_date) }}</span>
                    <span class="value">{{ item.food_amount || '--' }}g</span>
                  </div>
                </div>
                <p v-else class="no-data">暂无饮食记录</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 最近健康状态 -->
        <div class="latest-status" v-if="latestRecords.length">
          <h3>🩺 最近健康状态</h3>
          <div class="status-cards">
            <div 
              v-for="record in latestRecords" 
              :key="record.id" 
              class="status-card"
              :class="record.record_type"
            >
              <div class="status-icon">{{ getRecordIcon(record) }}</div>
              <div class="status-content">
                <div class="status-type">{{ getRecordTypeLabel(record.record_type) }}</div>
                <div class="status-value">{{ getRecordValue(record) }}</div>
                <div class="status-date">{{ formatDate(record.record_date) }}</div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 记录列表 -->
        <div class="records-section">
          <h3>📋 健康记录列表</h3>
          <div class="filter-bar">
            <select v-model="recordType" @change="loadHealthRecords">
              <option value="">全部类型</option>
              <option value="weight">体重</option>
              <option value="food">饮食</option>
              <option value="stool">排便</option>
              <option value="activity">活动</option>
              <option value="mood">心情</option>
              <option value="checkup">体检</option>
              <option value="consultation">问诊记录</option>
            </select>
          </div>
          
          <div v-if="records.length" class="records-list">
            <div v-for="record in records" :key="record.id" class="record-card" @click="openConsultationDetail(record)" :class="{ 'clickable': record.record_type === 'consultation' }">
              <div class="record-header">
                <span class="record-type-badge" :class="record.record_type">
                  {{ getRecordIcon(record) }} {{ getRecordTypeLabel(record.record_type) }}
                </span>
                <span class="record-date">{{ record.record_date }}</span>
              </div>
              <div class="record-body">
                <div v-if="record.weight" class="record-item">
                  <span class="label">体重:</span>
                  <span class="value">{{ record.weight }} kg</span>
                </div>
                <div v-if="record.food_amount" class="record-item">
                  <span class="label">食量:</span>
                  <span class="value">{{ record.food_amount }}g</span>
                </div>
                <div v-if="record.food_type" class="record-item">
                  <span class="label">食物类型:</span>
                  <span class="value">{{ record.food_type }}</span>
                </div>
                <div v-if="record.stool_status" class="record-item">
                  <span class="label">排便状态:</span>
                  <span class="value status-badge" :class="record.stool_status">{{ getStoolStatus(record.stool_status) }}</span>
                </div>
                <div v-if="record.activity_level" class="record-item">
                  <span class="label">活动量:</span>
                  <span class="value">{{ getActivityLevel(record.activity_level) }}</span>
                </div>
                <div v-if="record.mood" class="record-item">
                  <span class="label">心情:</span>
                  <span class="value">{{ getMood(record.mood) }}</span>
                </div>
                <div v-if="record.notes" class="record-item notes">
                  <span class="label">备注:</span>
                  <span class="value">{{ record.notes }}</span>
                </div>
                <!-- 问诊记录特殊显示 -->
                <div v-if="record.record_type === 'consultation'" class="record-item consultation-preview">
                  <span class="label">症状:</span>
                  <span class="value">{{ record.consultation_data ? JSON.parse(record.consultation_data).symptoms?.join(', ') : '--' }}</span>
                </div>
              </div>
              <div class="record-actions">
                <button @click.stop="deleteRecord(record.id)" class="delete-btn">删除</button>
              </div>
            </div>
          </div>
          <div v-else class="empty-state-small">
            <p>暂无健康记录</p>
          </div>
          
          <div v-if="pagination.pages > 1" class="pagination">
            <button @click="prevPage" :disabled="pagination.page <= 1">上一页</button>
            <span>{{ pagination.page }} / {{ pagination.pages }}</span>
            <button @click="nextPage" :disabled="pagination.page >= pagination.pages">下一页</button>
          </div>
        </div>
      </div>
      
      <div v-else class="empty-state">
        <div class="empty-icon">🏥</div>
        <p>请先选择一只宠物查看健康记录</p>
      </div>
    </div>
    
    <!-- 添加记录弹窗 -->
    <el-dialog title="添加健康记录" v-model="showAddModal" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="记录类型">
          <el-select v-model="form.record_type">
            <el-option label="体重" value="weight" />
            <el-option label="饮食" value="food" />
            <el-option label="排便" value="stool" />
            <el-option label="活动" value="activity" />
            <el-option label="心情" value="mood" />
            <el-option label="体检" value="checkup" />
          </el-select>
        </el-form-item>
        
        <el-form-item v-if="form.record_type === 'weight'" label="体重">
          <el-input v-model.number="form.weight" type="number" placeholder="请输入体重(kg)" />
        </el-form-item>
        
        <el-form-item v-if="form.record_type === 'food'" label="食量">
          <el-input v-model.number="form.food_amount" type="number" placeholder="请输入食量(g)" />
        </el-form-item>
        
        <el-form-item v-if="form.record_type === 'food'" label="食物类型">
          <el-input v-model="form.food_type" placeholder="请输入食物类型" />
        </el-form-item>
        
        <el-form-item v-if="form.record_type === 'stool'" label="排便状态">
          <el-select v-model="form.stool_status">
            <el-option label="正常" value="normal" />
            <el-option label="偏软" value="soft" />
            <el-option label="偏硬" value="hard" />
            <el-option label="异常" value="abnormal" />
          </el-select>
        </el-form-item>
        
        <el-form-item v-if="form.record_type === 'activity'" label="活动量">
          <el-select v-model="form.activity_level">
            <el-option label="活跃" value="active" />
            <el-option label="正常" value="normal" />
            <el-option label="较少" value="low" />
            <el-option label="很少" value="very_low" />
          </el-select>
        </el-form-item>
        
        <el-form-item v-if="form.record_type === 'mood'" label="心情">
          <el-select v-model="form.mood">
            <el-option label="开心" value="happy" />
            <el-option label="正常" value="normal" />
            <el-option label="低落" value="sad" />
            <el-option label="焦虑" value="anxious" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="备注">
          <el-input v-model="form.notes" type="textarea" placeholder="其他备注信息" />
        </el-form-item>
      </el-form>
      
      <div slot="footer" class="dialog-footer">
        <el-button @click="showAddModal = false">取消</el-button>
        <el-button type="primary" @click="submitRecord">添加</el-button>
      </div>
    </el-dialog>
    
    <!-- 问诊详情弹窗 -->
    <el-dialog title="👩⚕️ 问诊记录详情" v-model="showConsultationModal" width="700px" @close="closeConsultationModal">
      <div v-if="currentConsultation" class="consultation-detail">
        <div class="detail-section">
          <h4>📝 基本信息</h4>
          <div class="detail-row">
            <span class="detail-label">问诊日期:</span>
            <span class="detail-value">{{ currentConsultation.record_date }}</span>
          </div>
          <div v-if="consultationData.pet_name" class="detail-row">
            <span class="detail-label">宠物名称:</span>
            <span class="detail-value">{{ consultationData.pet_name }}</span>
          </div>
          <div v-if="consultationData.pet_type" class="detail-row">
            <span class="detail-label">宠物类型:</span>
            <span class="detail-value">{{ consultationData.pet_type }}</span>
          </div>
          <div v-if="consultationData.pet_breed" class="detail-row">
            <span class="detail-label">宠物品种:</span>
            <span class="detail-value">{{ consultationData.pet_breed }}</span>
          </div>
          <div v-if="consultationData.pet_age" class="detail-row">
            <span class="detail-label">宠物年龄:</span>
            <span class="detail-value">{{ consultationData.pet_age }}</span>
          </div>
          <div v-if="consultationData.pet_weight" class="detail-row">
            <span class="detail-label">宠物体重:</span>
            <span class="detail-value">{{ consultationData.pet_weight }} kg</span>
          </div>
        </div>
        
        <div class="detail-section" v-if="currentConsultation.consultation_data">
          <h4>🏥 问诊信息</h4>
          <div v-if="consultationData.symptoms" class="detail-row">
            <span class="detail-label">症状:</span>
            <span class="detail-value">{{ consultationData.symptoms.join(', ') }}</span>
          </div>
          <div v-if="consultationData.duration" class="detail-row">
            <span class="detail-label">发病时长:</span>
            <span class="detail-value">{{ consultationData.duration }}</span>
          </div>
          <div v-if="consultationData.severity" class="detail-row">
            <span class="detail-label">严重程度:</span>
            <span class="detail-value">{{ consultationData.severity }}</span>
          </div>
          <div v-if="consultationData.additional_info" class="detail-row">
            <span class="detail-label">补充信息:</span>
            <span class="detail-value">{{ consultationData.additional_info }}</span>
          </div>
        </div>
        
        <div class="detail-section" v-if="consultationData.consultation_result">
          <h4>💡 AI分析建议</h4>
          <div class="consultation-result">
            <div v-html="renderMarkdown(consultationData.consultation_result)"></div>
          </div>
        </div>
        
        <div class="detail-section" v-if="consultationData.recommendation">
          <h4>📋 行动建议</h4>
          <div class="consultation-result recommendation">
            <p>{{ consultationData.recommendation }}</p>
          </div>
        </div>
      </div>
      
      <div slot="footer" class="dialog-footer">
        <el-button @click="closeConsultationModal">关闭</el-button>
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
const records = ref([])
const weightTrends = ref([])
const foodTrends = ref([])
const allRecords = ref([])
const allPetsAllRecords = ref([])
const recordType = ref('')
const showAddModal = ref(false)
const showConsultationModal = ref(false)
const currentConsultation = ref(null)

const pagination = reactive({
  page: 1,
  per_page: 10,
  total: 0,
  pages: 0
})

const form = reactive({
  record_type: 'weight',
  weight: null,
  food_amount: null,
  food_type: '',
  stool_status: '',
  activity_level: '',
  mood: '',
  notes: ''
})

const recordTypeLabels = {
  weight: '体重',
  food: '饮食',
  stool: '排便',
  activity: '活动',
  mood: '心情',
  checkup: '体检',
  consultation: '问诊记录'
}

const recordTypeIcons = {
  weight: '⚖️',
  food: '🍖',
  stool: '💩',
  activity: '🏃',
  mood: '😊',
  checkup: '🩺',
  consultation: '👩⚕️'
}

// 总体统计 - 所有宠物
const totalRecords = computed(() => allPetsAllRecords.value.length)

const totalFoodRecords = computed(() => 
  allPetsAllRecords.value.filter(r => r.record_type === 'food').length
)

const totalHappyDays = computed(() => 
  allPetsAllRecords.value.filter(r => r.record_type === 'mood' && r.mood === 'happy').length
)

const totalActiveDays = computed(() => 
  allPetsAllRecords.value.filter(r => r.record_type === 'activity' && r.activity_level === 'active').length
)

const overallLatestWeight = computed(() => {
  const weightRecords = allPetsAllRecords.value.filter(r => r.weight)
  if (weightRecords.length === 0) return null
  return weightRecords[0].weight
})

// 计算统计
const stats = computed(() => {
  const typeDistribution = {}
  let totalFoodRecords = 0
  let happyDays = 0
  let activeDays = 0
  let maxTypeCount = 0

  allRecords.value.forEach(record => {
    const type = record.record_type
    typeDistribution[type] = (typeDistribution[type] || 0) + 1
    
    if (type === 'food') totalFoodRecords++
    if (type === 'mood' && record.mood === 'happy') happyDays++
    if (type === 'activity' && record.activity_level === 'active') activeDays++
  })

  maxTypeCount = Math.max(...Object.values(typeDistribution), 1)

  // 计算体重
  const weightRecords = allRecords.value.filter(r => r.weight)
  const latestWeight = weightRecords.length > 0 ? weightRecords[0].weight : null
  const avgWeight = weightRecords.length > 0 
    ? (weightRecords.reduce((sum, r) => sum + r.weight, 0) / weightRecords.length).toFixed(1)
    : null

  return {
    totalRecords: allRecords.value.length,
    latestWeight,
    avgWeight,
    totalFoodRecords,
    happyDays,
    activeDays,
    typeDistribution,
    maxTypeCount
  }
})

// 最新记录
const latestRecords = computed(() => {
  const latest = {}
  allRecords.value.forEach(record => {
    if (!latest[record.record_type]) {
      latest[record.record_type] = record
    }
  })
  return Object.values(latest).slice(0, 6)
})

const getRecordTypeLabel = (type) => recordTypeLabels[type] || type
const getRecordIcon = (record) => recordTypeIcons[record.record_type] || '📝'

const getRecordValue = (record) => {
  switch (record.record_type) {
    case 'weight': return `${record.weight} kg`
    case 'food': return `${record.food_amount || '--'}g`
    case 'stool': return getStoolStatus(record.stool_status)
    case 'activity': return getActivityLevel(record.activity_level)
    case 'mood': return getMood(record.mood)
    case 'checkup': return record.notes || '已完成'
    case 'consultation': return '点击查看详情'
    default: return '--'
  }
}

const getStoolStatus = (status) => {
  const map = { normal: '正常', soft: '偏软', hard: '偏硬', abnormal: '异常' }
  return map[status] || status
}

const getActivityLevel = (level) => {
  const map = { active: '活跃', normal: '正常', low: '较少', very_low: '很少' }
  return map[level] || level
}

const getMood = (mood) => {
  const map = { happy: '开心', normal: '正常', sad: '低落', anxious: '焦虑' }
  return map[mood] || mood
}

const formatDate = (dateStr) => {
  if (!dateStr) return '--'
  return dateStr.split(' ')[0]
}

// 解析问诊数据
const consultationData = computed(() => {
  if (!currentConsultation.value?.consultation_data) return {}
  try {
    return JSON.parse(currentConsultation.value.consultation_data)
  } catch {
    return {}
  }
})

// 简单的Markdown渲染
const renderMarkdown = (text) => {
  if (!text) return ''
  let html = text
    .replace(/### (.+)/g, '<h3>$1</h3>')
    .replace(/## (.+)/g, '<h2>$1</h2>')
    .replace(/### (.+)/g, '<h3>$1</h3>')
    .replace(/#### (.+)/g, '<h4>$1</h4>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/^\- (.+)$/gm, '<li>$1</li>')
    .replace(/^(\d+)\. (.+)$/gm, '<li>$1. $2</li>')
    .replace(/^\*\*\*$/gm, '<hr>')
    .replace(/\n/g, '<br>')
    .replace(/<li>/g, '<ul><li>')
    .replace(/<\/li>(?!<li>)/g, '</li></ul>')
  return html
}

const calculateWeightChange = () => {
  if (weightTrends.value.length < 2) return '数据不足'
  const latest = weightTrends.value[0].weight
  const oldest = weightTrends.value[weightTrends.value.length - 1].weight
  const change = (latest - oldest).toFixed(1)
  return change > 0 ? `+${change}kg` : `${change}kg`
}

const calculateAvgFood = () => {
  if (foodTrends.value.length === 0) return '--'
  const total = foodTrends.value.reduce((sum, r) => sum + (r.food_amount || 0), 0)
  return Math.round(total / foodTrends.value.length)
}

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

const loadAllData = async () => {
  if (!selectedPet.value) return
  
  // 加载所有记录用于统计
  try {
    const response = await petsAPI.getHealthRecords(selectedPet.value, {
      page: 1,
      per_page: 1000
    })
    if (response.success) {
      allRecords.value = response.data || []
    }
  } catch (error) {
    console.error('Failed to load all records:', error)
  }
  
  loadHealthRecords()
  loadHealthTrends()
}

const loadHealthRecords = async () => {
  if (!selectedPet.value) return
  
  try {
    const response = await petsAPI.getHealthRecords(selectedPet.value, {
      page: pagination.page,
      per_page: pagination.per_page,
      record_type: recordType.value
    })
    
    if (response.success) {
      records.value = response.data || []
      pagination.total = response.pagination?.total || 0
      pagination.pages = response.pagination?.pages || 0
    }
  } catch (error) {
    console.error('Failed to load health records:', error)
  }
}

const loadHealthTrends = async () => {
  if (!selectedPet.value) return
  
  try {
    const response = await petsAPI.getHealthTrends(selectedPet.value)
    if (response.success) {
      weightTrends.value = response.weight_trends || []
      foodTrends.value = response.food_trends || []
    }
  } catch (error) {
    console.error('Failed to load health trends:', error)
  }
}

const submitRecord = async () => {
  if (!selectedPet.value) {
    ElMessage.error('请先选择宠物')
    return
  }
  
  if (!form.record_type) {
    ElMessage.error('请选择记录类型')
    return
  }
  
  try {
    const response = await petsAPI.addHealthRecord(selectedPet.value, form)
    if (response.success) {
      ElMessage.success('记录添加成功')
      showAddModal.value = false
      resetForm()
      loadAllData()
    }
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

const deleteRecord = async (recordId) => {
  if (!confirm('确定要删除这条记录吗？')) return
  
  try {
    const response = await petsAPI.deleteHealthRecord(selectedPet.value, recordId)
    if (response.success) {
      ElMessage.success('删除成功')
      loadAllData()
    }
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const resetForm = () => {
  form.record_type = 'weight'
  form.weight = null
  form.food_amount = null
  form.food_type = ''
  form.stool_status = ''
  form.activity_level = ''
  form.mood = ''
  form.notes = ''
}

const openConsultationDetail = (record) => {
  if (record.record_type === 'consultation') {
    currentConsultation.value = record
    showConsultationModal.value = true
  }
}

const closeConsultationModal = () => {
  showConsultationModal.value = false
  currentConsultation.value = null
}

const prevPage = () => {
  if (pagination.page > 1) {
    pagination.page--
    loadHealthRecords()
  }
}

const nextPage = () => {
  if (pagination.page < pagination.pages) {
    pagination.page++
    loadHealthRecords()
  }
}

onMounted(() => {
  loadPets()
})
</script>

<style scoped>
.health-page {
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
  margin-bottom: 25px;
}

.page-title {
  font-size: 28px;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 15px;
}

.pet-select {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  min-width: 200px;
}

.add-btn {
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.add-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.health-content {
  background: white;
  border-radius: 16px;
  padding: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

/* 统计概览 */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 15px;
  margin-bottom: 25px;
}

.stat-card {
  background: linear-gradient(135deg, #f5f7fa 0%, #fff 100%);
  border-radius: 12px;
  padding: 15px;
  display: flex;
  align-items: center;
  gap: 12px;
  border: 1px solid #eee;
}

.stat-icon {
  font-size: 28px;
}

.stat-value {
  font-size: 22px;
  font-weight: 600;
  color: #333;
}

.stat-value .unit {
  font-size: 12px;
  color: #999;
  font-weight: normal;
}

.stat-label {
  font-size: 12px;
  color: #999;
}

/* 记录类型分布 */
.type-distribution {
  margin-bottom: 25px;
  padding: 20px;
  background: #f9fafb;
  border-radius: 12px;
}

.type-distribution h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
}

.distribution-bars {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.dist-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.dist-label {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #666;
}

.dist-count {
  color: #999;
}

.dist-bar-container {
  height: 8px;
  background: #eee;
  border-radius: 4px;
  overflow: hidden;
}

.dist-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.dist-bar.weight { background: linear-gradient(90deg, #667eea, #764ba2); }
.dist-bar.food { background: linear-gradient(90deg, #f093fb, #f5576c); }
.dist-bar.stool { background: linear-gradient(90deg, #4facfe, #00f2fe); }
.dist-bar.activity { background: linear-gradient(90deg, #43e97b, #38f9d7); }
.dist-bar.mood { background: linear-gradient(90deg, #fa709a, #fee140); }
.dist-bar.checkup { background: linear-gradient(90deg, #a8edea, #fed6e3); }

/* 趋势图表 */
.trends-section {
  margin-bottom: 25px;
}

.trends-section h3 {
  margin-bottom: 15px;
  font-size: 16px;
}

.trend-charts {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.chart-card {
  background: #f9fafb;
  border-radius: 12px;
  padding: 15px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.chart-header h4 {
  margin: 0;
  font-size: 14px;
}

.trend-summary {
  font-size: 12px;
  color: #667eea;
}

.trend-data {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.trend-item {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
  font-size: 13px;
}

.trend-item .date {
  color: #999;
}

.trend-item .value {
  color: #333;
  font-weight: 500;
}

.no-data {
  color: #999;
  text-align: center;
  padding: 20px;
}

/* 最新状态 */
.latest-status {
  margin-bottom: 25px;
}

.latest-status h3 {
  margin-bottom: 15px;
  font-size: 16px;
}

.status-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}

.status-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px;
  background: #f9fafb;
  border-radius: 12px;
  border-left: 4px solid #667eea;
}

.status-card.weight { border-left-color: #667eea; }
.status-card.food { border-left-color: #f5576c; }
.status-card.stool { border-left-color: #4facfe; }
.status-card.activity { border-left-color: #43e97b; }
.status-card.mood { border-left-color: #fa709a; }
.status-card.checkup { border-left-color: #a8edea; }

.status-icon {
  font-size: 24px;
}

.status-type {
  font-size: 12px;
  color: #999;
}

.status-value {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.status-date {
  font-size: 11px;
  color: #999;
}

/* 记录列表 */
.records-section h3 {
  margin-bottom: 15px;
  font-size: 16px;
}

.filter-bar {
  margin-bottom: 15px;
}

.filter-bar select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
}

.records-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.record-card {
  background: #f9fafb;
  border-radius: 12px;
  padding: 15px;
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.record-type-badge {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.record-type-badge.weight { background: #e6e9ff; color: #667eea; }
.record-type-badge.food { background: #ffe6e9; color: #f5576c; }
.record-type-badge.stool { background: #e0f7ff; color: #00c4cc; }
.record-type-badge.activity { background: #e0ffe9; color: #36b37e; }
.record-type-badge.mood { background: #fff0f3; color: #e44d8a; }
.record-type-badge.checkup { background: #f0f7ff; color: #5a7dff; }

.record-date {
  color: #999;
  font-size: 13px;
}

.record-body {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.record-item {
  display: flex;
  gap: 5px;
}

.record-item .label {
  color: #666;
}

.record-item .value {
  color: #333;
}

.status-badge {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.status-badge.normal { background: #e6f7ed; color: #52c41a; }
.status-badge.soft { background: #fff7e6; color: #faad14; }
.status-badge.hard { background: #fff1f0; color: #ff4d4f; }
.status-badge.abnormal { background: #fff1f0; color: #f5222d; }

.record-item.notes {
  width: 100%;
  margin-top: 8px;
}

.record-actions {
  margin-top: 10px;
  text-align: right;
}

.delete-btn {
  padding: 5px 15px;
  background: #fff2f0;
  color: #f56c6c;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
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

.empty-state, .empty-state-small {
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 16px;
}

.empty-state-small {
  padding: 30px;
}

.empty-icon {
  font-size: 60px;
  margin-bottom: 15px;
}

.empty-state p {
  color: #666;
  margin: 0;
}

/* 问诊记录样式 */
.record-type-badge.consultation { background: #e8f5e9; color: #2e7d32; }
.record-card.clickable {
  cursor: pointer;
  transition: box-shadow 0.2s ease;
}
.record-card.clickable:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.consultation-preview {
  width: 100%;
}

/* 问诊详情弹窗 */
.consultation-detail {
  max-height: 500px;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.detail-section:last-child {
  border-bottom: none;
}

.detail-section h4 {
  margin: 0 0 12px 0;
  font-size: 15px;
  color: #333;
}

.detail-row {
  display: flex;
  gap: 10px;
  margin-bottom: 8px;
  font-size: 14px;
}

.detail-label {
  color: #666;
  font-weight: 500;
  min-width: 80px;
}

.detail-value {
  color: #333;
}

.consultation-result {
  background: #f9fafb;
  padding: 15px;
  border-radius: 8px;
  white-space: pre-wrap;
  word-break: break-word;
}

.consultation-result h2,
.consultation-result h3,
.consultation-result h4 {
  margin-top: 15px;
  margin-bottom: 8px;
}

.consultation-result ul {
  margin: 5px 0;
  padding-left: 20px;
}

.consultation-result li {
  margin-bottom: 4px;
}

.consultation-result strong {
  color: #667eea;
}

/* 响应式 */
@media (max-width: 768px) {
  .stats-overview {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .distribution-bars {
    grid-template-columns: 1fr;
  }
  
  .trend-charts {
    grid-template-columns: 1fr;
  }
  
  .status-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
