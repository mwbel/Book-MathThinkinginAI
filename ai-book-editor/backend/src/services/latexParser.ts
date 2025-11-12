import * as fs from 'fs';
import * as path from 'path';

export interface LaTeXSection {
  id: string;
  type: 'chapter' | 'section' | 'subsection' | 'subsubsection';
  title: string;
  content: string;
  startLine: number;
  endLine: number;
  file: string;
  children?: LaTeXSection[];
}

export interface LaTeXDocument {
  mainFile: string;
  title: string;
  author: string;
  sections: LaTeXSection[];
  includedFiles: string[];
}

export class LaTeXParser {
  private basePath: string;

  constructor(basePath: string) {
    this.basePath = basePath;
  }

  /**
   * 解析主LaTeX文件
   */
  async parseMainDocument(mainFilePath: string): Promise<LaTeXDocument> {
    const fullPath = path.join(this.basePath, mainFilePath);
    const content = await fs.promises.readFile(fullPath, 'utf-8');
    
    const document: LaTeXDocument = {
      mainFile: mainFilePath,
      title: this.extractTitle(content),
      author: this.extractAuthor(content),
      sections: [],
      includedFiles: this.extractIncludedFiles(content)
    };

    // 解析包含的文件
    for (const includedFile of document.includedFiles) {
      try {
        const sections = await this.parseIncludedFile(includedFile);
        document.sections.push(...sections);
      } catch (error) {
        console.warn(`Failed to parse included file: ${includedFile}`, error);
      }
    }

    return document;
  }

  /**
   * 解析包含的文件
   */
  private async parseIncludedFile(fileName: string): Promise<LaTeXSection[]> {
    const filePath = path.join(this.basePath, `${fileName}.tex`);
    
    if (!fs.existsSync(filePath)) {
      console.warn(`File not found: ${filePath}`);
      return [];
    }

    const content = await fs.promises.readFile(filePath, 'utf-8');
    const lines = content.split('\n');
    const sections: LaTeXSection[] = [];

    let currentSection: LaTeXSection | null = null;
    let contentBuffer: string[] = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const sectionMatch = this.matchSection(line);

      if (sectionMatch) {
        // 保存前一个section
        if (currentSection) {
          currentSection.content = contentBuffer.join('\n').trim();
          currentSection.endLine = i - 1;
          sections.push(currentSection);
        }

        // 创建新section
        currentSection = {
          id: this.generateSectionId(sectionMatch.type, sectionMatch.title),
          type: sectionMatch.type,
          title: sectionMatch.title,
          content: '',
          startLine: i,
          endLine: i,
          file: fileName
        };
        contentBuffer = [];
      } else if (currentSection) {
        contentBuffer.push(line);
      }
    }

    // 保存最后一个section
    if (currentSection) {
      currentSection.content = contentBuffer.join('\n').trim();
      currentSection.endLine = lines.length - 1;
      sections.push(currentSection);
    }

    return sections;
  }

  /**
   * 匹配章节标题
   */
  private matchSection(line: string): { type: LaTeXSection['type'], title: string } | null {
    const patterns = [
      { regex: /\\chapter\{([^}]+)\}/, type: 'chapter' as const },
      { regex: /\\section\{([^}]+)\}/, type: 'section' as const },
      { regex: /\\subsection\{([^}]+)\}/, type: 'subsection' as const },
      { regex: /\\subsubsection\{([^}]+)\}/, type: 'subsubsection' as const }
    ];

    for (const pattern of patterns) {
      const match = line.match(pattern.regex);
      if (match) {
        return {
          type: pattern.type,
          title: this.cleanTitle(match[1])
        };
      }
    }

    return null;
  }

  /**
   * 清理标题文本
   */
  private cleanTitle(title: string): string {
    return title
      .replace(/\\textbf\{([^}]+)\}/g, '$1')
      .replace(/\\emph\{([^}]+)\}/g, '$1')
      .replace(/\\textit\{([^}]+)\}/g, '$1')
      .replace(/\\\\/g, ' ')
      .trim();
  }

  /**
   * 生成section ID
   */
  private generateSectionId(type: string, title: string): string {
    const cleanTitle = title.replace(/[^\w\u4e00-\u9fff]/g, '').substring(0, 20);
    return `${type}-${cleanTitle}-${Date.now()}`;
  }

  /**
   * 提取文档标题
   */
  private extractTitle(content: string): string {
    const match = content.match(/\\title\{([^}]+)\}/);
    return match ? this.cleanTitle(match[1]) : '';
  }

  /**
   * 提取作者信息
   */
  private extractAuthor(content: string): string {
    const match = content.match(/\\author\{([^}]+)\}/);
    return match ? this.cleanTitle(match[1]) : '';
  }

  /**
   * 提取包含的文件列表
   */
  private extractIncludedFiles(content: string): string[] {
    const includePattern = /\\include\{([^}]+)\}/g;
    const files: string[] = [];
    let match;

    while ((match = includePattern.exec(content)) !== null) {
      files.push(match[1]);
    }

    return files;
  }

  /**
   * 提取纯文本内容（去除LaTeX命令）
   */
  extractPlainText(latexContent: string): string {
    return latexContent
      // 移除注释
      .replace(/%.*$/gm, '')
      // 移除常见的LaTeX命令
      .replace(/\\[a-zA-Z]+\*?\{[^}]*\}/g, '')
      .replace(/\\[a-zA-Z]+\*?/g, '')
      // 移除数学公式
      .replace(/\$\$[^$]*\$\$/g, '')
      .replace(/\$[^$]*\$/g, '')
      // 移除环境
      .replace(/\\begin\{[^}]*\}[\s\S]*?\\end\{[^}]*\}/g, '')
      // 清理空白
      .replace(/\s+/g, ' ')
      .trim();
  }

  /**
   * 分析段落
   */
  analyzeParagraphs(content: string): string[] {
    const plainText = this.extractPlainText(content);
    return plainText
      .split(/\n\s*\n/)
      .map(p => p.trim())
      .filter(p => p.length > 0);
  }
}