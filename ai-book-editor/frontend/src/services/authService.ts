import api from './api'
import { User } from '../store/authStore'

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  full_name?: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

export interface ChangePasswordRequest {
  current_password: string
  new_password: string
}

export interface PasswordResetRequest {
  email: string
}

export interface PasswordResetConfirm {
  token: string
  new_password: string
}

class AuthService {
  // 用户登录
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await api.post('/auth/login', credentials)
    return response.data
  }

  // 用户注册
  async register(userData: RegisterRequest): Promise<LoginResponse> {
    const response = await api.post('/auth/register', userData)
    return response.data
  }

  // 刷新token
  async refreshToken(refreshToken: string): Promise<{ access_token: string }> {
    const response = await api.post('/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response.data
  }

  // 用户登出
  async logout(): Promise<void> {
    await api.post('/auth/logout')
  }

  // 获取当前用户信息
  async getCurrentUser(): Promise<User> {
    const response = await api.get('/auth/me')
    return response.data
  }

  // 更新用户信息
  async updateProfile(userData: Partial<User>): Promise<User> {
    const response = await api.put('/auth/me', userData)
    return response.data
  }

  // 修改密码
  async changePassword(passwordData: ChangePasswordRequest): Promise<void> {
    await api.post('/auth/change-password', passwordData)
  }

  // 请求密码重置
  async requestPasswordReset(data: PasswordResetRequest): Promise<void> {
    await api.post('/auth/password-reset', data)
  }

  // 确认密码重置
  async confirmPasswordReset(data: PasswordResetConfirm): Promise<void> {
    await api.post('/auth/password-reset/confirm', data)
  }

  // 验证token有效性
  async validateToken(): Promise<boolean> {
    try {
      await this.getCurrentUser()
      return true
    } catch (error) {
      return false
    }
  }
}

export const authService = new AuthService()