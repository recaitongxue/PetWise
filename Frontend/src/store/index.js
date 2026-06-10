import { reactive } from 'vue'

const state = reactive({
  isLoggedIn: !!localStorage.getItem('token'),
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  token: localStorage.getItem('token') || null
})

const actions = {
  login(token, user) {
    state.isLoggedIn = true
    state.token = token
    state.user = user
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(user))
  },
  
  logout() {
    state.isLoggedIn = false
    state.token = null
    state.user = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  },
  
  updateUser(user) {
    state.user = user
    localStorage.setItem('user', JSON.stringify(user))
  }
}

const store = {
  state,
  ...actions,
  install(app) {
    app.provide('store', store)
    app.config.globalProperties.$store = store
  }
}

export function useStore() {
  return store
}

export default store