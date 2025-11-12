import { OptimizationSuggestion } from './optimizationEngine';

// AI模型配置接口
interface AIModelConfig {
  provider: 'openai' | 'anthropic' | 'local';
  model: string;
  apiKey?: string;
  baseUrl?: string;
  maxTokens?: number;
  temperature?: number;
}

// AI分析结果接口
interface AIAnalysisResult {
  suggestions: OptimizationSuggestion[];
  confidence: number;
  reasoning: string;
  alternatives?: string[];
}

// 文本优化请求接口
interface OptimizationRequest {
  originalText: string;
  context: {
    sectionTitle: string;
    chapterTitle: string;
    previousParagraph?: string;
    nextParagraph?: string;
  };
  optimizationType: 'remove_duplicate' | 'add_transition' | 'improve_logic' | 'reduce_redundancy' | 'enhance_flow';
  preserveLatex: boolean;
}

// AI优化响应接口
interface OptimizationResponse {
  optimizedText: string;
  changes: {
    type: string;
    description: string;
    impact: {
      wordsChanged: number;
      readabilityImprovement: number;
      logicImprovement: number;
    };
  }[];
  confidence: number;
  explanation: string;
}

class AIService {
  private config: AIModelConfig;
  private rateLimitDelay: number = 1000; // 1秒延迟避免频率限制

  constructor(config: AIModelConfig) {
    this.config = config;
  }

  /**
   * 分析文本并生成优化建议
   */
  async analyzeText(
    text: string,
    context: {
      sectionTitle: string;
      chapterTitle: string;
      documentType: 'academic' | 'technical' | 'general';
    }
  ): Promise<AIAnalysisResult> {
    try {
      const prompt = this.buildAnalysisPrompt(text, context);
      const response = await this.callAIModel(prompt);
      
      return this.parseAnalysisResponse(response);
    } catch (error) {
      console.error('AI analysis failed:', error);
      throw new Error('AI分析失败，请稍后重试');
    }
  }

  /**
   * 优化文本内容
   */
  async optimizeText(request: OptimizationRequest): Promise<OptimizationResponse> {
    try {
      const prompt = this.buildOptimizationPrompt(request);
      const response = await this.callAIModel(prompt);
      
      return this.parseOptimizationResponse(response);
    } catch (error) {
      console.error('Text optimization failed:', error);
      throw new Error('文本优化失败，请稍后重试');
    }
  }

  /**
   * 检查重复内容
   */
  async detectDuplicates(
    texts: string[],
    threshold: number = 0.8
  ): Promise<{
    duplicates: Array<{
      indices: number[];
      similarity: number;
      suggestedAction: string;
    }>;
  }> {
    try {
      const prompt = this.buildDuplicateDetectionPrompt(texts, threshold);
      const response = await this.callAIModel(prompt);
      
      return this.parseDuplicateResponse(response);
    } catch (error) {
      console.error('Duplicate detection failed:', error);
      throw new Error('重复内容检测失败，请稍后重试');
    }
  }

  /**
   * 分析逻辑连贯性
   */
  async analyzeLogicFlow(
    paragraphs: string[],
    context: { sectionTitle: string; chapterTitle: string }
  ): Promise<{
    issues: Array<{
      position: number;
      type: 'logic_jump' | 'missing_transition' | 'redundant_info';
      severity: 'high' | 'medium' | 'low';
      description: string;
      suggestion: string;
    }>;
  }> {
    try {
      const prompt = this.buildLogicAnalysisPrompt(paragraphs, context);
      const response = await this.callAIModel(prompt);
      
      return this.parseLogicResponse(response);
    } catch (error) {
      console.error('Logic analysis failed:', error);
      throw new Error('逻辑分析失败，请稍后重试');
    }
  }

