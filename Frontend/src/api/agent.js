import axios from './axios'

const AGENT_BASE = '/agent'

export const agentAPI = {
  // 对话
  chat(data) {
    return axios.post(`${AGENT_BASE}/chat`, data)
  },

  // SSE流式对话
  chatStream(data) {
    return axios.post(`${AGENT_BASE}/chat/stream`, data, {
      responseType: 'stream'
    })
  },

  // 结构化问诊
  structuredConsultation(data) {
    return axios.post(`${AGENT_BASE}/structured-consultation`, data)
  },

  // 获取对话历史
  getHistory(sessionId) {
    return axios.get(`${AGENT_BASE}/history`, { 
      params: sessionId ? { session_id: sessionId } : {} 
    })
  },

  // 清除对话历史
  clearHistory(sessionId) {
    return axios.delete(`${AGENT_BASE}/history`, {
      params: sessionId ? { session_id: sessionId } : {}
    })
  },

  // 获取建议
  getAdvice(data) {
    return axios.post(`${AGENT_BASE}/advice`, data)
  },

  // 紧急咨询
  emergency(data) {
    return axios.post(`${AGENT_BASE}/emergency`, data)
  },

  // 健康检查
  healthCheck() {
    return axios.get(`${AGENT_BASE}/health`, { timeout: 10000 })
  },

  // 获取智能体信息
  getInfo() {
    return axios.get(`${AGENT_BASE}/info`)
  },

  // 获取可用模型
  getModels() {
    return axios.get(`${AGENT_BASE}/models`)
  }
}

export default agentAPI
