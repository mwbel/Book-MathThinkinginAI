import { DuplicateContent, LogicIssue } from './contentAnalyzer';

export interface OptimizationSuggestion {
  id: string;
  type: 'remove_duplicate' | 'merge_content' | 'add_transition' | 'restructure' | 'simplify';
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  originalText: string;
  suggestedText: string;
  location: {
    sectionId: string;
    sectionTitle: string;
    file: string;
    startLine?: number;
    endLine?: number;
  };
  impact: {
    wordsRemoved: number;
    readabilityImprovement: number;
    logicImprovement: number;
  };
}

export interface OptimizationResult {
  suggestions: OptimizationSuggestion[];
  summary: {
    totalSuggestions: number;
    potentialWordReduction: number;
    estimatedImprovementScore: number;
  };
}

export class OptimizationEngine {
  /**
   * 生成优化建议
   */
  async generateOptimizations(
    sections: any[],
    duplicates: DuplicateContent[],
    logicIssues: LogicIssue[]
  ): Promise<OptimizationResult> {
    const suggestions: OptimizationSuggestion[] = [];

    // 处理重复内容
    for (const duplicate of duplicates) {
      const duplicateSuggestions = this.handleDuplicateContent(duplicate, sections);
      suggestions.push(...duplicateSuggestions);
    }

    // 处理逻辑问题
    for (const issue of logicIssues) {
      const logicSuggestions = this.handleLogicIssue(issue, sections);
      suggestions.push(...logicSuggestions);
    }

    // 生成结构优化建议
    const structureSuggestions = this.generateStructureOptimizations(sections);
    suggestions.push(...structureSuggestions);

    const summary = this.calculateOptimizationSummary(suggestions);

    return {
      suggestions: suggestions.sort((a, b) => this.getPriorityWeight(b.priority) - this.getPriorityWeight(a.priority)),
      summary
    };
  }

  /**
   * 处理重复内容
   */
  private handleDuplicateContent(duplicate: DuplicateContent, sections: any[]): OptimizationSuggestion[] {
    const suggestions: OptimizationSuggestion[] = [];

    if (duplicate.locations.length === 2) {
      const [loc1, loc2] = duplicate.locations;
      
      // 建议删除重复段落
      suggestions.push({
        id: `remove-duplicate-${duplicate.id}`,
        type: 'remove_duplicate',
        priority: 'high',
        title: '删除重复段落',
        description: `在"${loc1.sectionTitle}"和"${loc2.sectionTitle}"中发现相似度${(duplicate.similarity * 100).toFixed(1)}%的重复内容`,
        originalText: duplicate.text,
        suggestedText: '',
        location: {
          sectionId: loc2.sectionId,
          sectionTitle: loc2.sectionTitle,
          file: loc2.file
        },
        impact: {
          wordsRemoved: duplicate.text.split(/\s+/).length,
          readabilityImprovement: 0.8,
          logicImprovement: 0.6
        }
      });

      // 如果内容有细微差异，建议合并
      if (duplicate.similarity < 0.95) {
        suggestions.push({
          id: `merge-content-${duplicate.id}`,
          type: 'merge_content',
          priority: 'medium',
          title: '合并相似内容',
          description: '将两处相似内容合并为一个更完整的段落',
          originalText: duplicate.text,
          suggestedText: this.generateMergedContent(duplicate, sections),
          location: {
            sectionId: loc1.sectionId,
            sectionTitle: loc1.sectionTitle,
            file: loc1.file
          },
          impact: {
            wordsRemoved: Math.floor(duplicate.text.split(/\s+/).length * 0.3),
            readabilityImprovement: 0.7,
            logicImprovement: 0.8
          }
        });
      }
    }

    return suggestions;
  }

