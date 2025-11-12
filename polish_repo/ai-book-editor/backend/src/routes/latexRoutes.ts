import { Router, Request, Response } from 'express';
import multer from 'multer';
import * as path from 'path';
import * as fs from 'fs';
import { LaTeXParser } from '../services/latexParser';
import { ContentAnalyzer } from '../services/contentAnalyzer';
import { OptimizationEngine } from '../services/optimizationEngine';
import { AIService, createAIService, defaultAIConfig } from '../services/aiService';

const router = Router();

// 配置文件上传
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = path.join(__dirname, '../../uploads');
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({ 
  storage,
  fileFilter: (req, file, cb) => {
    if (file.mimetype === 'text/plain' || path.extname(file.originalname) === '.tex') {
      cb(null, true);
    } else {
      cb(new Error('只支持.tex文件'));
    }
  },
  limits: {
    fileSize: 10 * 1024 * 1024 // 10MB限制
  }
});

// 初始化服务
const aiService = createAIService(defaultAIConfig);

/**
 * 上传并分析LaTeX文件
 */
router.post('/upload', upload.array('files'), async (req: Request, res: Response) => {
  try {
    const files = req.files as Express.Multer.File[];
    if (!files || files.length === 0) {
      return res.status(400).json({ error: '请上传至少一个文件' });
    }

    // 查找主文件
    const mainFile = files.find(file => 
      file.originalname.includes('main') || 
      file.originalname.includes('AImath') ||
      files.length === 1
    ) || files[0];

    const projectDir = path.dirname(mainFile.path);
    const parser = new LaTeXParser(projectDir);
    
    // 解析LaTeX文档
    const document = await parser.parseMainFile(mainFile.path);
    
    res.json({
      success: true,
      document: {
        title: document.title,
        author: document.author,
        sections: document.sections.map(section => ({
          id: section.id,
          type: section.type,
          title: section.title,
          file: section.file,
          wordCount: section.content.length
        }))
      },
      uploadedFiles: files.map(file => ({
        originalName: file.originalname,
        filename: file.filename,
        size: file.size
      }))
    });
  } catch (error) {
    console.error('File upload error:', error);
    res.status(500).json({ 
      error: '文件上传失败',
      details: error instanceof Error ? error.message : '未知错误'
    });
  }
});

/**
 * 分析LaTeX文档内容
 */
router.post('/analyze', async (req: Request, res: Response) => {
  try {
    const { projectPath, analysisType = 'full' } = req.body;
    
    if (!projectPath) {
      return res.status(400).json({ error: '请提供项目路径' });
    }

    const parser = new LaTeXParser(projectPath);
    const analyzer = new ContentAnalyzer();
    const optimizer = new OptimizationEngine();

    // 解析文档
    const mainFilePath = path.join(projectPath, 'AImath.v4.tex');
    const document = await parser.parseMainFile(mainFilePath);

    // 内容分析
    const analysisResult = await analyzer.analyzeDocument(document);

    // 生成优化建议
    const optimizationResult = await optimizer.generateOptimizations(
      analysisResult.duplicates,
      analysisResult.logicIssues
    );

    // AI增强分析（如果启用）
    let aiSuggestions = [];
    if (analysisType === 'full' || analysisType === 'ai') {
      try {
        for (const section of document.sections.slice(0, 3)) { // 限制前3个章节避免API限制
          const aiResult = await aiService.analyzeText(
            section.content,
            {
              sectionTitle: section.title,
              chapterTitle: section.title,
              documentType: 'academic'
            }
          );
          aiSuggestions.push(...aiResult.suggestions);
        }
      } catch (aiError) {
        console.warn('AI analysis failed:', aiError);
      }
    }

    res.json({
      success: true,
      analysis: {
        document: {
          title: document.title,
          author: document.author,
          totalSections: document.sections.length,
          totalWords: document.sections.reduce((sum, s) => sum + s.content.length, 0)
        },
        statistics: analysisResult.statistics,
        duplicates: analysisResult.duplicates,
        logicIssues: analysisResult.logicIssues,
        suggestions: optimizationResult.suggestions,
        aiSuggestions: aiSuggestions,
        summary: optimizationResult.summary
      }
    });
  } catch (error) {
    console.error('Analysis error:', error);
    res.status(500).json({ 
      error: '分析失败',
      details: error instanceof Error ? error.message : '未知错误'
    });
  }
});

/**
 * 获取特定章节的详细内容
 */
