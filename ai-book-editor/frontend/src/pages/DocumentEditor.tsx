import React, { useState, useEffect } from 'react'
import { 
  Row, 
  Col, 
  Card, 
  Button, 
  Typography, 
  Input, 
  Space, 
  Dropdown, 
  Modal, 
  Form, 
  Select,
  Statistic,
  Breadcrumb,
  message,
  Divider,
  Tooltip,
  Progress
} from 'antd'
import { 
  ArrowLeftOutlined,
  SaveOutlined,
  MoreOutlined,
  SettingOutlined,
  DownloadOutlined,
  ShareAltOutlined,
  EyeOutlined,
  EditOutlined,
  BulbOutlined,
  CheckOutlined,
  ClockCircleOutlined,
  FileTextOutlined
} from '@ant-design/icons'
import { useParams, useNavigate } from 'react-router-dom'
import styled from 'styled-components'
import dayjs from 'dayjs'

const { Title, Text } = Typography
const { TextArea } = Input
const { Option } = Select

const EditorContainer = styled.div`
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
`

const EditorHeader = styled.div`
  background: white;
  padding: 12px 24px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  
  .header-right {
    display: flex;
    align-items: center;
    gap: 8px;
  }
`

const EditorContent = styled.div`
  flex: 1;
  display: flex;
  overflow: hidden;
`

