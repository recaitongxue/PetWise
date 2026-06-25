import axios from './axios'

const RECOGNIZE_BASE = '/recognize'

export const recognizeAPI = {
  // 上传图片识别
  recognize(imageFile) {
    const formData = new FormData()
    formData.append('image', imageFile)
    return axios.post(`${RECOGNIZE_BASE}`, formData)
  },

  // Base64识别
  recognizeBase64(imageBase64) {
    return axios.post(`${RECOGNIZE_BASE}/base64`, { image_base64: imageBase64 })
  },

  // 摄像头识别
  recognizeCamera(imageBase64, sessionId) {
    return axios.post(`${RECOGNIZE_BASE}/camera`, { 
      image_base64: imageBase64,
      session_id: sessionId 
    })
  },

  // 摄像头批量识别
  recognizeCameraStream(images, sessionId) {
    return axios.post(`${RECOGNIZE_BASE}/camera/stream`, { 
      images,
      session_id: sessionId 
    })
  },

  // 获取摄像头会话
  getCameraSessions() {
    return axios.get(`${RECOGNIZE_BASE}/camera/sessions`)
  },

  // 获取摄像头会话记录
  getCameraSession(sessionId) {
    return axios.get(`${RECOGNIZE_BASE}/camera/session/${sessionId}`)
  },

  // 获取识别历史
  getHistory(params) {
    return axios.get(`${RECOGNIZE_BASE}/history`, { params })
  },

  // 删除识别记录
  deleteHistory(id) {
    return axios.delete(`${RECOGNIZE_BASE}/history/${id}`)
  },

  // 用户纠错
  correctRecognition(id, correctedBreed, reason) {
    return axios.post(`${RECOGNIZE_BASE}/correct`, {
      recognition_id: id,
      corrected_breed: correctedBreed,
      reason: reason
    })
  },

  // 获取纠错记录
  getCorrections(params) {
    return axios.get(`${RECOGNIZE_BASE}/corrections`, { params })
  },

  // 批量识别
  recognizeBatch(files) {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('images', file)
    })
    return axios.post(`${RECOGNIZE_BASE}/batch`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 获取所有类别
  getClasses() {
    return axios.get('/classes')
  },

  // 模型状态检查
  getModelStatus() {
    return axios.get('/model/status')
  },

  // 获取热门品种
  getPopularBreeds() {
    return axios.get('/breeds/popular')
  }
}

export default recognizeAPI
