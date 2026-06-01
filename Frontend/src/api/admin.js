import axios from './axios'

export const adminAPI = {
  getUsers(params) {
    return axios.get('/admin/users', { params })
  },
  updateUser(id, data) {
    return axios.put(`/admin/users/${id}`, data)
  },
  getStats() {
    return axios.get('/admin/stats')
  },
  getLogs() {
    return axios.get('/admin/logs')
  },
  getAnnouncements() {
    return axios.get('/admin/announcements')
  },
  createAnnouncement(data) {
    return axios.post('/admin/announcements', data)
  },
  getFeedback() {
    return axios.get('/admin/feedback')
  },
  replyFeedback(id, data) {
    return axios.put(`/admin/feedback/${id}`, data)
  },
  updateBreed(breed, data) {
    return axios.put(`/admin/breeds/${breed}`, data)
  }
}