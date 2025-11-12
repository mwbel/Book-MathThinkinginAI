import React, { useState } from 'react'
import { 
  Row, 
  Col, 
  Card, 
  Button, 
  Input, 
  Select, 
  Table, 
  Tag, 
  Space, 
  Dropdown, 
  Modal, 
  Form, 
  message,
  Typography,
  Pagination
} from 'antd'
import { 
  PlusOutlined, 
  SearchOutlined, 
  MoreOutlined, 
  EditOutlined, 
  DeleteOutlined, 
  CopyOutlined,
  EyeOutlined,
  BookOutlined
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { useProjects } from '../hooks/useProjects'
import { Project } from '../store/projectStore'
import { ProjectCreateRequest, ProjectUpdateRequest } from '../services/projectService'
import styled from 'styled-components'
import dayjs from 'dayjs'

const { Title } = Typography
const { Option } = Select
const { confirm } = Modal

const ProjectsContainer = styled.div`
  padding: 24px;
  background: #f5f5f5;
  min-height: calc(100vh - 64px);
`

const HeaderCard = styled(Card)`
  margin-bottom: 24px;
  
  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
  }
  
  .filters {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    align-items: center;
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
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
  }
  
  .project-title {
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 4px;
    cursor: pointer;
    
    &:hover {
      color: #667eea;
    }
  }
  
  .project-meta {
    color: #666;
    font-size: 12px;
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
  }
`

interface ProjectFormData {
  title: string
  description?: string
  genre?: string
  target_audience?: string
  word_count_goal?: number
}

const Projects: React.FC = () => {
  const navigate = useNavigate()
  const [searchText, setSearchText] = useState('')
  const [selectedGenre, setSelectedGenre] = useState<string>()
  const [selectedStatus, setSelectedStatus] = useState<string>()
  const [sortBy, setSortBy] = useState('updated_at')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [viewMode, setViewMode] = useState<'card' | 'table'>('card')
  
  // 模态框状态
  const [isCreateModalVisible, setIsCreateModalVisible] = useState(false)
  const [isEditModalVisible, setIsEditModalVisible] = useState(false)
  const [editingProject, setEditingProject] = useState<Project | null>(null)
  
  const [createForm] = Form.useForm()
  const [editForm] = Form.useForm()

  const {
    projects,
    pagination,
    isLoading,
    createProject,
    updateProject,
    deleteProject,
    duplicateProject,
    isCreating,
    isUpdating,
    isDeleting,
    isDuplicating
  } = useProjects({
    page: currentPage,
    size: pageSize,
    search: searchText,
    genre: selectedGenre,
    status: selectedStatus,
    sort_by: sortBy,
    sort_order: sortOrder
  })

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

  const handleCreateProject = async (values: unknown) => {
    const projectData = values as ProjectFormData
    try {
      await createProject(projectData)
      setIsCreateModalVisible(false)
      createForm.resetFields()
    } catch (error) {
      console.error('创建项目失败:', error)
    }
  }

  const handleEditProject = async (values: unknown) => {
    if (!editingProject) return
    
    const projectData = values as ProjectFormData
    try {
      await updateProject(editingProject.id.toString(), projectData)
      setIsEditModalVisible(false)
      setEditingProject(null)
      editForm.resetFields()
    } catch (error) {
      console.error('更新项目失败:', error)
    }
  }

  const handleDeleteProject = (project: Project) => {
    confirm({
      title: '确认删除',
      content: `确定要删除项目"${project.title}"吗？此操作不可恢复。`,
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await deleteProject(project.id.toString())
        } catch (error) {
          console.error('删除项目失败:', error)
        }
      }
    })
  }

  const handleDuplicateProject = (project: Project) => {
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

  const openEditModal = (project: Project) => {
    setEditingProject(project)
    editForm.setFieldsValue({
      title: project.title,
      description: project.description,
      genre: project.genre,
      target_audience: project.target_audience,
      word_count_goal: project.word_count_goal
    })
    setIsEditModalVisible(true)
  }

  const getProjectActions = (project: Project) => [
    {
      key: 'view',
      label: '查看详情',
      icon: <EyeOutlined />,
      onClick: () => navigate(`/projects/${project.id}`)
    },
    {
      key: 'edit',
      label: '编辑',
      icon: <EditOutlined />,
      onClick: () => openEditModal(project)
    },
    {
      key: 'duplicate',
      label: '复制',
      icon: <CopyOutlined />,
      onClick: () => handleDuplicateProject(project)
    },
    {
      key: 'delete',
      label: '删除',
      icon: <DeleteOutlined />,
      danger: true,
      onClick: () => handleDeleteProject(project)
    }
  ]

  const tableColumns = [
    {
      title: '项目名称',
      dataIndex: 'title',
      key: 'title',
      render: (title: string, record: Project) => (
        <Button 
          type="link" 
          onClick={() => navigate(`/projects/${record.id}`)}
          style={{ padding: 0, height: 'auto' }}
        >
          {title}
        </Button>
      )
    },
    {
      title: '类型',
      dataIndex: 'genre',
      key: 'genre',
      render: (genre: string) => genre || '-'
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>
          {getStatusText(status)}
        </Tag>
      )
    },
    {
      title: '目标字数',
      dataIndex: 'word_count_goal',
      key: 'word_count_goal',
      render: (count: number) => count ? `${count.toLocaleString()} 字` : '-'
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm')
    },
    {
      title: '操作',
      key: 'actions',
      render: (_: unknown, record: Project) => (
        <Dropdown
          menu={{ items: getProjectActions(record) }}
          trigger={['click']}
        >
          <Button type="text" icon={<MoreOutlined />} />
        </Dropdown>
      )
    }
  ]

  return (
    <ProjectsContainer>
      <HeaderCard>
        <div className="header-content">
          <div>
            <Title level={2} style={{ margin: 0 }}>
              我的项目
            </Title>
          </div>
          <div className="filters">
            <Input
              placeholder="搜索项目..."
              prefix={<SearchOutlined />}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              style={{ width: 200 }}
              allowClear
            />
            <Select
              placeholder="选择类型"
              value={selectedGenre}
              onChange={setSelectedGenre}
              style={{ width: 120 }}
              allowClear
            >
              <Option value="novel">小说</Option>
              <Option value="essay">散文</Option>
              <Option value="technical">技术文档</Option>
              <Option value="academic">学术论文</Option>
              <Option value="other">其他</Option>
            </Select>
            <Select
              placeholder="选择状态"
              value={selectedStatus}
              onChange={setSelectedStatus}
              style={{ width: 120 }}
              allowClear
            >
              <Option value="draft">草稿</Option>
              <Option value="active">进行中</Option>
              <Option value="paused">已暂停</Option>
              <Option value="completed">已完成</Option>
            </Select>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setIsCreateModalVisible(true)}
            >
              创建项目
            </Button>
          </div>
        </div>
      </HeaderCard>

      {viewMode === 'card' ? (
        <Row gutter={[16, 16]}>
          {projects.map((project) => (
            <Col xs={24} sm={12} lg={8} xl={6} key={project.id}>
              <ProjectCard
                actions={[
                  <Button 
                    type="text" 
                    icon={<EyeOutlined />}
                    onClick={() => navigate(`/projects/${project.id}`)}
                  >
                    查看
                  </Button>,
                  <Dropdown
                    menu={{ items: getProjectActions(project) }}
                    trigger={['click']}
                  >
                    <Button type="text" icon={<MoreOutlined />} />
                  </Dropdown>
                ]}
              >
                <div className="project-header">
                  <BookOutlined style={{ fontSize: 24, color: '#667eea' }} />
                  {project.status && (
                    <Tag color={getStatusColor(project.status)}>
                      {getStatusText(project.status)}
                    </Tag>
                  )}
                </div>
                <div 
                  className="project-title"
                  onClick={() => navigate(`/projects/${project.id}`)}
                >
                  {project.title}
                </div>
                {project.description && (
                  <p style={{ 
                    color: '#666', 
                    fontSize: 14, 
                    marginBottom: 12,
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden'
                  }}>
                    {project.description}
                  </p>
                )}
                <div className="project-meta">
                  {project.genre && <span>类型: {project.genre}</span>}
                  {project.word_count_goal && (
                    <span>目标: {project.word_count_goal.toLocaleString()}字</span>
                  )}
                  <span>更新: {dayjs(project.updated_at).fromNow()}</span>
                </div>
              </ProjectCard>
            </Col>
          ))}
        </Row>
      ) : (
        <Card>
          <Table
            columns={tableColumns}
            dataSource={projects}
            rowKey="id"
            loading={isLoading}
            pagination={false}
          />
        </Card>
      )}

      {pagination && (
        <div style={{ textAlign: 'center', marginTop: 24 }}>
          <Pagination
            current={pagination.current}
            pageSize={pagination.pageSize}
            total={pagination.total}
            showSizeChanger
            showQuickJumper
            showTotal={(total, range) => 
              `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
            }
            onChange={(page, size) => {
              setCurrentPage(page)
              setPageSize(size || 10)
            }}
          />
        </div>
      )}

      {/* 创建项目模态框 */}
      <Modal
        title="创建新项目"
        open={isCreateModalVisible}
        onCancel={() => {
          setIsCreateModalVisible(false)
          createForm.resetFields()
        }}
        footer={null}
        width={600}
      >
        <Form
          form={createForm}
          layout="vertical"
          onFinish={handleCreateProject}
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
              <Form.Item name="word_count_goal" label="目标字数">
                <Input 
                  type="number" 
                  placeholder="目标字数"
                  addonAfter="字"
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="target_audience" label="目标读者">
            <Input placeholder="目标读者群体" />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => {
                setIsCreateModalVisible(false)
                createForm.resetFields()
              }}>
                取消
              </Button>
              <Button 
                type="primary" 
                htmlType="submit"
                loading={isCreating}
              >
                创建
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 编辑项目模态框 */}
      <Modal
        title="编辑项目"
        open={isEditModalVisible}
        onCancel={() => {
          setIsEditModalVisible(false)
          setEditingProject(null)
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
              <Form.Item name="word_count_goal" label="目标字数">
                <Input 
                  type="number" 
                  placeholder="目标字数"
                  addonAfter="字"
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="target_audience" label="目标读者">
            <Input placeholder="目标读者群体" />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => {
                setIsEditModalVisible(false)
                setEditingProject(null)
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
    </ProjectsContainer>
  )
}

export default Projects