  /**
   * 构建分析提示词
   */
  private buildAnalysisPrompt(
    text: string,
    context: {
      sectionTitle: string;
      chapterTitle: string;
      documentType: 'academic' | 'technical' | 'general';
    }
  ): string {
    return `
作为一名专业的中文学术写作编辑，请分析以下LaTeX文档片段的质量并提供优化建议。

文档信息：
- 章节标题：${context.chapterTitle}
- 小节标题：${context.sectionTitle}
- 文档类型：${context.documentType}

待分析文本：
${text}

请从以下角度进行分析：
1. 语言表达的清晰度和准确性
2. 逻辑结构的连贯性
3. 内容的冗余程度
4. 段落间的过渡是否自然
5. 是否存在重复表述

请以JSON格式返回分析结果，包含：
- suggestions: 具体的优化建议数组
- confidence: 分析置信度(0-1)
- reasoning: 分析理由
- alternatives: 可选的改进方案

注意：请保持LaTeX命令和格式不变。
`;
  }

  /**
   * 构建优化提示词
   */
  private buildOptimizationPrompt(request: OptimizationRequest): string {
    const typeDescriptions = {
      remove_duplicate: '删除重复内容',
      add_transition: '添加过渡句',
      improve_logic: '改善逻辑结构',
      reduce_redundancy: '减少冗余表述',
      enhance_flow: '增强文本流畅性'
    };

    return `
作为专业的中文学术写作编辑，请对以下文本进行"${typeDescriptions[request.optimizationType]}"优化。

上下文信息：
- 章节：${request.context.chapterTitle}
- 小节：${request.context.sectionTitle}
${request.context.previousParagraph ? `- 前一段：${request.context.previousParagraph}` : ''}
${request.context.nextParagraph ? `- 后一段：${request.context.nextParagraph}` : ''}

原文：
${request.originalText}

优化要求：
1. ${request.preserveLatex ? '严格保持LaTeX命令和格式不变' : '可以调整格式'}
2. 保持原文的核心信息和观点
3. 提升文本的可读性和逻辑性
4. 使用自然流畅的中文表达

请以JSON格式返回优化结果，包含：
- optimizedText: 优化后的文本
- changes: 具体修改说明
- confidence: 优化置信度
- explanation: 优化说明
`;
  }

  /**
   * 构建重复检测提示词
   */
  private buildDuplicateDetectionPrompt(texts: string[], threshold: number): string {
    return `
请分析以下文本片段，识别相似度超过${threshold * 100}%的重复内容。

文本片段：
${texts.map((text, index) => `[${index}] ${text}`).join('\n\n')}

请以JSON格式返回检测结果，包含：
- duplicates: 重复内容数组，每项包含indices(索引数组)、similarity(相似度)、suggestedAction(建议操作)

注意：
1. 考虑语义相似性，不仅仅是字面重复
2. 忽略LaTeX命令的差异
3. 提供具体的处理建议
`;
  }

  /**
   * 构建逻辑分析提示词
   */
  private buildLogicAnalysisPrompt(
    paragraphs: string[],
    context: { sectionTitle: string; chapterTitle: string }
  ): string {
    return `
请分析以下段落序列的逻辑连贯性，识别逻辑跳跃、缺失过渡和冗余信息。

章节信息：
- 章节：${context.chapterTitle}
- 小节：${context.sectionTitle}

段落序列：
${paragraphs.map((p, index) => `[${index}] ${p}`).join('\n\n')}

请以JSON格式返回分析结果，包含：
- issues: 问题数组，每项包含position(位置)、type(类型)、severity(严重程度)、description(描述)、suggestion(建议)

分析重点：
1. 段落间的逻辑关系是否清晰
2. 是否存在突兀的话题转换
3. 是否缺少必要的过渡句
4. 是否有重复或冗余的信息
`;
  }

  /**
   * 调用AI模型
   */
  private async callAIModel(prompt: string): Promise<string> {
    // 添加延迟避免频率限制
    await new Promise(resolve => setTimeout(resolve, this.rateLimitDelay));

    switch (this.config.provider) {
      case 'openai':
        return this.callOpenAI(prompt);
      case 'anthropic':
        return this.callAnthropic(prompt);
      case 'local':
        return this.callLocalModel(prompt);
      default:
        throw new Error(`不支持的AI提供商: ${this.config.provider}`);
    }
  }

