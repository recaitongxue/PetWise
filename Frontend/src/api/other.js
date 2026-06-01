import axios from './axios'

export const otherAPI = {
  getBreedInfo(breed) {
    return axios.get(`/breed/${breed}`)
  },
  submitFeedback(data) {
    return axios.post('/feedback', data)
  },
  healthCheck() {
    return axios.get('/health_check')
  }
}