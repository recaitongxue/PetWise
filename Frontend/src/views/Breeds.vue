<template>
  <div class="breeds-page">
    <Navbar />

    <div class="container">
      <div class="page-header">
        <h1 class="page-title">📚 品种百科</h1>
        <p class="page-subtitle">探索 23 种常见猫狗品种，了解它们的性格、护理与喂养知识</p>
      </div>

      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索品种名称..."
          clearable
          prefix-icon="Search"
          class="search-input"
        />
        <div class="category-tabs">
          <button
            v-for="tab in categoryTabs"
            :key="tab.value"
            :class="['tab-btn', { active: activeCategory === tab.value }]"
            @click="activeCategory = tab.value"
          >
            {{ tab.icon }} {{ tab.label }}
          </button>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <el-skeleton :rows="6" animated />
      </div>

      <template v-else>
        <div v-if="filteredBreeds.length" class="breeds-grid">
          <div
            v-for="breed in filteredBreeds"
            :key="breed.name"
            class="breed-card"
            @click="goToBreed(breed.name)"
          >
            <div class="breed-icon">{{ breed.category === 'cat' ? '🐱' : '🐶' }}</div>
            <div class="breed-info">
              <h3>{{ breed.name }}</h3>
              <span class="category-tag">{{ breed.category === 'cat' ? '猫科' : '犬科' }}</span>
            </div>
            <div class="card-arrow">→</div>
          </div>
        </div>

        <div v-else class="empty-state">
          <div class="empty-icon">🔍</div>
          <p>未找到匹配的品种</p>
        </div>

        <div class="stats-bar">
          共 {{ allBreeds.length }} 个品种 · 显示 {{ filteredBreeds.length }} 个
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '@/components/Navbar.vue'
import { breedAPI } from '@/api/breed'

const router = useRouter()
const loading = ref(true)
const searchQuery = ref('')
const activeCategory = ref('all')
const allBreeds = ref([])

const categoryTabs = [
  { value: 'all', label: '全部', icon: '🐾' },
  { value: 'dog', label: '狗狗', icon: '🐶' },
  { value: 'cat', label: '猫咪', icon: '🐱' }
]

const filteredBreeds = computed(() => {
  let list = allBreeds.value

  if (activeCategory.value !== 'all') {
    list = list.filter(b => b.category === activeCategory.value)
  }

  if (searchQuery.value.trim()) {
    const q = searchQuery.value.trim().toLowerCase()
    list = list.filter(b => b.name.toLowerCase().includes(q))
  }

  return list
})

const loadBreeds = async () => {
  loading.value = true
  try {
    const response = await breedAPI.getAllBreeds()
    if (response.success) {
      const breeds = []
      if (response.categories?.dog) {
        response.categories.dog.forEach(name => {
          breeds.push({ name, category: 'dog' })
        })
      }
      if (response.categories?.cat) {
        response.categories.cat.forEach(name => {
          breeds.push({ name, category: 'cat' })
        })
      }
      allBreeds.value = breeds
    }
  } catch (error) {
    console.error('Failed to load breeds:', error)
  } finally {
    loading.value = false
  }
}

const goToBreed = (name) => {
  router.push(`/breed/${encodeURIComponent(name)}`)
}

onMounted(() => {
  loadBreeds()
})
</script>

<style scoped>
.breeds-page {
  min-height: 100vh;
  background: var(--color-bg);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-title {
  font-size: 28px;
  color: #333;
  margin-bottom: 8px;
}

.page-subtitle {
  color: #666;
  font-size: 15px;
}

.search-bar {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: var(--shadow-card);
  margin-bottom: 24px;
}

.search-input {
  margin-bottom: 16px;
}

.category-tabs {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.tab-btn {
  padding: 8px 20px;
  border: 1px solid #e0e0e0;
  background: white;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.tab-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.tab-btn.active {
  background: var(--gradient-hero);
  color: white;
  border-color: transparent;
}

.breeds-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}

.breed-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  cursor: pointer;
  box-shadow: var(--shadow-sm);
  transition: all 0.2s;
}

.breed-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(41, 182, 246, 0.15);
}

.breed-icon {
  font-size: 36px;
  flex-shrink: 0;
}

.breed-info {
  flex: 1;
  min-width: 0;
}

.breed-info h3 {
  font-size: 15px;
  margin: 0 0 4px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.category-tag {
  font-size: 12px;
  color: #999;
  background: var(--color-bg);
  padding: 2px 8px;
  border-radius: 10px;
}

.card-arrow {
  color: #ccc;
  font-size: 18px;
  transition: color 0.2s;
}

.breed-card:hover .card-arrow {
  color: var(--color-primary);
}

.loading-state {
  background: white;
  border-radius: 16px;
  padding: 30px;
}

.empty-state {
  text-align: center;
  padding: 60px;
  background: white;
  border-radius: 16px;
  color: #999;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.stats-bar {
  text-align: center;
  margin-top: 24px;
  color: #999;
  font-size: 13px;
}
</style>
