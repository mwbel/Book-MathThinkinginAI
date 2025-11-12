import React, { useState, useEffect } from 'react';
import {
  Layout,
  Card,
  Button,
  Tree,
  Tabs,
  List,
  Typography,
  Progress,
  Tag,
  Space,
  Alert,
  Divider,
  Tooltip,
  Modal,
  Input,
  Row,
  Col,
  Statistic,
  Badge,
  Collapse,
  Upload,
  message
} from 'antd';
import {
  FileTextOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  DeleteOutlined,
  EditOutlined,
  EyeOutlined,
  DownloadOutlined,
  SyncOutlined,
  BugOutlined,
  BookOutlined,
  BarChartOutlined,
  UploadOutlined
} from '@ant-design/icons';
import styled from 'styled-components';
import { latexService, LaTeXSection, OptimizationSuggestion, AnalysisResult } from '../services/latexService';

const { Content, Sider } = Layout;
const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;
const { Panel } = Collapse;

// 样式组件
const StyledLayout = styled(Layout)`
  min-height: 100vh;
  background: #f5f5f5;
`;

const StyledSider = styled(Sider)`
  background: white;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
`;

const StyledContent = styled(Content)`
  padding: 24px;
  margin-left: 8px;
`;

interface OptimizationCardProps {
  priority?: 'high' | 'medium' | 'low';
}

interface StatisticsCardProps {
  color?: string;
}

const OptimizationCard = styled(Card)<OptimizationCardProps>`
  margin-bottom: 16px;
  border-left: 4px solid ${props => 
    props.priority === 'high' ? '#ff4d4f' : 
    props.priority === 'medium' ? '#faad14' : '#52c41a'
  };
`;

const StatisticsCard = styled(Card)<StatisticsCardProps>`
  text-align: center;
  .ant-statistic-content {
    color: ${props => props.color || '#1890ff'};
  }
`;

// 接口定义已从 latexService 导入

