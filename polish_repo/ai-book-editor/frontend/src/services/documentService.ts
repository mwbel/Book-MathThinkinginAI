import api, { PaginatedResponse } from './api'

export interface Document {
  id: number
  title: string
  content: string
  order_index: number
  created_at: string
  updated_at: string
  project_id: number
}

export interface DocumentCreateRequest {
  title: string
  content?: string
  order_index?: number
}

export interface DocumentUpdateRequest {
  title?: string
  content?: string
  order_index?: number
}

export interface DocumentListParams {
  page?: number
  size?: number
  search?: string
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface DocumentOptimizationRequest {
  optimization_type: 'grammar' | 'style' | 'structure' | 'clarity' | 'engagement'
  target_audience?: string
  tone?: string
  additional_instructions?: string
}

export interface OptimizationResult {
  id: number
  document_id: number
  optimization_type: string
  original_content: string
  optimized_content: string
  suggestions: string[]
  status: 'pending' | 'processing' | 'completed' | 'failed'
  created_at: string
  updated_at: string
}

class DocumentService {
  // 获取项目的文档列表
  async getDocuments(projectId: string, params: DocumentListParams = {}): Promise<PaginatedResponse<Document>> {
    const response = await api.get(`/projects/${projectId}/documents/`, { params })
    return response.data
  }

  // 获取单个文档
  async getDocument(projectId: string, documentId: string): Promise<Document> {
    const response = await api.get(`/projects/${projectId}/documents/${documentId}`)
    return response.data
  }

  // 创建文档
  async createDocument(projectId: string, documentData: DocumentCreateRequest): Promise<Document> {
    const response = await api.post(`/projects/${projectId}/documents/`, documentData)
    return response.data
  }

  // 更新文档
  async updateDocument(projectId: string, documentId: string, documentData: DocumentUpdateRequest): Promise<Document> {
    const response = await api.put(`/projects/${projectId}/documents/${documentId}`, documentData)
    return response.data
  }

  // 删除文档
  async deleteDocument(projectId: string, documentId: string): Promise<void> {
    await api.delete(`/projects/${projectId}/documents/${documentId}`)
  }

  // 重新排序文档
  async reorderDocuments(projectId: string, documentOrders: { id: number; order_index: number }[]): Promise<void> {
    await api.post(`/projects/${projectId}/documents/reorder`, { documents: documentOrders })
  }

  // 复制文档
  async duplicateDocument(projectId: string, documentId: string, title: string): Promise<Document> {
    const response = await api.post(`/projects/${projectId}/documents/${documentId}/duplicate`, { title })
    return response.data
  }

  // 请求文档优化
  async optimizeDocument(
    projectId: string, 
    documentId: string, 
    optimizationData: DocumentOptimizationRequest
  ): Promise<OptimizationResult> {
    const response = await api.post(`/projects/${projectId}/documents/${documentId}/optimize`, optimizationData)
    return response.data
  }

  // 获取文档的优化历史
  async getOptimizationHistory(projectId: string, documentId: string): Promise<OptimizationResult[]> {
    const response = await api.get(`/projects/${projectId}/documents/${documentId}/optimizations`)
    return response.data
  }

  // 获取单个优化结果
  async getOptimizationResult(projectId: string, documentId: string, optimizationId: string): Promise<OptimizationResult> {
    const response = await api.get(`/projects/${projectId}/documents/${documentId}/optimizations/${optimizationId}`)
    return response.data
  }

  // 应用优化结果
  async applyOptimization(projectId: string, documentId: string, optimizationId: string): Promise<Document> {
    const response = await api.post(`/projects/${projectId}/documents/${documentId}/optimizations/${optimizationId}/apply`)
    return response.data
  }

  // 导出文档
  async exportDocument(projectId: string, documentId: string, format: 'pdf' | 'docx' | 'txt' | 'markdown'): Promise<Blob> {
    const response = await api.get(`/projects/${projectId}/documents/${documentId}/export`, {
      params: { format },
      responseType: 'blob'
    })
    return response.data
  }

  // 导出整个项目
  async exportProject(projectId: string, format: 'pdf' | 'docx' | 'txt' | 'markdown'): Promise<Blob> {
    const response = await api.get(`/projects/${projectId}/export`, {
      params: { format },
      responseType: 'blob'
    })
    return response.data
  }

  // 搜索文档内容
  async searchDocuments(projectId: string, query: string, params: Omit<DocumentListParams, 'search'> = {}): Promise<PaginatedResponse<Document>> {
    return this.getDocuments(projectId, { ...params, search: query })
  }

  // 获取文档统计信息
  async getDocumentStatistics(projectId: string, documentId: string): Promise<{
    word_count: number
    character_count: number
    paragraph_count: number
    reading_time: number
  }> {
    const response = await api.get(`/projects/${projectId}/documents/${documentId}/statistics`)
    return response.data
  }
}

export const documentService = new DocumentService()