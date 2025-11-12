// LaTeX文件处理服务
export interface LaTeXSection {
  id: string;
  type: 'chapter' | 'section' | 'subsection';
  title: string;
  content: string;
  file: string;
  children?: LaTeXSection[];
}

export interface OptimizationSuggestion {
  id: string;
  type: string;
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  originalText: string;
  suggestedText: string;
  location: {
    sectionId: string;
    sectionTitle: string;
    file: string;
  };
  impact: {
    wordsRemoved: number;
    readabilityImprovement: number;
    logicImprovement: number;
  };
}

export interface AnalysisResult {
  duplicates: any[];
  logicIssues: any[];
  statistics: {
    totalSections: number;
    totalParagraphs: number;
    totalWords: number;
    duplicateRate: number;
    averageSectionLength: number;
  };
  suggestions: OptimizationSuggestion[];
}

class LaTeXService {
  private baseUrl = 'http://localhost:8000/api'; // 假设后端API地址

  /**
   * 加载LaTeX项目
   */
  async loadProjectFromDirectory(directoryPath: string): Promise<{
    sections: LaTeXSection[];
    analysis: AnalysisResult;
  }> {
    try {
      console.log('Loading LaTeX project from:', directoryPath);
      
      // 尝试调用后端API
      try {
        const response = await fetch(`${this.baseUrl}/latex/analyze-directory`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ directory_path: directoryPath }),
        });
        
