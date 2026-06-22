import { reactive } from 'vue'

const state = reactive({
  isLoggedIn: !!localStorage.getItem('token'),
  user: (() => {
    try {
      return JSON.parse(localStorage.getItem('user') || 'null')
    } catch {
      return null
    }
  })(),
  token: localStorage.getItem('token') || null
})

const login = (token, user) => {
  state.isLoggedIn = true
  state.token = token
  state.user = user
  localStorage.setItem('token', token)
  localStorage.setItem('user', JSON.stringify(user))
}

const logout = () => {
  state.isLoggedIn = false
  state.token = null
  state.user = null
  localStorage.removeItem('token')
  localStorage.removeItem('user')
}

const updateUser = (user) => {
  state.user = user
  localStorage.setItem('user', JSON.stringify(user))
}

const store = {
  state,
  login,
  logout,
  updateUser,
  install(app) {
    app.provide('store', store)
    app.config.globalProperties.$store = store
  }
}

export function useStore() {
  return store
}

export default store