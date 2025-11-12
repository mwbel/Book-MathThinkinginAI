import React from 'react'
import { Form, Input, Button, Card, Typography, Divider, Space } from 'antd'
import { UserOutlined, LockOutlined, BookOutlined, RightOutlined } from '@ant-design/icons'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { LoginRequest } from '../services/authService'
import { useAuthStore } from '../store/authStore'
import styled from 'styled-components'

const { Title, Text } = Typography

const LoginContainer = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
`

const LoginCard = styled(Card)`
  width: 100%;
  max-width: 400px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border-radius: 16px;
  border: none;
  
  .ant-card-body {
    padding: 40px;
  }
`

const LogoContainer = styled.div`
  text-align: center;
  margin-bottom: 32px;
`

const Logo = styled.div`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  margin-bottom: 16px;
  
  .anticon {
    font-size: 32px;
    color: white;
  }
`

const StyledForm = styled(Form)`
  .ant-form-item {
    margin-bottom: 20px;
  }
  
  .ant-input-affix-wrapper {
    padding: 12px 16px;
    border-radius: 8px;
    border: 1px solid #d9d9d9;
    
    &:hover, &:focus {
      border-color: #667eea;
      box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
    }
  }
  
  .ant-btn-primary {
    height: 48px;
    border-radius: 8px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    font-weight: 500;
    
    &:hover {
      background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
    }
  }
`

const FooterLinks = styled.div`
  text-align: center;
  margin-top: 24px;
  
  a {
    color: #667eea;
    text-decoration: none;
    
    &:hover {
      color: #5a6fd8;
      text-decoration: underline;
    }
  }
`

const Login: React.FC = () => {
  const { login, isLoggingIn } = useAuth()
  const { setUser, setTokens } = useAuthStore()
  const navigate = useNavigate()
  const [form] = Form.useForm()

  const handleSubmit = (values: unknown) => {
    const loginData = values as LoginRequest
    login(loginData)
  }

  const handleSkipLogin = () => {
    // 创建一个临时用户用于演示
    const demoUser = {
      id: 999,
      username: 'demo_user',
      email: 'demo@example.com',
      full_name: '演示用户',
      is_active: true,
      is_superuser: false
    }
    
    // 设置临时token和用户信息
    setTokens('demo_token', 'demo_refresh_token')
    setUser(demoUser)
    
    // 跳转到Dashboard
    navigate('/dashboard')
  }

  return (
    <LoginContainer>
      <LoginCard>
        <LogoContainer>
          <Logo>
            <BookOutlined />
          </Logo>
          <Title level={2} style={{ margin: 0, color: '#1f2937' }}>
            AI书稿编辑器
          </Title>
          <Text type="secondary">
            智能化的书稿编辑和优化平台
          </Text>
        </LogoContainer>

        <StyledForm
          form={form}
          name="login"
          onFinish={handleSubmit}
          autoComplete="off"
          size="large"
        >
          <Form.Item
            name="username"
            rules={[
              { required: true, message: '请输入用户名' },
              { min: 3, message: '用户名至少3个字符' }
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="用户名"
              autoComplete="username"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              { required: true, message: '请输入密码' },
              { min: 6, message: '密码至少6个字符' }
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
              autoComplete="current-password"
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 16 }}>
            <Button
              type="primary"
              htmlType="submit"
              loading={isLoggingIn}
              block
            >
              {isLoggingIn ? '登录中...' : '登录'}
            </Button>
          </Form.Item>
          
          <Form.Item style={{ marginBottom: 16 }}>
            <Button
              type="default"
              onClick={handleSkipLogin}
              block
              icon={<RightOutlined />}
            >
              跳过登录，直接体验
            </Button>
          </Form.Item>
        </StyledForm>

        <Divider>
          <Text type="secondary">还没有账号？</Text>
        </Divider>

        <FooterLinks>
          <Space direction="vertical" size="small">
            <Link to="/register">
              立即注册
            </Link>
            <Link to="/forgot-password">
              忘记密码？
            </Link>
          </Space>
        </FooterLinks>
      </LoginCard>
    </LoginContainer>
  )
}

export default Login