import axios from './axios'

export const commentsAPI = {
  getComments(breed, params) {
    return axios.get(`/comments/${encodeURIComponent(breed)}`, { params })
  },
  addComment(data) {
    return axios.post('/comments', data)
  },
  likeComment(id) {
    return axios.post(`/comments/${id}/like`)
  },
  checkLiked(id) {
    return axios.get(`/comments/${id}/liked`)
  },
  deleteComment(id) {
    return axios.delete(`/comments/${id}`)
  }
}