        if (response.ok) {
          const data = await response.json();
          return {
            sections: data.sections,
            analysis: data.analysis
          };
        } else {
          console.warn('Backend API not available, using mock data');
        }
      } catch (apiError) {
        console.warn('Backend API not available, using mock data:', apiError);
      }
      
      // 如果API不可用，使用模拟数据
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // 模拟从指定目录读取的LaTeX文件数据
      const sections: LaTeXSection[] = [
        {
          id: 'chapter-1',
          type: 'chapter',
          title: '引言 什么是智能？',
          content: `这一章将带领你从哲学、科学和工程的角度出发，追问"什么是智能"这个根本问题。

智能并非人类独有，许多动物，如海豚、鸟类、猩猩，甚至章鱼，都表现出高度的学习能力、问题解决能力和适应性。然而，人类智能的独特之处在于其抽象思维、语言表达、创造性和自我反思的能力。

从计算的角度来看，智能可以被理解为一种信息处理能力，它涉及感知、学习、推理、决策和行动。这种能力使得智能体能够在复杂和不确定的环境中实现目标。

人工智能的发展历程可以追溯到20世纪50年代，当时科学家们开始探索如何让机器模拟人类的智能行为。从早期的符号主义方法到现代的深度学习，AI经历了多次起伏和突破。`,
          file: '1-Def.tex'
        },
        {
          id: 'chapter-2',
          type: 'chapter',
          title: '机器学习：学习如何学习？',
          content: `机器学习是对能通过经验自动改进的计算机算法的研究。它是人工智能的一个重要分支，专注于让计算机系统能够从数据中学习模式和规律。

传统的编程方法需要程序员明确指定每一个步骤和规则，而机器学习则允许计算机通过分析大量数据来自动发现这些规则。这种方法在处理复杂问题时显示出巨大的优势。

智能并非人类独有，许多动物都表现出学习能力。类似地，机器学习试图赋予计算机这种学习能力，使其能够在没有明确编程的情况下改进性能。

机器学习的发展经历了从简单的线性模型到复杂的神经网络的演进过程。每一次技术突破都为解决更复杂的问题提供了新的可能性。`,
          file: '5-ML.v2.tex'
        },
        {
          id: 'chapter-3',
          type: 'chapter',
          title: '深度学习，真的行',
          content: `深度学习作为机器学习的一个重要分支，通过构建具有多个隐藏层的神经网络来模拟人脑的信息处理方式。

深度学习的核心思想是通过层次化的特征学习来理解数据。每一层都能学习到不同层次的特征表示，从低级的边缘和纹理到高级的语义概念。

这种方法在图像识别、自然语言处理、语音识别等领域取得了突破性进展，甚至在某些任务上超越了人类的表现。

然而，深度学习也面临着一些挑战，包括对大量数据的依赖、计算资源的需求、模型的可解释性等问题。`,
          file: '7-DL.tex'
        }
      ];

      // 模拟分析结果
      const analysis: AnalysisResult = {
        duplicates: [
          {
            id: 'dup-1',
            similarity: 0.85,
            text1: '智能并非人类独有，许多动物，如海豚、鸟类、猩猩，甚至章鱼，都表现出高度的学习能力',
            text2: '智能并非人类独有，许多动物都表现出学习能力',
            locations: [
              { sectionTitle: '引言 什么是智能？', file: '1-Def.tex', paragraph: 2 },
              { sectionTitle: '机器学习：学习如何学习？', file: '5-ML.v2.tex', paragraph: 3 }
            ]
          }
        ],
        logicIssues: [
          {
            id: 'logic-1',
            type: 'logic_jump',
            severity: 'medium',
            description: '从智能定义直接跳转到AI发展历程，缺少过渡',
            location: { sectionTitle: '引言 什么是智能？', file: '1-Def.tex', paragraph: 4 }
          },
          {
            id: 'logic-2',
            type: 'missing_transition',
            severity: 'low',
            description: '段落间缺少逻辑连接',
            location: { sectionTitle: '深度学习，真的行', file: '7-DL.tex', paragraph: 2 }
          }
        ],
        statistics: {
          totalSections: 3,
          totalParagraphs: 12,
          totalWords: 1250,
          duplicateRate: 0.12,
          averageSectionLength: 417
        },
        suggestions: [
          {
            id: 'sugg-1',
            type: 'remove_duplicate',
            priority: 'high',
            title: '删除重复段落',
            description: '在"引言"和"机器学习"章节中发现85%相似的重复内容，建议保留更详细的版本并删除简化版本',
            originalText: '智能并非人类独有，许多动物都表现出学习能力。',
            suggestedText: '',
            location: {
              sectionId: 'chapter-2',
              sectionTitle: '机器学习：学习如何学习？',
              file: '5-ML.v2.tex'
            },
            impact: {
              wordsRemoved: 23,
              readabilityImprovement: 0.8,
              logicImprovement: 0.6
            }
          },
          {
            id: 'sugg-2',
            type: 'add_transition',
            priority: 'medium',
            title: '添加过渡句',
            description: '在智能定义和AI发展历程之间添加过渡句，增强逻辑连贯性',
            originalText: '人工智能的发展历程可以追溯到20世纪50年代...',
            suggestedText: '基于对智能本质的理解，人工智能的发展历程可以追溯到20世纪50年代...',
            location: {
              sectionId: 'chapter-1',
              sectionTitle: '引言 什么是智能？',
              file: '1-Def.tex'
            },
            impact: {
              wordsRemoved: 0,
              readabilityImprovement: 0.6,
              logicImprovement: 0.9
            }
          },
          {
            id: 'sugg-3',
            type: 'improve_flow',
            priority: 'medium',
            title: '改善段落流畅性',
            description: '调整深度学习章节的段落顺序，使论述更加流畅',
            originalText: '深度学习作为机器学习的一个重要分支...',
            suggestedText: '深度学习作为机器学习领域的重要突破...',
            location: {
              sectionId: 'chapter-3',
              sectionTitle: '深度学习，真的行',
              file: '7-DL.tex'
            },
            impact: {
              wordsRemoved: 0,
              readabilityImprovement: 0.7,
              logicImprovement: 0.5
            }
          },
          {
            id: 'sugg-4',
            type: 'reduce_redundancy',
            priority: 'low',
            title: '减少冗余表述',
            description: '简化部分重复的概念表述，提高文本密度',
            originalText: '这种方法在处理复杂问题时显示出巨大的优势。',
            suggestedText: '这种方法在复杂问题处理上优势明显。',
            location: {
              sectionId: 'chapter-2',
              sectionTitle: '机器学习：学习如何学习？',
              file: '5-ML.v2.tex'
            },
            impact: {
              wordsRemoved: 8,
              readabilityImprovement: 0.4,
              logicImprovement: 0.2
            }
          }
        ]
      };

      return { sections, analysis };
    } catch (error) {
      console.error('Failed to load LaTeX project:', error);
      throw new Error('加载LaTeX项目失败');
    }
  }

  /**
   * 分析特定章节
   */
  async analyzeSection(sectionId: string): Promise<{
    duplicates: any[];
    logicIssues: any[];
    suggestions: OptimizationSuggestion[];
  }> {
    // 模拟章节分析
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    return {
      duplicates: [],
      logicIssues: [],
      suggestions: []
    };
  }

  /**
   * 应用优化建议
   */
  async applySuggestion(suggestionId: string, sectionId: string): Promise<boolean> {
    try {
      console.log('Applying suggestion:', suggestionId, 'to section:', sectionId);
      
      // 尝试调用后端API
      try {
        const response = await fetch(`${this.baseUrl}/latex/apply-suggestion`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            suggestion_id: suggestionId, 
            section_id: sectionId 
          }),
        });
        
        if (response.ok) {
          const data = await response.json();
          return data.success;
        } else {
          console.warn('Backend API not available, using mock response');
        }
      } catch (apiError) {
        console.warn('Backend API not available, using mock response:', apiError);
      }
      
      // 如果API不可用，使用模拟响应
      await new Promise(resolve => setTimeout(resolve, 1000));
      return Math.random() > 0.1; // 90%成功率
    } catch (error) {
      console.error('Error applying suggestion:', error);
      return false;
    }
  }

  /**
   * 获取文件内容（模拟）
   */
  async getFileContent(filename: string): Promise<string> {
    // 模拟文件内容
    const mockContents: { [key: string]: string } = {
      '1-Def.tex': `\\chapter{引言 什么是智能？}

这一章将带领你从哲学、科学和工程的角度出发，追问"什么是智能"这个根本问题。

智能并非人类独有，许多动物，如海豚、鸟类、猩猩，甚至章鱼，都表现出高度的学习能力、问题解决能力和适应性。然而，人类智能的独特之处在于其抽象思维、语言表达、创造性和自我反思的能力。

从计算的角度来看，智能可以被理解为一种信息处理能力，它涉及感知、学习、推理、决策和行动。这种能力使得智能体能够在复杂和不确定的环境中实现目标。

人工智能的发展历程可以追溯到20世纪50年代，当时科学家们开始探索如何让机器模拟人类的智能行为。从早期的符号主义方法到现代的深度学习，AI经历了多次起伏和突破。`,
      
      '5-ML.v2.tex': `\\chapter{机器学习：学习如何学习？}

机器学习是对能通过经验自动改进的计算机算法的研究。它是人工智能的一个重要分支，专注于让计算机系统能够从数据中学习模式和规律。

传统的编程方法需要程序员明确指定每一个步骤和规则，而机器学习则允许计算机通过分析大量数据来自动发现这些规则。这种方法在处理复杂问题时显示出巨大的优势。

智能并非人类独有，许多动物都表现出学习能力。类似地，机器学习试图赋予计算机这种学习能力，使其能够在没有明确编程的情况下改进性能。

机器学习的发展经历了从简单的线性模型到复杂的神经网络的演进过程。每一次技术突破都为解决更复杂的问题提供了新的可能性。`,
      
      '7-DL.tex': `\\chapter{深度学习，真的行}

深度学习作为机器学习的一个重要分支，通过构建具有多个隐藏层的神经网络来模拟人脑的信息处理方式。

深度学习的核心思想是通过层次化的特征学习来理解数据。每一层都能学习到不同层次的特征表示，从低级的边缘和纹理到高级的语义概念。

这种方法在图像识别、自然语言处理、语音识别等领域取得了突破性进展，甚至在某些任务上超越了人类的表现。

然而，深度学习也面临着一些挑战，包括对大量数据的依赖、计算资源的需求、模型的可解释性等问题。`
    };

    await new Promise(resolve => setTimeout(resolve, 500));
    return mockContents[filename] || '文件未找到';
  }

  /**
   * 上传LaTeX文件
   */
  async uploadFile(file: File): Promise<{
    sections: LaTeXSection[];
    analysis: AnalysisResult;
  }> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${this.baseUrl}/latex/upload`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        return {
          sections: data.sections,
          analysis: data.analysis
        };
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      throw error;
    }
  }

  /**
   * 导出优化后的文件
   */
  async exportOptimizedFiles(): Promise<Blob> {
    // 模拟导出功能
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const content = '优化后的LaTeX文件内容...';
    return new Blob([content], { type: 'text/plain' });
  }
}

// 创建服务实例
export const latexService = new LaTeXService();

export default LaTeXService;