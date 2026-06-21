import axios from './axios'

export const healthAPI = {
  // 获取宠物健康记录
  getHealthRecords(petId, params = {}) {
    return axios.get(`/pets/${petId}/health`, { params })
  },

  // 添加健康记录
  addHealthRecord(petId, data) {
    return axios.post(`/pets/${petId}/health`, data)
  },

  // 删除健康记录
  deleteHealthRecord(petId, recordId) {
    return axios.delete(`/pets/${petId}/health/${recordId}`)
  },

  // 获取健康趋势
  getHealthTrends(petId) {
    return axios.get(`/pets/${petId}/health/trends`)
  },

  // 保存问诊结果到健康记录
  saveConsultationRecord(petId, data) {
    console.log('saveConsultationRecord called with:', { petId, data: JSON.stringify(data, null, 2) })
    return axios.post(`/pets/${petId}/health/consultation`, data)
      .then(response => {
        console.log('saveConsultationRecord full response:', response)
        console.log('saveConsultationRecord response.data:', response.data)
        return response.data
      })
      .catch(error => {
        console.error('saveConsultationRecord error:', error)
        console.error('Error response:', error.response?.data)
        throw error
      })
  },

  // 导出问诊记录为Markdown
  exportConsultationMD(petId, recordId) {
    return axios.get(`/pets/${petId}/health/consultation/${recordId}/export`)
      .then(response => response.data)
  }
}

export default healthAPI
