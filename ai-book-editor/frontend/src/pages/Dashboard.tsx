import React from 'react'
import { Row, Col, Card, Statistic, List, Button, Typography, Space, Avatar, Tag } from 'antd'
import { 
  BookOutlined, 
  FileTextOutlined, 
  CheckCircleOutlined, 
  ClockCircleOutlined,
  PlusOutlined,
  EyeOutlined,
  ExperimentOutlined
} from '@ant-design/icons'
import { Link, useNavigate } from 'react-router-dom'
import { useProjectsOverview, useRecentProjects } from '../hooks/useProjects'
import { useAuth } from '../hooks/useAuth'
import styled from 'styled-components'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

const { Title, Text, Paragraph } = Typography

const DashboardContainer = styled.div`
  padding: 24px;
  background: #f5f5f5;
  min-height: calc(100vh - 64px);
`

const WelcomeCard = styled(Card)`
  margin-bottom: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  
  .ant-card-body {
    color: white;
  }
  
  .welcome-title {
    color: white !important;
    margin-bottom: 8px;
  }
  
  .welcome-text {
    color: rgba(255, 255, 255, 0.8);
  }
`

const StatsCard = styled(Card)`
  .ant-statistic-title {
    color: #666;
    font-size: 14px;
  }
  
  .ant-statistic-content {
    color: #1f2937;
  }
`

const ProjectCard = styled(Card)`
  margin-bottom: 16px;
  transition: all 0.3s ease;
  
  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
  }
  
  .project-header {
    display: flex;
    justify-content: between;
    align-items: flex-start;
    margin-bottom: 12px;
  }
  
  .project-title {
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 4px;
  }
  
  .project-meta {
    color: #666;
    font-size: 12px;
  }
`

const QuickActionCard = styled(Card)`
  text-align: center;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px dashed #d9d9d9;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #667eea;
    background: #f8f9ff;
  }
  
  .ant-card-body {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
  }
`

