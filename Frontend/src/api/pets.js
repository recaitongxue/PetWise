import axios from './axios'

const PET_BASE = '/pets'

export const petsAPI = {
  // 获取我的宠物列表
  getPets(params) {
    return axios.get(`${PET_BASE}`, { params })
  },

  // 添加宠物
  addPet(data) {
    return axios.post(`${PET_BASE}`, data)
  },

  // 获取宠物详情
  getPet(id) {
    return axios.get(`${PET_BASE}/${id}`)
  },

  // 更新宠物
  updatePet(id, data) {
    return axios.put(`${PET_BASE}/${id}`, data)
  },

  // 删除宠物
  deletePet(id) {
    return axios.delete(`${PET_BASE}/${id}`)
  },

  // ==================== 健康记录相关 ====================
  
  // 添加健康记录
  addHealthRecord(petId, data) {
    return axios.post(`${PET_BASE}/${petId}/health`, data)
  },

  // 获取健康记录
  getHealthRecords(petId, params) {
    return axios.get(`${PET_BASE}/${petId}/health`, { params })
  },

  // 获取健康趋势
  getHealthTrends(petId) {
    return axios.get(`${PET_BASE}/${petId}/health/trends`)
  },

  // 删除健康记录
  deleteHealthRecord(petId, recordId) {
    return axios.delete(`${PET_BASE}/${petId}/health/${recordId}`)
  },

  // ==================== 日程提醒相关 ====================
  
  // 添加提醒
  addReminder(petId, data) {
    return axios.post(`${PET_BASE}/${petId}/schedule`, data)
  },

  // 获取日程列表
  getReminders(petId, params) {
    return axios.get(`${PET_BASE}/${petId}/schedule`, { params })
  },

  // 生成智能日程
  generateSchedule(petId) {
    return axios.post(`${PET_BASE}/${petId}/schedule/generate`)
  },

  // 完成提醒
  completeReminder(reminderId) {
    return axios.put(`/schedule/${reminderId}/complete`)
  },

  // 删除提醒
  deleteReminder(reminderId) {
    return axios.delete(`/schedule/${reminderId}`)
  },

  // 获取即将到来的提醒
  getUpcomingReminders(days = 7) {
    return axios.get('/schedule/upcoming', { params: { days } })
  }
}

export default petsAPI
