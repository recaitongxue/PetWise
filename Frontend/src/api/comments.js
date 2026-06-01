import axios from './axios'

export const commentsAPI = {
  getComments(breed) {
    return axios.get(`/comments/${breed}`)
  },
  addComment(data) {
    return axios.post('/comments', data)
  },
  likeComment(id) {
    return axios.post(`/comments/${id}/like`)
  }
}