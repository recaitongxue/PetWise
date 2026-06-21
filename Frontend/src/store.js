import { reactive } from 'vue'

const state = reactive({
  user: null,
  token: localStorage.getItem('token') || null,
  isLoggedIn: !!localStorage.getItem('token')
})

const mutations = {
  SET_USER(state, user) {
    state.user = user
  },
  SET_TOKEN(state, token) {
    state.token = token
    state.isLoggedIn = !!token
    if (token) {
      localStorage.setItem('token', token)
    } else {
      localStorage.removeItem('token')
    }
  },
  LOGOUT(state) {
    state.user = null
    state.token = null
    state.isLoggedIn = false
    localStorage.removeItem('token')
  }
}

export function useStore() {
  const setUser = (user) => mutations.SET_USER(state, user)
  const setToken = (token) => mutations.SET_TOKEN(state, token)
  const logout = () => mutations.LOGOUT(state)

  return {
    state,
    setUser,
    setToken,
    logout
  }
}

export default {
  install(app) {
    app.config.globalProperties.$store = state
  }
}