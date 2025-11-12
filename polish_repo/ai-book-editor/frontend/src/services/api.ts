import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { useAuthStore } from '../store/authStore'

// API基础配置
const API_BASE_URL = 'http://localhost:8000'

// 创建axios实例
const api: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const { token } = useAuthStore.getState()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config

    // 处理401错误（token过期）
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const { refreshToken } = useAuthStore.getState()
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
            refresh_token: refreshToken,
          })

          const { access_token } = response.data
          useAuthStore.getState().setTokens(access_token, refreshToken)

          // 重试原始请求
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        }
      } catch (refreshError) {
        // 刷新token失败，清除认证状态
        useAuthStore.getState().logout()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    // 处理其他错误
    const errorMessage = error.response?.data?.detail || error.message || '请求失败'
    
    // 设置全局错误状态
    useAuthStore.getState().setError(errorMessage)

    return Promise.reject(error)
  }
)

export default api

// 通用API响应类型
export interface ApiResponse<T = any> {
  data: T
  message?: string
  success?: boolean
}

// 分页响应类型
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// 错误响应类型
export interface ApiError {
  detail: string
  code?: string
  field?: string
}