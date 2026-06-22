import axios from './axios'

export const breedAPI = {
  getBreedInfo(breed) {
    return axios.get(`/breed/${encodeURIComponent(breed)}`)
  },
  getAllBreeds() {
    return axios.get('/classes')
  },
  getPopularBreeds() {
    return axios.get('/breeds/popular')
  }
}

export default breedAPI
