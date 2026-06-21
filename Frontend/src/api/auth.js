import axios from './axios'

export const authAPI = {
  register(data) {
    return axios.post('/auth/register', data)
  },
  login(data) {
    return axios.post('/auth/login', data)
  },
  logout() {
    return axios.post('/auth/logout')
  },
  getProfile() {
    return axios.get('/auth/profile')
  },
  updateProfile(data) {
    return axios.put('/auth/profile', data)
  }
}