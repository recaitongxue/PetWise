import axios from './axios'

export const adminAPI = {
  // ==================== 用户管理 ====================
  getUsers(params) {
    return axios.get('/admin/users', { params })
  },
  updateUser(id, data) {
    return axios.put(`/admin/users/${id}`, data)
  },
  createUser(data) {
    return axios.post('/admin/users', data)
  },
  deleteUser(id) {
    return axios.delete(`/admin/users/${id}`)
  },
  getUserStats() {
    return axios.get('/admin/users/stats')
  },
  exportUsers() {
    return axios.get('/admin/users/export', { responseType: 'blob' })
  },
  importUsers(data) {
    return axios.post('/admin/users/import', data, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // ==================== 系统统计 ====================
  getStats() {
    return axios.get('/admin/stats')
  },
  getLogs(params) {
    return axios.get('/admin/logs', { params })
  },

  // ==================== 公告管理 ====================
  getAnnouncements() {
    return axios.get('/admin/announcements')
  },
  createAnnouncement(data) {
    return axios.post('/admin/announcements', data)
  },
  updateAnnouncement(id, data) {
    return axios.put(`/admin/announcements/${id}`, data)
  },
  deleteAnnouncement(id) {
    return axios.delete(`/admin/announcements/${id}`)
  },

  // ==================== 用户反馈 ====================
  getFeedback(params) {
    return axios.get('/admin/feedback', { params })
  },
  replyFeedback(id, data) {
    return axios.put(`/admin/feedback/${id}`, data)
  },

  // ==================== 品种信息管理 ====================
  updateBreed(breed, data) {
    return axios.put(`/admin/breeds/${encodeURIComponent(breed)}`, data)
  },
  getBreeds() {
    return axios.get('/admin/breeds')
  },

  // ==================== 大模型管理 ====================
  getLLMModels(params) {
    return axios.get('/admin/models', { params })
  },
  createLLMModel(data) {
    return axios.post('/admin/models', data)
  },
  updateLLMModel(id, data) {
    return axios.put(`/admin/models/${id}`, data)
  },
  deleteLLMModel(id) {
    return axios.delete(`/admin/models/${id}`)
  },
  setDefaultModel(id) {
    return axios.post(`/admin/models/default/${id}`)
  },
  getDefaultEmbeddingModel() {
    return axios.get('/admin/models/embedding/default')
  },
  setDefaultEmbeddingModel(id) {
    return axios.post(`/admin/models/embedding/default/${id}`)
  },

  // ==================== 知识库管理 ====================
  getKnowledge(params) {
    return axios.get('/admin/knowledge', { params })
  },
  createKnowledge(data) {
    return axios.post('/admin/knowledge', data)
  },
  updateKnowledge(id, data) {
    return axios.put(`/admin/knowledge/${id}`, data)
  },
  deleteKnowledge(id) {
    return axios.delete(`/admin/knowledge/${id}`)
  },
  getKnowledgeCategories() {
    return axios.get('/admin/knowledge/categories')
  },
  uploadKnowledgeFile(formData) {
    return axios.post('/admin/knowledge/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // ==================== 难样本管理 ====================
  getHardExamples(params) {
    return axios.get('/admin/samples/hard', { params })
  },
  reviewHardExample(id, data) {
    return axios.put(`/admin/samples/hard/${id}/review`, data)
  },
  deleteHardExample(id) {
    return axios.delete(`/admin/samples/hard/${id}`)
  },
  exportHardExamples(data) {
    return axios.post('/admin/samples/hard/export', data, { responseType: 'blob' })
  },
  getHardExamplesStats() {
    return axios.get('/admin/samples/hard/stats')
  },

  // ==================== 纠错管理 ====================
  getCorrections(params) {
    return axios.get('/admin/corrections', { params })
  },
  updateCorrection(id, data) {
    return axios.put(`/admin/corrections/${id}`, data)
  },

  // ==================== 模型版本管理 ====================
  getModelVersions() {
    return axios.get('/admin/models')
  },
  createModelVersion(data) {
    return axios.post('/admin/models', data)
  },
  activateModelVersion(id) {
    return axios.put(`/admin/models/${id}/activate`)
  },
  deleteModelVersion(id) {
    return axios.delete(`/admin/models/${id}`)
  },
  getModelAccuracy() {
    return axios.get('/admin/models/accuracy')
  },
  getModelStatus() {
    return axios.get('/admin/models/status')
  },

  // ==================== 限流配置管理 ====================
  getRateLimits() {
    return axios.get('/admin/rate-limits')
  },
  addRateLimit(data) {
    return axios.post('/admin/rate-limits', data)
  },
  updateRateLimit(id, data) {
    return axios.put(`/admin/rate-limits/${id}`, data)
  },
  deleteRateLimit(id) {
    return axios.delete(`/admin/rate-limits/${id}`)
  },

  // ==================== 敏感词管理 ====================
  getSensitiveWords() {
    return axios.get('/admin/sensitive-words')
  },
  addSensitiveWord(data) {
    return axios.post('/admin/sensitive-words', data)
  },
  updateSensitiveWord(id, data) {
    return axios.put(`/admin/sensitive-words/${id}`, data)
  },
  deleteSensitiveWord(id) {
    return axios.delete(`/admin/sensitive-words/${id}`)
  },

  // ==================== Prompt模板管理 ====================
  getPromptTemplates() {
    return axios.get('/admin/prompt-templates')
  },
  addPromptTemplate(data) {
    return axios.post('/admin/prompt-templates', data)
  },
  updatePromptTemplate(id, data) {
    return axios.put(`/admin/prompt-templates/${id}`, data)
  },
  deletePromptTemplate(id) {
    return axios.delete(`/admin/prompt-templates/${id}`)
  },

  // ==================== 实时监控 ====================
  getRealtimeStats() {
    return axios.get('/admin/monitor/realtime')
  }
}