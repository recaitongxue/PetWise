import axios from './axios'

export const agentAPI = {
  chat(data) {
    return axios.post('/agent/chat', data)
  },
  getHistory() {
    return axios.get('/agent/history')
  },
  clearHistory() {
    return axios.delete('/agent/history')
  },
  getAdvice(data) {
    return axios.post('/agent/advice', data)
  },
  emergency(data) {
    return axios.post('/agent/emergency', data)
  },
  healthCheck() {
    return axios.get('/agent/health')
  },
  getModels() {
    return axios.get('/agent/models')
  }
}