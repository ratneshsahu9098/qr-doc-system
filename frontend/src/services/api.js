import axios from 'axios'

const api = axios.create({
  baseURL: '/api'
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const auth = {
  login: (username, password) => api.post('/auth/login', { username, password }),
  setup: (username, password) => api.post('/auth/setup', { username, password })
}

export const documents = {
  list: () => api.get('/documents'),
  get: (id) => api.get(`/documents/${id}`),
  create: (formData) => api.post('/documents', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  update: (id, data) => api.put(`/documents/${id}`, data),
  delete: (id) => api.delete(`/documents/${id}`),
  replace: (id, formData) => api.post(`/documents/${id}/replace`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const qr = {
  get: (docId) => `/api/qr/${docId}`,
  getByCode: (code) => `/api/qr/code/${code}`
}

export default api
