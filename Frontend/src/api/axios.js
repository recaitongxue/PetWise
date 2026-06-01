import axios from 'axios'
import { useStore } from '../store'

const instance = axios.create({
  baseURL: '/api',
  timeout: 30000
})

instance.interceptors.request.use(
  config => {
    const { state } = useStore()
    if (state.token) {
      config.headers.Authorization = state.token
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

instance.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    const { logout } = useStore()
    if (error.response && error.response.status === 401) {
      logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default instance