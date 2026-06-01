import axios from './axios'

export const petsAPI = {
  getPets(params) {
    return axios.get('/pets', { params })
  },
  addPet(data) {
    return axios.post('/pets', data)
  },
  getPet(id) {
    return axios.get(`/pets/${id}`)
  },
  updatePet(id, data) {
    return axios.put(`/pets/${id}`, data)
  },
  deletePet(id) {
    return axios.delete(`/pets/${id}`)
  }
}