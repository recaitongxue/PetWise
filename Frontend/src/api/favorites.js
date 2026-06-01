import axios from './axios'

export const favoritesAPI = {
  getFavorites() {
    return axios.get('/favorites')
  },
  addFavorite(data) {
    return axios.post('/favorites', data)
  },
  deleteFavorite(breed) {
    return axios.delete(`/favorites/${breed}`)
  }
}