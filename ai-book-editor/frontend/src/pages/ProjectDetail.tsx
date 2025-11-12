import React, { useState, useEffect } from 'react'
import { 
  Row, 
  Col, 
  Card, 
  Button, 
  Typography, 
  Tag, 
  Space, 
  Dropdown, 
  Modal, 
  Form, 
  Input, 
  Select,
  Statistic,
  Progress,
  List,
  Avatar,
  Divider,
  Breadcrumb,
  message
} from 'antd'
import { 
  ArrowLeftOutlined,
  EditOutlined, 
  DeleteOutlined, 
  CopyOutlined,
  MoreOutlined,
  PlusOutlined,
  FileTextOutlined,
  SettingOutlined,
  BarChartOutlined,
  CalendarOutlined,
  UserOutlined,
  BookOutlined
} from '@ant-design/icons'
import { useParams, useNavigate } from 'react-router-dom'
import { useProjects, useProject, useProjectStatistics } from '../hooks/useProjects'
import { Project } from '../store/projectStore'
import styled from 'styled-components'
import dayjs from 'dayjs'

const { Title, Text, Paragraph } = Typography
const { Option } = Select
const { confirm } = Modal

const ProjectDetailContainer = styled.div`
  padding: 24px;
  background: #f5f5f5;
  min-height: calc(100vh - 64px);
`

const HeaderCard = styled(Card)`
  margin-bottom: 24px;
  
  .project-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 16px;
  }
  
  .project-info {
    flex: 1;
  }
  
  .project-actions {
    display: flex;
    gap: 8px;
  }
  
  .project-meta {
    display: flex;
    gap: 24px;
    flex-wrap: wrap;
    margin-top: 16px;
    color: #666;
  }
`

const StatsCard = styled(Card)`
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
  }
`

const DocumentCard = styled(Card)`
  .document-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid #f0f0f0;
    
    &:last-child {
      border-bottom: none;
    }
  }
  
  .document-info {
    display: flex;
    align-items: center;
    gap: 12px;
    flex: 1;
  }
  
  .document-meta {
    color: #666;
    font-size: 12px;
  }
`

interface ProjectFormData {
  title: string
  description?: string
  genre?: string
  target_audience?: string
  word_count_goal?: number
  status?: string
}

const ProjectDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [isEditModalVisible, setIsEditModalVisible] = useState(false)
  const [editForm] = Form.useForm()

  const { project, isLoading: projectLoading } = useProject(id || '')
  const { statistics: projectStats, isLoading: statsLoading } = useProjectStatistics(id || '')
  
  const {
    updateProject,
    deleteProject,
    duplicateProject,
    isUpdating,
    isDeleting,
    isDuplicating
  } = useProjects()

  const isLoading = projectLoading || statsLoading

  if (!project && !isLoading) {
    return (
      <ProjectDetailContainer>
        <Card>
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Title level={3}>项目不存在</Title>
            <Button type="primary" onClick={() => navigate('/projects')}>
              返回项目列表
            </Button>
          </div>
        </Card>
      </ProjectDetailContainer>
    )
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

  const handleEditProject = async (values: unknown) => {
    if (!project) return
    
    const projectData = values as ProjectFormData
    try {
      await updateProject(project.id.toString(), projectData)
      setIsEditModalVisible(false)
      editForm.resetFields()
    } catch (error) {
      console.error('更新项目失败:', error)
    }
  }

  const handleDeleteProject = () => {
    if (!project) return
    
    confirm({
      title: '确认删除',
      content: `确定要删除项目"${project.title}"吗？此操作不可恢复。`,
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await deleteProject(project.id.toString())
          navigate('/projects')
        } catch (error) {
          console.error('删除项目失败:', error)
        }
      }
    })
  }

  const handleDuplicateProject = () => {
    if (!project) return
    
    Modal.confirm({
      title: '复制项目',
      content: (
        <Form
          layout="vertical"
          initialValues={{
            title: `${project.title} - 副本`,
            description: project.description
          }}
          onFinish={async (values) => {
            try {
              await duplicateProject(project.id.toString(), values)
              Modal.destroyAll()
            } catch (error) {
              console.error('复制项目失败:', error)
            }
          }}
        >
          <Form.Item
            name="title"
            label="项目标题"
            rules={[{ required: true, message: '请输入项目标题' }]}
          >
            <Input placeholder="请输入项目标题" />
          </Form.Item>
          <Form.Item name="description" label="项目描述">
            <Input.TextArea placeholder="请输入项目描述" rows={3} />
          </Form.Item>
        </Form>
      ),
      okText: '复制',
      cancelText: '取消',
      width: 500
    })
  }

  const openEditModal = () => {
    if (!project) return
    
    editForm.setFieldsValue({
      title: project.title,
      description: project.description,
      genre: project.genre,
      target_audience: project.target_audience,
      word_count_goal: project.word_count_goal,
      status: project.status
    })
    setIsEditModalVisible(true)
  }

  const projectActions = [
    {
      key: 'edit',
      label: '编辑项目',
      icon: <EditOutlined />,
      onClick: openEditModal
    },
    {
      key: 'duplicate',
      label: '复制项目',
      icon: <CopyOutlined />,
      onClick: handleDuplicateProject
    },
    {
      key: 'settings',
      label: '项目设置',
      icon: <SettingOutlined />,
      onClick: () => navigate(`/projects/${id}/settings`)
    },
    {
      type: 'divider' as const
    },
    {
      key: 'delete',
      label: '删除项目',
      icon: <DeleteOutlined />,
      danger: true,
      onClick: handleDeleteProject
    }
  ]

  const calculateProgress = () => {
    if (!project?.word_count_goal || !projectStats?.total_words) {
      return 0
    }
    return Math.min((projectStats.total_words / project.word_count_goal) * 100, 100)
  }

  // 模拟文档数据
  const mockDocuments = [
    {
      id: 1,
      title: '第一章：开始',
      word_count: 2500,
      updated_at: '2024-01-15T10:30:00Z',
      status: 'draft'
    },
    {
      id: 2,
      title: '第二章：发展',
      word_count: 3200,
      updated_at: '2024-01-14T15:20:00Z',
      status: 'active'
    },
    {
      id: 3,
      title: '第三章：高潮',
      word_count: 1800,
      updated_at: '2024-01-13T09:45:00Z',
      status: 'draft'
    }
  ]

  return (
    <ProjectDetailContainer>
      <Breadcrumb style={{ marginBottom: 16 }}>
        <Breadcrumb.Item>
          <Button 
            type="link" 
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/projects')}
            style={{ padding: 0 }}
          >
            项目列表
          </Button>
        </Breadcrumb.Item>
        <Breadcrumb.Item>{project?.title || '加载中...'}</Breadcrumb.Item>
      </Breadcrumb>

      <HeaderCard loading={isLoading}>
        {project && (
          <>
            <div className="project-header">
              <div className="project-info">
                <Space align="start" size={16}>
                  <BookOutlined style={{ fontSize: 32, color: '#667eea' }} />
                  <div>
                    <Title level={2} style={{ margin: 0 }}>
                      {project.title}
                    </Title>
                    {project.status && (
                      <Tag color={getStatusColor(project.status)} style={{ marginTop: 8 }}>
                        {getStatusText(project.status)}
                      </Tag>
                    )}
                  </div>
                </Space>
              </div>
              <div className="project-actions">
                <Button 
                  type="primary" 
                  icon={<PlusOutlined />}
                  onClick={() => navigate(`/projects/${id}/documents/new`)}
                >
                  新建文档
                </Button>
                <Dropdown
                  menu={{ items: projectActions }}
                  trigger={['click']}
                >
                  <Button icon={<MoreOutlined />} />
                </Dropdown>
              </div>
            </div>

            {project.description && (
              <Paragraph style={{ fontSize: 16, color: '#666', marginBottom: 16 }}>
                {project.description}
              </Paragraph>
            )}

            <div className="project-meta">
              {project.genre && (
                <Space>
                  <BookOutlined />
                  <Text>类型: {project.genre}</Text>
                </Space>
              )}
              {project.target_audience && (
                <Space>
                  <UserOutlined />
                  <Text>目标读者: {project.target_audience}</Text>
                </Space>
              )}
              <Space>
                <CalendarOutlined />
                <Text>创建时间: {dayjs(project.created_at).format('YYYY-MM-DD')}</Text>
              </Space>
              <Space>
                <CalendarOutlined />
                <Text>更新时间: {dayjs(project.updated_at).format('YYYY-MM-DD HH:mm')}</Text>
              </Space>
            </div>
          </>
        )}
      </HeaderCard>

      <Row gutter={[24, 24]}>
        <Col xs={24} lg={16}>
          <DocumentCard 
            title="文档列表" 
            extra={
              <Button 
                type="primary" 
                size="small"
                icon={<PlusOutlined />}
                onClick={() => navigate(`/projects/${id}/documents/new`)}
              >
                新建文档
              </Button>
            }
          >
            <List
              dataSource={mockDocuments}
              renderItem={(doc) => (
                <div className="document-item">
                  <div className="document-info">
                    <Avatar icon={<FileTextOutlined />} />
                    <div>
                      <div style={{ fontWeight: 500 }}>{doc.title}</div>
                      <div className="document-meta">
                        {doc.word_count} 字 · 更新于 {dayjs(doc.updated_at).fromNow()}
                      </div>
                    </div>
                  </div>
                  <Space>
                    <Tag color={doc.status === 'active' ? 'processing' : 'default'}>
                      {doc.status === 'active' ? '编辑中' : '草稿'}
                    </Tag>
                    <Button 
                      type="link" 
                      size="small"
                      onClick={() => navigate(`/projects/${id}/documents/${doc.id}`)}
                    >
                      编辑
                    </Button>
                  </Space>
                </div>
              )}
            />
          </DocumentCard>
        </Col>

        <Col xs={24} lg={8}>
          <Space direction="vertical" size={24} style={{ width: '100%' }}>
            <StatsCard title="项目统计" extra={<BarChartOutlined />}>
              <div className="stats-grid">
                <Statistic
                  title="总字数"
                  value={projectStats?.total_words || 0}
                  suffix="字"
                />
                <Statistic
                  title="文档数量"
                  value={projectStats?.document_count || 0}
                  suffix="个"
                />
                <Statistic
                  title="完成度"
                  value={calculateProgress()}
                  precision={1}
                  suffix="%"
                />
                <Statistic
                  title="段落数量"
                  value={projectStats?.paragraph_count || 0}
                  suffix="段"
                />
              </div>
              
              {project?.word_count_goal && (
                <>
                  <Divider />
                  <div>
                    <div style={{ marginBottom: 8 }}>
                      <Text>写作进度</Text>
                      <Text style={{ float: 'right' }}>
                        {projectStats?.total_words || 0} / {project.word_count_goal} 字
                      </Text>
                    </div>
                    <Progress 
                      percent={calculateProgress()} 
                      strokeColor="#667eea"
                      showInfo={false}
                    />
                  </div>
                </>
              )}
            </StatsCard>

            <Card title="最近活动">
              <List
                size="small"
                dataSource={[
                  { action: '创建了文档', target: '第三章：高潮', time: '2小时前' },
                  { action: '更新了文档', target: '第二章：发展', time: '1天前' },
                  { action: '创建了项目', target: project?.title, time: '3天前' }
                ]}
                renderItem={(item) => (
                  <List.Item>
                    <div style={{ width: '100%' }}>
                      <div>{item.action} "{item.target}"</div>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {item.time}
                      </Text>
                    </div>
                  </List.Item>
                )}
              />
            </Card>
          </Space>
        </Col>
      </Row>

      {/* 编辑项目模态框 */}
      <Modal
        title="编辑项目"
        open={isEditModalVisible}
        onCancel={() => {
          setIsEditModalVisible(false)
          editForm.resetFields()
        }}
        footer={null}
        width={600}
      >
        <Form
          form={editForm}
          layout="vertical"
          onFinish={handleEditProject}
        >
          <Form.Item
            name="title"
            label="项目标题"
            rules={[
              { required: true, message: '请输入项目标题' },
              { max: 100, message: '标题最多100个字符' }
            ]}
          >
            <Input placeholder="请输入项目标题" />
          </Form.Item>

          <Form.Item
            name="description"
            label="项目描述"
            rules={[{ max: 500, message: '描述最多500个字符' }]}
          >
            <Input.TextArea 
              placeholder="请输入项目描述" 
              rows={3}
              showCount
              maxLength={500}
            />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="genre" label="项目类型">
                <Select placeholder="选择项目类型">
                  <Option value="novel">小说</Option>
                  <Option value="essay">散文</Option>
                  <Option value="technical">技术文档</Option>
                  <Option value="academic">学术论文</Option>
                  <Option value="other">其他</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="status" label="项目状态">
                <Select placeholder="选择项目状态">
                  <Option value="draft">草稿</Option>
                  <Option value="active">进行中</Option>
                  <Option value="paused">已暂停</Option>
                  <Option value="completed">已完成</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="word_count_goal" label="目标字数">
                <Input 
                  type="number" 
                  placeholder="目标字数"
                  addonAfter="字"
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="target_audience" label="目标读者">
                <Input placeholder="目标读者群体" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => {
                setIsEditModalVisible(false)
                editForm.resetFields()
              }}>
                取消
              </Button>
              <Button 
                type="primary" 
                htmlType="submit"
                loading={isUpdating}
              >
                保存
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </ProjectDetailContainer>
  )
}

export default ProjectDetail