  /**
   * 调用OpenAI API
   */
  private async callOpenAI(prompt: string): Promise<string> {
    // 模拟API调用 - 实际实现需要使用OpenAI SDK
    console.log('Calling OpenAI with prompt:', prompt.substring(0, 100) + '...');
    
    // 模拟响应
    return JSON.stringify({
      suggestions: [
        {
          type: 'improve_clarity',
          description: '建议简化复杂句式，提高可读性',
          confidence: 0.85
        }
      ],
      confidence: 0.8,
      reasoning: '文本整体结构清晰，但部分句式较为复杂'
    });
  }

  /**
   * 调用Anthropic Claude API
   */
  private async callAnthropic(prompt: string): Promise<string> {
    // 模拟API调用 - 实际实现需要使用Anthropic SDK
    console.log('Calling Anthropic with prompt:', prompt.substring(0, 100) + '...');
    
    // 模拟响应
    return JSON.stringify({
      suggestions: [
        {
          type: 'enhance_transition',
          description: '建议在段落间添加过渡句',
          confidence: 0.9
        }
      ],
      confidence: 0.85,
      reasoning: '段落间的逻辑连接可以进一步加强'
    });
  }

  /**
   * 调用本地模型
   */
  private async callLocalModel(prompt: string): Promise<string> {
    // 模拟本地模型调用
    console.log('Calling local model with prompt:', prompt.substring(0, 100) + '...');
    
    // 模拟响应
    return JSON.stringify({
      suggestions: [
        {
          type: 'reduce_redundancy',
          description: '发现重复表述，建议合并或删除',
          confidence: 0.75
        }
      ],
      confidence: 0.7,
      reasoning: '基于本地模型的分析结果'
    });
  }

  /**
   * 解析分析响应
   */
  private parseAnalysisResponse(response: string): AIAnalysisResult {
    try {
      const parsed = JSON.parse(response);
      return {
        suggestions: parsed.suggestions || [],
        confidence: parsed.confidence || 0.5,
        reasoning: parsed.reasoning || '无详细分析',
        alternatives: parsed.alternatives || []
      };
    } catch (error) {
      console.error('Failed to parse AI response:', error);
      return {
        suggestions: [],
        confidence: 0,
        reasoning: '解析AI响应失败',
        alternatives: []
      };
    }
  }

  /**
   * 解析优化响应
   */
  private parseOptimizationResponse(response: string): OptimizationResponse {
    try {
      const parsed = JSON.parse(response);
      return {
        optimizedText: parsed.optimizedText || '',
        changes: parsed.changes || [],
        confidence: parsed.confidence || 0.5,
        explanation: parsed.explanation || '无详细说明'
      };
    } catch (error) {
      console.error('Failed to parse optimization response:', error);
      return {
        optimizedText: '',
        changes: [],
        confidence: 0,
        explanation: '解析优化响应失败'
      };
    }
  }

  /**
   * 解析重复检测响应
   */
  private parseDuplicateResponse(response: string) {
    try {
      return JSON.parse(response);
    } catch (error) {
      console.error('Failed to parse duplicate response:', error);
      return { duplicates: [] };
    }
  }

  /**
   * 解析逻辑分析响应
   */
  private parseLogicResponse(response: string) {
    try {
      return JSON.parse(response);
    } catch (error) {
      console.error('Failed to parse logic response:', error);
      return { issues: [] };
    }
  }

  /**
   * 设置频率限制延迟
   */
  setRateLimitDelay(delay: number) {
    this.rateLimitDelay = delay;
  }

  /**
   * 更新配置
   */
  updateConfig(config: Partial<AIModelConfig>) {
    this.config = { ...this.config, ...config };
  }
}

// 创建AI服务实例的工厂函数
export function createAIService(config: AIModelConfig): AIService {
  return new AIService(config);
}

// 默认配置
export const defaultAIConfig: AIModelConfig = {
  provider: 'openai',
  model: 'gpt-4',
  maxTokens: 2000,
  temperature: 0.3
};

export { AIService, AIModelConfig, AIAnalysisResult, OptimizationRequest, OptimizationResponse };