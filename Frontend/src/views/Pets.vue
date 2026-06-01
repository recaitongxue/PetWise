<template>
  <div class="pets-page">
    <Navbar />
    
    <div class="container">
      <div class="page-header">
        <h1 class="page-title">🐾 我的宠物</h1>
        <button class="add-btn" @click="showAddModal = true">+ 添加宠物</button>
      </div>
      
      <div v-if="pets.length" class="pets-grid">
        <div 
          v-for="pet in pets" 
          :key="pet.id" 
          class="pet-card"
        >
          <div class="pet-icon">{{ pet.category === 'cat' ? '🐱' : '🐶' }}</div>
          <div class="pet-info">
            <h3>{{ pet.name }}</h3>
            <p>{{ pet.breed }}</p>
            <p class="pet-meta">{{ pet.age }}岁 · {{ pet.gender === 'male' ? '公' : '母' }}</p>
          </div>
          <div class="pet-actions">
            <button @click="editPet(pet)">✏️</button>
            <button @click="deletePet(pet.id)">🗑️</button>
          </div>
        </div>
      </div>
      
      <div v-else class="empty-state">
        <div class="empty-icon">🐾</div>
        <p>还没有添加宠物</p>
        <button class="add-btn" @click="showAddModal = true">添加宠物</button>
      </div>
    </div>
    
    <el-dialog title="添加宠物" :visible.sync="showAddModal">
      <el-form :model="form" label-width="80px">
        <el-form-item label="宠物名称">
          <el-input v-model="form.name" placeholder="请输入宠物名称" />
        </el-form-item>
        <el-form-item label="品种">
          <el-input v-model="form.breed" placeholder="请输入品种" />
        </el-form-item>
        <el-form-item label="类别">
          <el-select v-model="form.category">
            <el-option label="猫" value="cat" />
            <el-option label="狗" value="dog" />
          </el-select>
        </el-form-item>
        <el-form-item label="年龄">
          <el-input v-model.number="form.age" type="number" placeholder="请输入年龄" />
        </el-form-item>
        <el-form-item label="性别">
          <el-select v-model="form.gender">
            <el-option label="公" value="male" />
            <el-option label="母" value="female" />
          </el-select>
        </el-form-item>
        <el-form-item label="简介">
          <el-textarea v-model="form.bio" placeholder="请输入宠物简介" />
        </el-form-item>
      </el-form>
      
      <div slot="footer" class="dialog-footer">
        <el-button @click="showAddModal = false">取消</el-button>
        <el-button type="primary" @click="submitPet">{{ editingId ? '保存' : '添加' }}</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElDialog } from 'element-plus'
import Navbar from '@/components/Navbar.vue'
import { petsAPI } from '@/api/pets'

const pets = ref([])
const showAddModal = ref(false)
const editingId = ref(null)

const form = reactive({
  name: '',
  breed: '',
  category: 'cat',
  age: 1,
  gender: 'male',
  bio: ''
})

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

const editPet = (pet) => {
  editingId.value = pet.id
  form.name = pet.name
  form.breed = pet.breed
  form.category = pet.category
  form.age = pet.age
  form.gender = pet.gender
  form.bio = pet.bio || ''
  showAddModal.value = true
}

const deletePet = async (id) => {
  if (!confirm('确定要删除这个宠物吗？')) return
  
  try {
    const response = await petsAPI.deletePet(id)
    if (response.success) {
      ElMessage.success('删除成功')
      await loadPets()
    }
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const submitPet = async () => {
  if (!form.name || !form.breed) {
    ElMessage.error('请填写宠物名称和品种')
    return
  }
  
  try {
    if (editingId.value) {
      const response = await petsAPI.updatePet(editingId.value, form)
      if (response.success) {
        ElMessage.success('更新成功')
      }
    } else {
      const response = await petsAPI.addPet(form)
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
}

onMounted(() => {
  loadPets()
})
</script>

<style scoped>
.pets-page {
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

.add-btn {
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.pets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.pet-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.pet-icon {
  font-size: 50px;
  margin-bottom: 15px;
}

.pet-info {
  text-align: center;
  flex: 1;
}

.pet-info h3 {
  margin: 0 0 5px 0;
  font-size: 18px;
}

.pet-info p {
  margin: 0 0 5px 0;
  color: #666;
  font-size: 14px;
}

.pet-meta {
  font-size: 12px !important;
  color: #999 !important;
}

.pet-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.pet-actions button {
  padding: 6px 12px;
  background: #f5f7fa;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
}

.pet-actions button:hover {
  background: #eee;
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
  margin-bottom: 20px;
}

.dialog-footer {
  text-align: right;
}
</style>