const MainEditor = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  margin: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`

const EditorToolbar = styled.div`
  padding: 16px 24px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  .toolbar-left {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  
  .toolbar-right {
    display: flex;
    align-items: center;
    gap: 8px;
  }
`

const EditorTextArea = styled(TextArea)`
  flex: 1;
  border: none !important;
  box-shadow: none !important;
  resize: none;
  padding: 24px;
  font-size: 16px;
  line-height: 1.8;
  
  &:focus {
    box-shadow: none !important;
  }
`

const SidePanel = styled.div`
  width: 320px;
  background: white;
  margin: 24px 24px 24px 0;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
`

const StatusBar = styled.div`
  background: white;
  padding: 8px 24px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #666;
`

interface Document {
  id: number
  title: string
  content: string
  word_count: number
  created_at: string
  updated_at: string
  project_id: number
}

const DocumentEditor: React.FC = () => {
  const { projectId, documentId } = useParams<{ projectId: string; documentId: string }>()
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [lastSaved, setLastSaved] = useState<Date | null>(null)
  const [wordCount, setWordCount] = useState(0)
  const [characterCount, setCharacterCount] = useState(0)
  const [isOptimizing, setIsOptimizing] = useState(false)
  
  // 文档数据
  const [document, setDocument] = useState<Document>({
    id: parseInt(documentId || '1'),
    title: '第一章：开始',
    content: '这里是文档内容...\n\n请开始您的创作。',
    word_count: 0,
    created_at: '2024-01-15T10:30:00Z',
    updated_at: '2024-01-15T10:30:00Z',
    project_id: parseInt(projectId || '1')
  })

  const [title, setTitle] = useState(document.title)
  const [content, setContent] = useState(document.content)

  useEffect(() => {
    // 计算字数和字符数
    const words = content.trim().split(/\s+/).filter(word => word.length > 0).length
    const characters = content.length
    setWordCount(words)
    setCharacterCount(characters)
  }, [content])

  const handleSave = async () => {
    setIsSaving(true)
    try {
      // 模拟保存
      await new Promise(resolve => setTimeout(resolve, 1000))
      setLastSaved(new Date())
      message.success('保存成功')
    } catch (error) {
      message.error('保存失败')
    } finally {
      setIsSaving(false)
    }
  }

  const handleOptimize = async () => {
    setIsOptimizing(true)
    try {
      // 模拟AI优化
      await new Promise(resolve => setTimeout(resolve, 2000))
      message.success('AI优化建议已生成')
    } catch (error) {
      message.error('优化失败')
    } finally {
      setIsOptimizing(false)
    }
  }

  const documentActions = [
    {
      key: 'preview',
      label: '预览',
      icon: <EyeOutlined />
    },
    {
      key: 'export',
      label: '导出',
      icon: <DownloadOutlined />
    },
    {
      key: 'share',
      label: '分享',
      icon: <ShareAltOutlined />
    },
    {
      type: 'divider' as const
    },
    {
      key: 'settings',
      label: '设置',
      icon: <SettingOutlined />
    }
  ]

  return (
    <EditorContainer>
      <EditorHeader>
        <div className="header-left">
          <Button 
            type="text" 
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate(`/projects/${projectId}`)}
          >
            返回项目
          </Button>
          <Divider type="vertical" />
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            variant="borderless"
            style={{ fontSize: 16, fontWeight: 500 }}
            placeholder="文档标题"
          />
        </div>
        <div className="header-right">
          <Button 
            type="primary" 
            icon={<SaveOutlined />}
            loading={isSaving}
            onClick={handleSave}
          >
            保存
          </Button>
          <Dropdown
            menu={{ items: documentActions }}
            trigger={['click']}
          >
            <Button icon={<MoreOutlined />} />
          </Dropdown>
        </div>
      </EditorHeader>

      <EditorContent>
        <MainEditor>
          <EditorToolbar>
            <div className="toolbar-left">
              <Space>
                <FileTextOutlined style={{ color: '#667eea' }} />
                <Text strong>正在编辑</Text>
              </Space>
            </div>
            <div className="toolbar-right">
              <Button 
                type="primary" 
                ghost
                icon={<BulbOutlined />}
                loading={isOptimizing}
                onClick={handleOptimize}
              >
                AI优化建议
              </Button>
            </div>
          </EditorToolbar>
          
          <EditorTextArea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="开始您的创作..."
            autoSize={false}
          />
        </MainEditor>

        <SidePanel>
          <Card title="文档统计" size="small">
            <Row gutter={16}>
              <Col span={12}>
                <Statistic
                  title="字数"
                  value={wordCount}
                  suffix="字"
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="字符数"
                  value={characterCount}
                  suffix="个"
                />
              </Col>
            </Row>
            <Divider />
            <div>
              <Text type="secondary">创建时间</Text>
              <br />
              <Text>{dayjs(document.created_at).format('YYYY-MM-DD HH:mm')}</Text>
            </div>
            <div style={{ marginTop: 8 }}>
              <Text type="secondary">最后修改</Text>
              <br />
              <Text>{dayjs(document.updated_at).format('YYYY-MM-DD HH:mm')}</Text>
            </div>
          </Card>

          <Card title="AI优化" size="small" style={{ marginTop: 16 }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>优化建议</Text>
                <div style={{ marginTop: 8 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <Text type="secondary">语法检查</Text>
                    <CheckOutlined style={{ color: '#52c41a' }} />
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <Text type="secondary">风格优化</Text>
                    <ClockCircleOutlined style={{ color: '#faad14' }} />
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <Text type="secondary">内容增强</Text>
                    <ClockCircleOutlined style={{ color: '#faad14' }} />
                  </div>
                </div>
              </div>
              
              <Button 
                type="primary" 
                block
                icon={<BulbOutlined />}
                loading={isOptimizing}
                onClick={handleOptimize}
              >
                获取AI建议
              </Button>
            </Space>
          </Card>

          <Card title="版本历史" size="small" style={{ marginTop: 16 }}>
            <div style={{ fontSize: 12, color: '#666' }}>
              <div style={{ marginBottom: 8 }}>
                <div>版本 1.2</div>
                <div>2小时前</div>
              </div>
              <div style={{ marginBottom: 8 }}>
                <div>版本 1.1</div>
                <div>1天前</div>
              </div>
              <div>
                <div>版本 1.0</div>
                <div>3天前</div>
              </div>
            </div>
          </Card>
        </SidePanel>
      </EditorContent>

      <StatusBar>
        <div>
          <Space size={24}>
            <span>行 1, 列 1</span>
            <span>{wordCount} 字</span>
            <span>{characterCount} 字符</span>
          </Space>
        </div>
        <div>
          {lastSaved ? (
            <span>最后保存: {dayjs(lastSaved).format('HH:mm:ss')}</span>
          ) : (
            <span>未保存</span>
          )}
        </div>
      </StatusBar>
    </EditorContainer>
  )
}

export default DocumentEditor