const LaTeXOptimizer: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [sections, setSections] = useState<LaTeXSection[]>([]);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [selectedSection, setSelectedSection] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedSuggestion, setSelectedSuggestion] = useState<OptimizationSuggestion | null>(null);

  // 加载LaTeX项目
  useEffect(() => {
    loadLaTeXProject();
  }, []);

  const loadLaTeXProject = async () => {
    setLoading(true);
    try {
      // 加载LaTeX项目文件
      const projectPath = '/Users/Min369/Desktop/书/书稿打磨/ai-book-editor/draft-tex';
      const result = await latexService.loadProjectFromDirectory(projectPath);
      
      setSections(result.sections);
      setAnalysisResult(result.analysis);
    } catch (error) {
      console.error('Failed to load LaTeX project:', error);
    } finally {
      setLoading(false);
    }
  };

  const runAnalysis = async () => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 3000));
      // 重新分析
      await loadLaTeXProject();
    } finally {
      setLoading(false);
    }
  };

  const applySuggestion = (suggestion: OptimizationSuggestion) => {
    Modal.confirm({
      title: '应用优化建议',
      content: `确定要应用"${suggestion.title}"的建议吗？此操作将修改原文件。`,
      onOk: async () => {
        try {
          const success = await latexService.applySuggestion(suggestion.id, suggestion.location.sectionId);
          if (success) {
            message.success('优化建议已成功应用');
            // 重新加载项目以显示更新后的内容
            await loadLaTeXProject();
          } else {
            message.error('应用建议失败');
          }
        } catch (error) {
          console.error('Failed to apply suggestion:', error);
          message.error('应用建议时发生错误');
        }
      }
    });
  };

  const viewSuggestionDetail = (suggestion: OptimizationSuggestion) => {
    setSelectedSuggestion(suggestion);
    setModalVisible(true);
  };

  const handleFileUpload = async (file: File) => {
    setLoading(true);
    try {
      const result = await latexService.uploadFile(file);
      setSections(result.sections);
      setAnalysisResult(result.analysis);
      message.success('文件上传并分析成功！');
    } catch (error) {
      console.error('Upload error:', error);
      message.error('文件上传时发生错误，使用默认项目数据');
      // 如果上传失败，加载默认项目
      await loadLaTeXProject();
    } finally {
      setLoading(false);
    }
  };

  // 构建章节树数据
  const treeData = sections.map(section => ({
    title: section.title,
    key: section.id,
    icon: <BookOutlined />,
    children: []
  }));

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'red';
      case 'medium': return 'orange';
      case 'low': return 'green';
      default: return 'blue';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'remove_duplicate': return <DeleteOutlined />;
      case 'add_transition': return <EditOutlined />;
      case 'merge_content': return <SyncOutlined />;
      default: return <BugOutlined />;
    }
  };

  return (
    <StyledLayout>
      <StyledSider width={300} collapsible>
        <div style={{ padding: '16px' }}>
          <Title level={4}>
            <FileTextOutlined /> LaTeX 书稿优化器
          </Title>
          
          <Upload
            accept=".tex,.zip"
            showUploadList={false}
            beforeUpload={(file) => {
              handleFileUpload(file);
              return false; // 阻止默认上传行为
            }}
            style={{ marginBottom: '16px' }}
          >
            <Button 
              type="primary" 
              block 
              loading={loading}
              icon={<UploadOutlined />}
              style={{ marginBottom: '8px' }}
            >
              上传LaTeX文件
            </Button>
          </Upload>
          
          <Button 
            type="default" 
            block 
            loading={loading}
            onClick={runAnalysis}
            style={{ marginBottom: '16px' }}
          >
            <SyncOutlined /> 重新分析
          </Button>
        </div>
        
        <div style={{ padding: '0 16px' }}>
          <Title level={5}>章节导航</Title>
          <Tree
            treeData={treeData}
            selectedKeys={selectedSection ? [selectedSection] : []}
            onSelect={(keys) => setSelectedSection(keys[0] as string)}
            showIcon
          />
        </div>
      </StyledSider>

      <StyledContent>
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane tab="概览" key="overview">
            {analysisResult && (
              <Row gutter={[16, 16]}>
                <Col span={6}>
                  <StatisticsCard>
                    <Statistic
                      title="总章节数"
                      value={analysisResult.statistics.totalSections}
                      prefix={<BookOutlined />}
                    />
                  </StatisticsCard>
                </Col>
                <Col span={6}>
                  <StatisticsCard>
                    <Statistic
                      title="总字数"
                      value={analysisResult.statistics.totalWords}
                      prefix={<FileTextOutlined />}
                    />
                  </StatisticsCard>
                </Col>
                <Col span={6}>
                  <StatisticsCard color="#ff4d4f">
                    <Statistic
                      title="重复率"
                      value={analysisResult.statistics.duplicateRate * 100}
                      precision={1}
                      suffix="%"
                      prefix={<ExclamationCircleOutlined />}
                    />
                  </StatisticsCard>
                </Col>
                <Col span={6}>
                  <StatisticsCard color="#52c41a">
                    <Statistic
                      title="优化建议"
                      value={analysisResult.suggestions.length}
                      prefix={<CheckCircleOutlined />}
                    />
                  </StatisticsCard>
                </Col>
              </Row>
            )}

            <Card title="分析进度" style={{ marginTop: '16px' }}>
              <Progress 
                percent={loading ? 50 : 100} 
                status={loading ? 'active' : 'success'}
                strokeColor={{
                  '0%': '#108ee9',
                  '100%': '#87d068',
                }}
              />
              <Text type="secondary">
                {loading ? '正在分析LaTeX文件...' : '分析完成'}
              </Text>
            </Card>
          </TabPane>

          <TabPane tab={`优化建议 ${analysisResult?.suggestions.length || 0}`} key="suggestions">
            {analysisResult?.suggestions.map(suggestion => (
              <OptimizationCard
                key={suggestion.id}
                priority={suggestion.priority}
                title={
                  <Space>
                    {getTypeIcon(suggestion.type)}
                    {suggestion.title}
                    <Tag color={getPriorityColor(suggestion.priority)}>
                      {suggestion.priority}
                    </Tag>
                  </Space>
                }
                extra={
                  <Space>
                    <Tooltip title="查看详情">
                      <Button 
                        icon={<EyeOutlined />} 
                        onClick={() => viewSuggestionDetail(suggestion)}
                      />
                    </Tooltip>
                    <Tooltip title="应用建议">
                      <Button 
                        type="primary" 
                        icon={<CheckCircleOutlined />}
                        onClick={() => applySuggestion(suggestion)}
                      />
                    </Tooltip>
                  </Space>
                }
              >
                <Paragraph>{suggestion.description}</Paragraph>
                <Text type="secondary">
                  位置: {suggestion.location.sectionTitle} ({suggestion.location.file})
                </Text>
                <Divider />
                <Row gutter={16}>
                  <Col span={8}>
                    <Statistic
                      title="减少字数"
                      value={suggestion.impact.wordsRemoved}
                      suffix="字"
                    />
                  </Col>
                  <Col span={8}>
                    <Statistic
                      title="可读性提升"
                      value={suggestion.impact.readabilityImprovement * 100}
                      precision={0}
                      suffix="%"
                    />
                  </Col>
                  <Col span={8}>
                    <Statistic
                      title="逻辑改善"
                      value={suggestion.impact.logicImprovement * 100}
                      precision={0}
                      suffix="%"
                    />
                  </Col>
                </Row>
              </OptimizationCard>
            ))}
          </TabPane>

          <TabPane tab="重复内容" key="duplicates">
            {analysisResult?.duplicates.map((duplicate, index) => (
              <Card key={index} style={{ marginBottom: '16px' }}>
                <Badge.Ribbon text={`相似度 ${(duplicate.similarity * 100).toFixed(1)}%`} color="red">
                  <Title level={5}>重复内容 #{index + 1}</Title>
                  <Collapse>
                    <Panel header="查看重复位置" key="1">
                      <List
                        dataSource={duplicate.locations}
                        renderItem={(location: any) => (
                          <List.Item>
                            <Text strong>{location.sectionTitle}</Text>
                            <Text type="secondary"> - {location.file}</Text>
                          </List.Item>
                        )}
                      />
                    </Panel>
                  </Collapse>
                </Badge.Ribbon>
              </Card>
            ))}
          </TabPane>

          <TabPane tab="统计报告" key="statistics">
            {analysisResult && (
              <Card title={<><BarChartOutlined /> 详细统计</> }>
                <Row gutter={[16, 16]}>
                  <Col span={12}>
                    <Card type="inner" title="内容统计">
                      <Statistic
                        title="总段落数"
                        value={analysisResult.statistics.totalParagraphs}
                        style={{ marginBottom: '16px' }}
                      />
                      <Statistic
                        title="平均章节长度"
                        value={analysisResult.statistics.averageSectionLength}
                        suffix="字"
                      />
                    </Card>
                  </Col>
                  <Col span={12}>
                    <Card type="inner" title="质量指标">
                      <Statistic
                        title="重复内容数量"
                        value={analysisResult.duplicates.length}
                        style={{ marginBottom: '16px' }}
                      />
                      <Statistic
                        title="逻辑问题数量"
                        value={analysisResult.logicIssues.length}
                      />
                    </Card>
                  </Col>
                </Row>
              </Card>
            )}
          </TabPane>
        </Tabs>

        {/* 建议详情模态框 */}
        <Modal
          title="优化建议详情"
          visible={modalVisible}
          onCancel={() => setModalVisible(false)}
          width={800}
          footer={[
            <Button key="cancel" onClick={() => setModalVisible(false)}>
              取消
            </Button>,
            <Button 
              key="apply" 
              type="primary" 
              onClick={() => {
                if (selectedSuggestion) {
                  applySuggestion(selectedSuggestion);
                  setModalVisible(false);
                }
              }}
            >
              应用建议
            </Button>
          ]}
        >
          {selectedSuggestion && (
            <div>
              <Title level={4}>{selectedSuggestion.title}</Title>
              <Paragraph>{selectedSuggestion.description}</Paragraph>
              
              <Divider />
              
              <Title level={5}>原文内容</Title>
              <Card>
                <Text>{selectedSuggestion.originalText}</Text>
              </Card>
              
              {selectedSuggestion.suggestedText && (
                <>
                  <Title level={5} style={{ marginTop: '16px' }}>建议修改</Title>
                  <Card style={{ backgroundColor: '#f6ffed', border: '1px solid #b7eb8f' }}>
                    <Text>{selectedSuggestion.suggestedText}</Text>
                  </Card>
                </>
              )}
              
              <Divider />
              
              <Title level={5}>影响评估</Title>
              <Row gutter={16}>
                <Col span={8}>
                  <Statistic
                    title="减少字数"
                    value={selectedSuggestion.impact.wordsRemoved}
                    suffix="字"
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="可读性提升"
                    value={selectedSuggestion.impact.readabilityImprovement * 100}
                    precision={0}
                    suffix="%"
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="逻辑改善"
                    value={selectedSuggestion.impact.logicImprovement * 100}
                    precision={0}
                    suffix="%"
                  />
                </Col>
              </Row>
            </div>
          )}
        </Modal>
      </StyledContent>
    </StyledLayout>
  );
};

export default LaTeXOptimizer;