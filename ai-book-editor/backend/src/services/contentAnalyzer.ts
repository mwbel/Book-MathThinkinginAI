export interface DuplicateContent {
  id: string;
  text: string;
  similarity: number;
  locations: Array<{
    sectionId: string;
    sectionTitle: string;
    file: string;
    startIndex: number;
    endIndex: number;
  }>;
}

export interface LogicIssue {
  id: string;
  type: 'logic_jump' | 'missing_transition' | 'redundant_content' | 'inconsistent_style';
  severity: 'low' | 'medium' | 'high';
  description: string;
  location: {
    sectionId: string;
    sectionTitle: string;
    file: string;
    paragraph: number;
  };
  suggestion: string;
}

export interface ContentAnalysisResult {
  duplicates: DuplicateContent[];
  logicIssues: LogicIssue[];
  statistics: {
    totalSections: number;
    totalParagraphs: number;
    totalWords: number;
    duplicateRate: number;
    averageSectionLength: number;
  };
}

export class ContentAnalyzer {
  private readonly SIMILARITY_THRESHOLD = 0.8;
  private readonly MIN_DUPLICATE_LENGTH = 50;

  /**
   * 分析内容重复和逻辑问题
   */
  async analyzeContent(sections: any[]): Promise<ContentAnalysisResult> {
    const duplicates = await this.findDuplicateContent(sections);
    const logicIssues = await this.analyzeLogicIssues(sections);
    const statistics = this.calculateStatistics(sections, duplicates);

    return {
      duplicates,
      logicIssues,
      statistics
    };
  }

  /**
   * 查找重复内容
   */
  private async findDuplicateContent(sections: any[]): Promise<DuplicateContent[]> {
    const duplicates: DuplicateContent[] = [];
    const paragraphs: Array<{
      text: string;
      sectionId: string;
      sectionTitle: string;
      file: string;
      index: number;
    }> = [];

    // 提取所有段落
    sections.forEach(section => {
      const sectionParagraphs = this.extractParagraphs(section.content);
      sectionParagraphs.forEach((paragraph, index) => {
        if (paragraph.length >= this.MIN_DUPLICATE_LENGTH) {
          paragraphs.push({
            text: paragraph,
            sectionId: section.id,
            sectionTitle: section.title,
            file: section.file,
            index
          });
        }
      });
    });

    // 比较段落相似性
    for (let i = 0; i < paragraphs.length; i++) {
      for (let j = i + 1; j < paragraphs.length; j++) {
        const similarity = this.calculateSimilarity(paragraphs[i].text, paragraphs[j].text);
        
        if (similarity >= this.SIMILARITY_THRESHOLD) {
          const duplicateId = `duplicate-${i}-${j}`;
          
          duplicates.push({
            id: duplicateId,
            text: paragraphs[i].text,
            similarity,
            locations: [
              {
                sectionId: paragraphs[i].sectionId,
                sectionTitle: paragraphs[i].sectionTitle,
                file: paragraphs[i].file,
                startIndex: paragraphs[i].index,
                endIndex: paragraphs[i].index
              },
              {
                sectionId: paragraphs[j].sectionId,
                sectionTitle: paragraphs[j].sectionTitle,
                file: paragraphs[j].file,
                startIndex: paragraphs[j].index,
                endIndex: paragraphs[j].index
              }
            ]
          });
        }
      }
    }

    return duplicates;
  }