router.get('/section/:sectionId', async (req: Request, res: Response) => {
  try {
    const { sectionId } = req.params;
    const { projectPath } = req.query;

    if (!projectPath) {
      return res.status(400).json({ error: '请提供项目路径' });
    }

    const parser = new LaTeXParser(projectPath as string);
    const mainFilePath = path.join(projectPath as string, 'AImath.v4.tex');
    const document = await parser.parseMainFile(mainFilePath);

    const section = document.sections.find(s => s.id === sectionId);
    if (!section) {
      return res.status(404).json({ error: '章节未找到' });
    }

    // 获取段落详情
    const paragraphs = parser.extractParagraphs(section.content);

    res.json({
      success: true,
      section: {
        ...section,
        paragraphs: paragraphs.map((p, index) => ({
          id: `${sectionId}-p${index}`,
          content: p,
          wordCount: p.length,
          index
        }))
      }
    });
  } catch (error) {
    console.error('Section fetch error:', error);
    res.status(500).json({ 
      error: '获取章节失败',
      details: error instanceof Error ? error.message : '未知错误'
    });
  }
});

/**
 * 应用优化建议
 */
router.post('/optimize', async (req: Request, res: Response) => {
  try {
    const { 
      projectPath, 
      sectionId, 
      optimizationType, 
      originalText, 
      context 
    } = req.body;

    if (!projectPath || !sectionId || !optimizationType || !originalText) {
      return res.status(400).json({ error: '缺少必要参数' });
    }

    // 使用AI服务进行优化
    const optimizationResult = await aiService.optimizeText({
      originalText,
      context: context || {
        sectionTitle: '未知章节',
        chapterTitle: '未知章节'
      },
      optimizationType,
      preserveLatex: true
    });

    // 这里应该实际修改文件，但为了安全起见，我们只返回建议
    res.json({
      success: true,
      optimization: optimizationResult,
      preview: {
        original: originalText,
        optimized: optimizationResult.optimizedText,
        changes: optimizationResult.changes
      }
    });
  } catch (error) {
    console.error('Optimization error:', error);
    res.status(500).json({ 
      error: '优化失败',
      details: error instanceof Error ? error.message : '未知错误'
    });
  }
});

/**
 * 检测重复内容
 */
router.post('/detect-duplicates', async (req: Request, res: Response) => {
  try {
    const { texts, threshold = 0.8 } = req.body;

    if (!texts || !Array.isArray(texts)) {
      return res.status(400).json({ error: '请提供文本数组' });
    }

    const result = await aiService.detectDuplicates(texts, threshold);

    res.json({
      success: true,
      duplicates: result.duplicates
    });
  } catch (error) {
    console.error('Duplicate detection error:', error);
    res.status(500).json({ 
      error: '重复检测失败',
      details: error instanceof Error ? error.message : '未知错误'
    });
  }
});

/**
 * 分析逻辑流程
 */
router.post('/analyze-logic', async (req: Request, res: Response) => {
  try {
    const { paragraphs, context } = req.body;

    if (!paragraphs || !Array.isArray(paragraphs)) {
      return res.status(400).json({ error: '请提供段落数组' });
    }

    const result = await aiService.analyzeLogicFlow(paragraphs, context || {
      sectionTitle: '未知章节',
      chapterTitle: '未知章节'
    });

    res.json({
      success: true,
      logicAnalysis: result
    });
  } catch (error) {
    console.error('Logic analysis error:', error);
    res.status(500).json({ 
      error: '逻辑分析失败',
      details: error instanceof Error ? error.message : '未知错误'
    });
  }
});

/**
 * 获取项目统计信息
 */
router.get('/stats', async (req: Request, res: Response) => {
  try {
    const { projectPath } = req.query;

    if (!projectPath) {
      return res.status(400).json({ error: '请提供项目路径' });
    }

    const parser = new LaTeXParser(projectPath as string);
    const mainFilePath = path.join(projectPath as string, 'AImath.v4.tex');
    const document = await parser.parseMainFile(mainFilePath);

    const stats = {
      totalSections: document.sections.length,
      totalWords: document.sections.reduce((sum, s) => sum + s.content.length, 0),
      totalParagraphs: document.sections.reduce((sum, s) => 
        sum + parser.extractParagraphs(s.content).length, 0
      ),
      averageSectionLength: Math.round(
        document.sections.reduce((sum, s) => sum + s.content.length, 0) / document.sections.length
      ),
      sections: document.sections.map(section => ({
        id: section.id,
        title: section.title,
        wordCount: section.content.length,
        paragraphCount: parser.extractParagraphs(section.content).length
      }))
    };

    res.json({
      success: true,
      stats
    });
  } catch (error) {
    console.error('Stats error:', error);
    res.status(500).json({ 
      error: '获取统计信息失败',
      details: error instanceof Error ? error.message : '未知错误'
    });
  }
});

/**
 * 错误处理中间件
 */
router.use((error: any, req: Request, res: Response, next: any) => {
  console.error('LaTeX route error:', error);
  
  if (error instanceof multer.MulterError) {
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({ error: '文件大小超过限制（最大10MB）' });
    }
  }
  
  res.status(500).json({ 
    error: '服务器内部错误',
    details: error.message 
  });
});

export default router;