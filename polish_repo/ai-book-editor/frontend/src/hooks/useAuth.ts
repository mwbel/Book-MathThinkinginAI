import { useMutation, useQuery, useQueryClient } from 'react-query'
import { useNavigate } from 'react-router-dom'
import { authService, LoginRequest, RegisterRequest, ChangePasswordRequest, LoginResponse } from '../services/authService'
import { useAuthStore, User } from '../store/authStore'
import { message } from 'antd'

export const useAuth = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { 
    user, 
    token, 
    isAuthenticated, 
    setUser, 
    setTokens, 
    logout: logoutStore, 
    setLoading, 
    setError, 
    clearError 
  } = useAuthStore()

  // 登录
  const loginMutation = useMutation({
    mutationFn: authService.login,
    onMutate: () => {
      setLoading(true)
      clearError()
    },
    onSuccess: (data: LoginResponse) => {
      setTokens(data.access_token, data.refresh_token)
      setUser(data.user)
      setLoading(false)
      message.success('登录成功')
      navigate('/dashboard')
    },
    onError: (error: any) => {
      setLoading(false)
      const errorMessage = error.response?.data?.detail || '登录失败'
      setError(errorMessage)
      message.error(errorMessage)
    }
  })

  // 注册
  const registerMutation = useMutation({
    mutationFn: authService.register,
    onMutate: () => {
      setLoading(true)
      clearError()
    },
    onSuccess: (data: LoginResponse) => {
      setTokens(data.access_token, data.refresh_token)
      setUser(data.user)
      setLoading(false)
      message.success('注册成功')
      navigate('/dashboard')
    },
    onError: (error: any) => {
      setLoading(false)
      const errorMessage = error.response?.data?.detail || '注册失败'
      setError(errorMessage)
      message.error(errorMessage)
    }
  })

  // 登出
  const logoutMutation = useMutation({
    mutationFn: authService.logout,
    onSuccess: () => {
      logoutStore()
      queryClient.clear()
      message.success('已退出登录')
      navigate('/login')
    },
    onError: () => {
      // 即使服务器端登出失败，也要清除本地状态
      logoutStore()
      queryClient.clear()
      navigate('/login')
    }
  })

  // 获取当前用户信息
  const { data: currentUser, isLoading: isLoadingUser } = useQuery({
    queryKey: ['currentUser'],
    queryFn: authService.getCurrentUser,
    enabled: !!token && isAuthenticated,
    retry: false,
    onSuccess: (userData: User) => {
      setUser(userData)
    },
    onError: () => {
      logoutStore()
      navigate('/login')
    }
  })

  // 更新用户信息
  const updateProfileMutation = useMutation({
    mutationFn: authService.updateProfile,
    onSuccess: (userData: User) => {
      setUser(userData)
      queryClient.invalidateQueries(['currentUser'])
      message.success('个人信息更新成功')
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.detail || '更新失败'
      message.error(errorMessage)
    }
  })

  // 修改密码
  const changePasswordMutation = useMutation({
    mutationFn: authService.changePassword,
    onSuccess: () => {
      message.success('密码修改成功')
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.detail || '密码修改失败'
      message.error(errorMessage)
    }
  })

  // 请求密码重置
  const requestPasswordResetMutation = useMutation({
    mutationFn: authService.requestPasswordReset,
    onSuccess: () => {
      message.success('密码重置邮件已发送')
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.detail || '发送失败'
      message.error(errorMessage)
    }
  })

  // 确认密码重置
  const confirmPasswordResetMutation = useMutation({
    mutationFn: authService.confirmPasswordReset,
    onSuccess: () => {
      message.success('密码重置成功')
      navigate('/login')
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.detail || '密码重置失败'
      message.error(errorMessage)
    }
  })

  return {
    // 状态
    user,
    isAuthenticated,
    isLoading: loginMutation.isLoading || registerMutation.isLoading || isLoadingUser,
    
    // 方法
    login: (credentials: LoginRequest) => loginMutation.mutate(credentials),
    register: (userData: RegisterRequest) => registerMutation.mutate(userData),
    logout: () => logoutMutation.mutate(),
    updateProfile: (userData: Partial<User>) => updateProfileMutation.mutate(userData),
    changePassword: (passwordData: ChangePasswordRequest) => changePasswordMutation.mutate(passwordData),
    requestPasswordReset: (email: string) => requestPasswordResetMutation.mutate({ email }),
    confirmPasswordReset: (token: string, newPassword: string) => 
      confirmPasswordResetMutation.mutate({ token, new_password: newPassword }),
    
    // 加载状态
    isLoggingIn: loginMutation.isLoading,
    isRegistering: registerMutation.isLoading,
    isLoggingOut: logoutMutation.isLoading,
    isUpdatingProfile: updateProfileMutation.isLoading,
    isChangingPassword: changePasswordMutation.isLoading,
    isRequestingPasswordReset: requestPasswordResetMutation.isLoading,
    isConfirmingPasswordReset: confirmPasswordResetMutation.isLoading,
  }
}