  /**
   * 分析逻辑问题
   */
  private async analyzeLogicIssues(sections: any[]): Promise<LogicIssue[]> {
    const issues: LogicIssue[] = [];

    for (let i = 0; i < sections.length; i++) {
      const section = sections[i];
      const paragraphs = this.extractParagraphs(section.content);

      // 检查段落间的逻辑连贯性
      for (let j = 0; j < paragraphs.length - 1; j++) {
        const currentParagraph = paragraphs[j];
        const nextParagraph = paragraphs[j + 1];

        // 检查逻辑跳跃
        if (this.hasLogicJump(currentParagraph, nextParagraph)) {
          issues.push({
            id: `logic-jump-${section.id}-${j}`,
            type: 'logic_jump',
            severity: 'medium',
            description: '段落间存在逻辑跳跃，缺少过渡',
            location: {
              sectionId: section.id,
              sectionTitle: section.title,
              file: section.file,
              paragraph: j
            },
            suggestion: '建议添加过渡句或重新组织段落顺序'
          });
        }

        // 检查缺少承上启下
        if (this.missingTransition(currentParagraph, nextParagraph)) {
          issues.push({
            id: `missing-transition-${section.id}-${j}`,
            type: 'missing_transition',
            severity: 'low',
            description: '段落间缺少承上启下的连接',
            location: {
              sectionId: section.id,
              sectionTitle: section.title,
              file: section.file,
              paragraph: j
            },
            suggestion: '建议添加过渡词或连接句'
          });
        }
      }

      // 检查冗余内容
      const redundantParagraphs = this.findRedundantContent(paragraphs);
      redundantParagraphs.forEach(paragraphIndex => {
        issues.push({
          id: `redundant-${section.id}-${paragraphIndex}`,
          type: 'redundant_content',
          severity: 'medium',
          description: '段落内容冗余，可以精简',
          location: {
            sectionId: section.id,
            sectionTitle: section.title,
            file: section.file,
            paragraph: paragraphIndex
          },
          suggestion: '建议删除重复信息或合并相似内容'
        });
      });
    }

    return issues;
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
   * 计算文本相似性（简化版本）
   */
  private calculateSimilarity(text1: string, text2: string): number {
    const words1 = new Set(text1.toLowerCase().split(/\s+/));
    const words2 = new Set(text2.toLowerCase().split(/\s+/));
    
    const intersection = new Set([...words1].filter(x => words2.has(x)));
    const union = new Set([...words1, ...words2]);
    
    return intersection.size / union.size;
  }

  /**
   * 检查逻辑跳跃
   */
  private hasLogicJump(paragraph1: string, paragraph2: string): boolean {
    // 简化的逻辑跳跃检测
    const transitionWords = ['因此', '所以', '然而', '但是', '另外', '此外', '同时', '接下来', '首先', '其次', '最后'];
    const hasTransition = transitionWords.some(word => 
      paragraph2.includes(word) || paragraph1.includes(word)
    );
    
    // 如果段落很短且没有过渡词，可能存在逻辑跳跃
    return paragraph1.length > 100 && paragraph2.length > 100 && !hasTransition;
  }

  /**
   * 检查缺少过渡
   */
  private missingTransition(paragraph1: string, paragraph2: string): boolean {
    // 检查是否缺少承上启下的连接
    const connectiveWords = ['这', '这样', '因此', '所以', '基于此', '在此基础上'];
    return !connectiveWords.some(word => paragraph2.startsWith(word));
  }

  /**
   * 查找冗余内容
   */
  private findRedundantContent(paragraphs: string[]): number[] {
    const redundant: number[] = [];
    
    for (let i = 0; i < paragraphs.length; i++) {
      const paragraph = paragraphs[i];
      
      // 检查是否包含重复的短语
      const sentences = paragraph.split(/[。！？]/);
      const uniqueSentences = new Set(sentences.map(s => s.trim()));
      
      if (sentences.length > uniqueSentences.size * 1.5) {
        redundant.push(i);
      }
    }
    
    return redundant;
  }

  /**
   * 计算统计信息
   */
  private calculateStatistics(sections: any[], duplicates: DuplicateContent[]) {
    const totalSections = sections.length;
    let totalParagraphs = 0;
    let totalWords = 0;

    sections.forEach(section => {
      const paragraphs = this.extractParagraphs(section.content);
      totalParagraphs += paragraphs.length;
      totalWords += section.content.split(/\s+/).length;
    });

    const duplicateRate = duplicates.length / totalParagraphs;
    const averageSectionLength = totalWords / totalSections;

    return {
      totalSections,
      totalParagraphs,
      totalWords,
      duplicateRate,
      averageSectionLength
    };
  }
}