const Dashboard: React.FC = () => {
  const navigate = useNavigate()
  const { user } = useAuth()
  const { overview, isLoading: isLoadingOverview } = useProjectsOverview()
  const { recentProjects, isLoading: isLoadingRecent } = useRecentProjects(5)

  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return '早上好'
    if (hour < 18) return '下午好'
    return '晚上好'
  }

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'active': return 'processing'
      case 'completed': return 'success'
      case 'paused': return 'warning'
      default: return 'default'
    }
  }

  const getStatusText = (status?: string) => {
    switch (status) {
      case 'active': return '进行中'
      case 'completed': return '已完成'
      case 'paused': return '已暂停'
      default: return '草稿'
    }
  }

  return (
    <DashboardContainer>
      {/* 欢迎卡片 */}
      <WelcomeCard>
        <Row align="middle">
          <Col flex="auto">
            <Title level={2} className="welcome-title">
              {getGreeting()}，{user?.full_name || user?.username}！
            </Title>
            <Paragraph className="welcome-text">
              欢迎回到AI书稿编辑器。今天准备创作什么精彩内容呢？
            </Paragraph>
          </Col>
          <Col>
            <Button 
              type="primary" 
              size="large" 
              icon={<PlusOutlined />}
              onClick={() => navigate('/projects/new')}
              style={{ 
                background: 'rgba(255, 255, 255, 0.2)', 
                border: '1px solid rgba(255, 255, 255, 0.3)',
                backdropFilter: 'blur(10px)'
              }}
            >
              创建新项目
            </Button>
          </Col>
        </Row>
      </WelcomeCard>

      <Row gutter={[24, 24]}>
        {/* 统计数据 */}
        <Col xs={24} sm={12} md={6}>
          <StatsCard>
            <Statistic
              title="总项目数"
              value={overview?.total || 0}
              prefix={<BookOutlined />}
              loading={isLoadingOverview}
            />
          </StatsCard>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <StatsCard>
            <Statistic
              title="进行中"
              value={overview?.active || 0}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#1890ff' }}
              loading={isLoadingOverview}
            />
          </StatsCard>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <StatsCard>
            <Statistic
              title="已完成"
              value={overview?.completed || 0}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
              loading={isLoadingOverview}
            />
          </StatsCard>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <QuickActionCard onClick={() => navigate('/projects/new')}>
            <PlusOutlined style={{ fontSize: 32, color: '#667eea', marginBottom: 16 }} />
            <Title level={4} style={{ margin: 0, color: '#667eea' }}>
              创建新项目
            </Title>
            <Text type="secondary">开始您的新创作</Text>
          </QuickActionCard>
        </Col>
      </Row>

      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        {/* 最近项目 */}
        <Col xs={24} lg={16}>
          <Card 
            title="最近项目" 
            extra={<Link to="/projects">查看全部</Link>}
            loading={isLoadingRecent}
          >
            {recentProjects.length > 0 ? (
              <List
                dataSource={recentProjects}
                renderItem={(project) => (
                  <List.Item
                    actions={[
                      <Button 
                        type="text" 
                        icon={<EyeOutlined />}
                        onClick={() => navigate(`/projects/${project.id}`)}
                      >
                        查看
                      </Button>
                    ]}
                  >
                    <List.Item.Meta
                      avatar={
                        <Avatar 
                          style={{ backgroundColor: '#667eea' }}
                          icon={<BookOutlined />}
                        />
                      }
                      title={
                        <Space>
                          <Link to={`/projects/${project.id}`}>
                            {project.title}
                          </Link>
                          {project.status && (
                            <Tag color={getStatusColor(project.status)}>
                              {getStatusText(project.status)}
                            </Tag>
                          )}
                        </Space>
                      }
                      description={
                        <Space direction="vertical" size={4}>
                          {project.description && (
                            <Text type="secondary">{project.description}</Text>
                          )}
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            最后访问：{dayjs(project.last_accessed || project.updated_at).fromNow()}
                          </Text>
                        </Space>
                      }
                    />
                  </List.Item>
                )}
              />
            ) : (
              <div style={{ textAlign: 'center', padding: '40px 0' }}>
                <FileTextOutlined style={{ fontSize: 48, color: '#d9d9d9', marginBottom: 16 }} />
                <Title level={4} type="secondary">还没有项目</Title>
                <Text type="secondary">创建您的第一个项目开始创作吧</Text>
                <br />
                <Button 
                  type="primary" 
                  icon={<PlusOutlined />}
                  style={{ marginTop: 16 }}
                  onClick={() => navigate('/projects/new')}
                >
                  创建项目
                </Button>
              </div>
            )}
          </Card>
        </Col>

        {/* 快速操作 */}
        <Col xs={24} lg={8}>
          <Card title="快速操作">
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <Button 
                type="primary" 
                block 
                icon={<PlusOutlined />}
                onClick={() => navigate('/projects/new')}
              >
                创建新项目
              </Button>
              <Button 
                block 
                icon={<BookOutlined />}
                onClick={() => navigate('/projects')}
              >
                浏览所有项目
              </Button>
              <Button 
                block 
                icon={<FileTextOutlined />}
                onClick={() => navigate('/documents')}
              >
                最近文档
              </Button>
              <Button 
                block 
                icon={<ExperimentOutlined />}
                onClick={() => navigate('/latex-optimizer')}
                style={{ 
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  border: 'none'
                }}
              >
                LaTeX 书稿优化
              </Button>
            </Space>
          </Card>

          {/* 使用提示 */}
          <Card title="使用提示" style={{ marginTop: 16 }}>
            <List
              size="small"
              dataSource={[
                '使用AI优化功能提升文章质量',
                '定期保存您的创作进度',
                '利用项目分类管理不同类型的作品',
                '查看统计数据了解创作进展'
              ]}
              renderItem={(item, index) => (
                <List.Item>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {index + 1}. {item}
                  </Text>
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>
    </DashboardContainer>
  )
}

export default Dashboard