  /**
   * 处理逻辑问题
   */
  private handleLogicIssue(issue: LogicIssue, sections: any[]): OptimizationSuggestion[] {
    const suggestions: OptimizationSuggestion[] = [];
    const section = sections.find(s => s.id === issue.location.sectionId);
    
    if (!section) return suggestions;

    const paragraphs = this.extractParagraphs(section.content);
    const targetParagraph = paragraphs[issue.location.paragraph];

    switch (issue.type) {
      case 'logic_jump':
        suggestions.push({
          id: `fix-logic-jump-${issue.id}`,
          type: 'add_transition',
          priority: 'medium',
          title: '添加过渡句',
          description: issue.description,
          originalText: targetParagraph,
          suggestedText: this.generateTransitionText(targetParagraph, paragraphs[issue.location.paragraph + 1]),
          location: {
            sectionId: issue.location.sectionId,
            sectionTitle: issue.location.sectionTitle,
            file: issue.location.file
          },
          impact: {
            wordsRemoved: 0,
            readabilityImprovement: 0.6,
            logicImprovement: 0.9
          }
        });
        break;

      case 'missing_transition':
        suggestions.push({
          id: `add-transition-${issue.id}`,
          type: 'add_transition',
          priority: 'low',
          title: '改善段落连接',
          description: issue.description,
          originalText: targetParagraph,
          suggestedText: this.addTransitionWords(targetParagraph),
          location: {
            sectionId: issue.location.sectionId,
            sectionTitle: issue.location.sectionTitle,
            file: issue.location.file
          },
          impact: {
            wordsRemoved: 0,
            readabilityImprovement: 0.4,
            logicImprovement: 0.5
          }
        });
        break;

      case 'redundant_content':
        suggestions.push({
          id: `simplify-${issue.id}`,
          type: 'simplify',
          priority: 'medium',
          title: '精简冗余内容',
          description: issue.description,
          originalText: targetParagraph,
          suggestedText: this.simplifyContent(targetParagraph),
          location: {
            sectionId: issue.location.sectionId,
            sectionTitle: issue.location.sectionTitle,
            file: issue.location.file
          },
          impact: {
            wordsRemoved: Math.floor(targetParagraph.split(/\s+/).length * 0.2),
            readabilityImprovement: 0.7,
            logicImprovement: 0.6
          }
        });
        break;
    }

    return suggestions;
  }

  /**
   * 生成结构优化建议
   */
  private generateStructureOptimizations(sections: any[]): OptimizationSuggestion[] {
    const suggestions: OptimizationSuggestion[] = [];

    // 检查章节长度平衡
    const avgLength = sections.reduce((sum, s) => sum + s.content.length, 0) / sections.length;
    
    sections.forEach(section => {
      if (section.content.length > avgLength * 2) {
        suggestions.push({
          id: `restructure-${section.id}`,
          type: 'restructure',
          priority: 'low',
          title: '考虑拆分长章节',
          description: `章节"${section.title}"内容较长，建议考虑拆分为多个小节`,
          originalText: section.content.substring(0, 200) + '...',
          suggestedText: '建议将此章节拆分为2-3个小节，每个小节专注于一个主要概念',
          location: {
            sectionId: section.id,
            sectionTitle: section.title,
            file: section.file
          },
          impact: {
            wordsRemoved: 0,
            readabilityImprovement: 0.5,
            logicImprovement: 0.7
          }
        });
      }
    });

    return suggestions;
  }

  /**
   * 生成合并内容
   */
  private generateMergedContent(duplicate: DuplicateContent, sections: any[]): string {
    // 简化版本：返回第一个位置的内容加上改进建议
    return duplicate.text + '\n\n[建议：将两处相似内容的独特信息合并到此处]';
  }

  /**
   * 生成过渡文本
   */
  private generateTransitionText(currentParagraph: string, nextParagraph: string): string {
    const transitionPhrases = [
      '基于以上分析，',
      '在此基础上，',
      '进一步来看，',
      '接下来我们探讨',
      '由此可见，'
    ];
    
    const randomTransition = transitionPhrases[Math.floor(Math.random() * transitionPhrases.length)];
    return currentParagraph + '\n\n' + randomTransition + nextParagraph;
  }

  /**
   * 添加过渡词
   */
  private addTransitionWords(paragraph: string): string {
    const transitionWords = ['因此，', '同时，', '另外，', '此外，'];
    const randomWord = transitionWords[Math.floor(Math.random() * transitionWords.length)];
    return randomWord + paragraph;
  }

  /**
   * 精简内容
   */
  private simplifyContent(content: string): string {
    // 简化版本：移除一些冗余词汇
    return content
      .replace(/非常/g, '')
      .replace(/十分/g, '')
      .replace(/极其/g, '')
      .replace(/相当/g, '')
      .replace(/\s+/g, ' ')
      .trim();
  }

  /**
   * 提取段落
   */
  private extractParagraphs(content: string): string[] {
    return content
      .split(/\n\s*\n/)
      .map(p => p.trim())
      .filter(p => p.length > 0);
  }

  /**
   * 获取优先级权重
   */
  private getPriorityWeight(priority: string): number {
    switch (priority) {
      case 'high': return 3;
      case 'medium': return 2;
      case 'low': return 1;
      default: return 0;
    }
  }

  /**
   * 计算优化摘要
   */
  private calculateOptimizationSummary(suggestions: OptimizationSuggestion[]) {
    const totalSuggestions = suggestions.length;
    const potentialWordReduction = suggestions.reduce((sum, s) => sum + s.impact.wordsRemoved, 0);
    const estimatedImprovementScore = suggestions.reduce((sum, s) => 
      sum + (s.impact.readabilityImprovement + s.impact.logicImprovement) / 2, 0
    ) / totalSuggestions;

    return {
      totalSuggestions,
      potentialWordReduction,
      estimatedImprovementScore
    };
  }
}