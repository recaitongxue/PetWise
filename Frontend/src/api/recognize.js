import axios from './axios'

export const recognizeAPI = {
  recognize(formData) {
    return axios.post('/recognize', formData)
  },
  recognizeBase64(data) {
    return axios.post('/recognize/base64', data)
  },
  getHistory() {
    return axios.get('/recognize/history')
  },
  deleteHistory(id) {
    return axios.delete(`/recognize/history/${id}`)
  },
  getClasses() {
    return axios.get('/classes')
  },
  getModelStatus() {
    return axios.get('/model/status')
  }
}