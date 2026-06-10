<template>
  <div class="health-page">
    <Navbar />
    
    <div class="container">
      <div class="page-header">
        <h1 class="page-title">📊 健康记录</h1>
        <div class="header-actions">
          <select v-model="selectedPet" class="pet-select" @change="loadHealthRecords">
            <option value="">选择宠物</option>
            <option v-for="pet in pets" :key="pet.id" :value="pet.id">
              {{ pet.name }} ({{ pet.breed }})
            </option>
          </select>
          <button class="add-btn" @click="showAddModal = true" :disabled="!selectedPet">
            + 添加记录
          </button>
        </div>
      </div>
      
      <div v-if="selectedPet" class="health-content">
        <!-- 趋势图表 -->
        <div class="trends-section">
          <h3>📈 健康趋势</h3>
          <div class="trend-charts">
            <div class="chart-card">
              <h4>体重变化</h4>
              <div class="chart-placeholder">
                <div v-if="weightTrends.length" class="trend-data">
                  <div v-for="(item, idx) in weightTrends" :key="idx" class="trend-item">
                    <span class="date">{{ item.record_date }}</span>
                    <span class="value">{{ item.weight }} kg</span>
                  </div>
                </div>
                <p v-else class="no-data">暂无体重记录</p>
              </div>
            </div>
            <div class="chart-card">
              <h4>饮食记录</h4>
              <div class="chart-placeholder">
                <div v-if="foodTrends.length" class="trend-data">
                  <div v-for="(item, idx) in foodTrends" :key="idx" class="trend-item">
                    <span class="date">{{ item.record_date }}</span>
                    <span class="value">{{ item.food_amount }}g {{ item.food_type }}</span>
                  </div>
                </div>
                <p v-else class="no-data">暂无饮食记录</p>
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
            </select>
          </div>
          
          <div v-if="records.length" class="records-list">
            <div v-for="record in records" :key="record.id" class="record-card">
              <div class="record-header">
                <span class="record-type">{{ getRecordTypeLabel(record.record_type) }}</span>
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
                  <span class="value">{{ record.stool_status }}</span>
                </div>
                <div v-if="record.activity_level" class="record-item">
                  <span class="label">活动量:</span>
                  <span class="value">{{ record.activity_level }}</span>
                </div>
                <div v-if="record.mood" class="record-item">
                  <span class="label">心情:</span>
                  <span class="value">{{ record.mood }}</span>
                </div>
                <div v-if="record.notes" class="record-item notes">
                  <span class="label">备注:</span>
                  <span class="value">{{ record.notes }}</span>
                </div>
              </div>
              <div class="record-actions">
                <button @click="deleteRecord(record.id)" class="delete-btn">删除</button>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
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
        <div class="empty-icon">📊</div>
        <p>请先选择一只宠物查看健康记录</p>
      </div>
    </div>
    
    <!-- 添加记录弹窗 -->
    <el-dialog title="添加健康记录" :visible.sync="showAddModal" width="500px">
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import Navbar from '@/components/Navbar.vue'
import { petsAPI } from '@/api/pets'

const pets = ref([])
const selectedPet = ref('')
const records = ref([])
const weightTrends = ref([])
const foodTrends = ref([])
const recordType = ref('')
const showAddModal = ref(false)

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
  checkup: '体检'
}

const getRecordTypeLabel = (type) => recordTypeLabels[type] || type

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
      loadHealthRecords()
      loadHealthTrends()
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
      loadHealthRecords()
      loadHealthTrends()
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
  max-width: 1000px;
  margin: 0 auto;
  padding: 30px 20px;
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
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.trends-section {
  margin-bottom: 30px;
}

.trends-section h3 {
  margin-bottom: 15px;
}

.trend-charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.chart-card {
  background: #f9fafb;
  border-radius: 12px;
  padding: 15px;
}

.chart-card h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #666;
}

.trend-data {
  display: flex;
  flex-direction: column;
  gap: 8px;
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

.records-section h3 {
  margin-bottom: 15px;
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
  gap: 15px;
}

.record-card {
  background: #f9fafb;
  border-radius: 12px;
  padding: 15px;
}

.record-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.record-type {
  font-weight: 500;
  color: #667eea;
}

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

.record-item.notes {
  width: 100%;
  margin-top: 10px;
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

.empty-state {
  text-align: center;
  padding: 60px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.empty-icon {
  font-size: 60px;
  margin-bottom: 15px;
}

.empty-state p {
  color: #666;
}
</style>