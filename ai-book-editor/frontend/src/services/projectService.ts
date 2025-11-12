import api, { PaginatedResponse } from './api'
import { Project, ProjectStatistics } from '../store/projectStore'

export interface ProjectCreateRequest {
  title: string
  description?: string
  genre?: string
  target_audience?: string
  word_count_goal?: number
}

export interface ProjectUpdateRequest {
  title?: string
  description?: string
  genre?: string
  target_audience?: string
  word_count_goal?: number
  status?: string
}

export interface ProjectDuplicateRequest {
  title: string
  description?: string
}

export interface ProjectListParams {
  page?: number
  size?: number
  search?: string
  genre?: string
  status?: string
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

class ProjectService {
  // 获取项目列表
  async getProjects(params: ProjectListParams = {}): Promise<PaginatedResponse<Project>> {
    const response = await api.get('/projects/', { params })
    return response.data
  }

  // 获取单个项目
  async getProject(projectId: string): Promise<Project> {
    const response = await api.get(`/projects/${projectId}`)
    return response.data
  }

  // 创建项目
  async createProject(projectData: ProjectCreateRequest): Promise<Project> {
    const response = await api.post('/projects/', projectData)
    return response.data
  }

  // 更新项目
  async updateProject(projectId: string, projectData: ProjectUpdateRequest): Promise<Project> {
    const response = await api.put(`/projects/${projectId}`, projectData)
    return response.data
  }

  // 删除项目
  async deleteProject(projectId: string): Promise<void> {
    await api.delete(`/projects/${projectId}`)
  }

  // 复制项目
  async duplicateProject(projectId: string, data: ProjectDuplicateRequest): Promise<Project> {
    const response = await api.post(`/projects/${projectId}/duplicate`, data)
    return response.data
  }

  // 获取项目统计信息
  async getProjectStatistics(projectId: string): Promise<ProjectStatistics> {
    const response = await api.get(`/projects/${projectId}/statistics`)
    return response.data
  }

  // 获取最近的项目
  async getRecentProjects(limit: number = 10): Promise<Project[]> {
    const response = await api.get('/projects/recent/list', {
      params: { limit }
    })
    return response.data
  }

  // 搜索项目
  async searchProjects(query: string, params: Omit<ProjectListParams, 'search'> = {}): Promise<PaginatedResponse<Project>> {
    return this.getProjects({ ...params, search: query })
  }

  // 按类型获取项目
  async getProjectsByGenre(genre: string, params: Omit<ProjectListParams, 'genre'> = {}): Promise<PaginatedResponse<Project>> {
    return this.getProjects({ ...params, genre })
  }

  // 按状态获取项目
  async getProjectsByStatus(status: string, params: Omit<ProjectListParams, 'status'> = {}): Promise<PaginatedResponse<Project>> {
    return this.getProjects({ ...params, status })
  }

  // 获取项目概览数据（用于仪表盘）
  async getProjectsOverview(): Promise<{
    total: number
    active: number
    completed: number
    recent: Project[]
  }> {
    const [allProjects, recentProjects] = await Promise.all([
      this.getProjects({ size: 1000 }), // 获取所有项目用于统计
      this.getRecentProjects(5)
    ])

    const total = allProjects.total
    const active = allProjects.items.filter(p => p.status === 'active').length
    const completed = allProjects.items.filter(p => p.status === 'completed').length

    return {
      total,
      active,
      completed,
      recent: recentProjects
    }
  }
}

export const projectService = new ProjectService()