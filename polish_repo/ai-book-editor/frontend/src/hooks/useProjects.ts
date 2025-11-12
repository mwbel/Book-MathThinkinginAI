import { useMutation, useQuery, useQueryClient } from 'react-query'
import { projectService, ProjectCreateRequest, ProjectUpdateRequest, ProjectListParams } from '../services/projectService'
import { useProjectStore, Project } from '../store/projectStore'
import { message } from 'antd'

export const useProjects = (params: ProjectListParams = {}) => {
  const queryClient = useQueryClient()
  const { setProjects, setLoading, setError } = useProjectStore()

  // 获取项目列表
  const {
    data: projectsData,
    isLoading,
    error,
    refetch
  } = useQuery({
    queryKey: ['projects', params],
    queryFn: () => projectService.getProjects(params),
    onSuccess: (data) => {
      setProjects(data.items)
      setLoading(false)
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.detail || '获取项目列表失败'
      setError(errorMessage)
      setLoading(false)
    }
  })

  // 创建项目
  const createProjectMutation = useMutation({
    mutationFn: projectService.createProject,
    onSuccess: (newProject: Project) => {
      queryClient.invalidateQueries(['projects'])
      queryClient.invalidateQueries(['recentProjects'])
      message.success('项目创建成功')
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.detail || '项目创建失败'
      message.error(errorMessage)
    }
  })

  // 更新项目
  const updateProjectMutation = useMutation({
    mutationFn: ({ projectId, data }: { projectId: string; data: ProjectUpdateRequest }) =>
      projectService.updateProject(projectId, data),
    onSuccess: (updatedProject: Project) => {
      queryClient.invalidateQueries(['projects'])
      queryClient.invalidateQueries(['project', updatedProject.id.toString()])
      message.success('项目更新成功')
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.detail || '项目更新失败'
      message.error(errorMessage)
    }
  })

  // 删除项目
  const deleteProjectMutation = useMutation({
    mutationFn: projectService.deleteProject,
    onSuccess: () => {
      queryClient.invalidateQueries(['projects'])
      queryClient.invalidateQueries(['recentProjects'])
      message.success('项目删除成功')
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.detail || '项目删除失败'
      message.error(errorMessage)
    }
  })

  // 复制项目
  const duplicateProjectMutation = useMutation({
    mutationFn: ({ projectId, data }: { projectId: string; data: { title: string; description?: string } }) =>
      projectService.duplicateProject(projectId, data),
    onSuccess: (duplicatedProject: Project) => {
      queryClient.invalidateQueries(['projects'])
      message.success('项目复制成功')
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.detail || '项目复制失败'
      message.error(errorMessage)
    }
  })

  return {
    // 数据
    projects: projectsData?.items || [],
    pagination: projectsData ? {
      current: projectsData.page,
      pageSize: projectsData.size,
      total: projectsData.total,
      showSizeChanger: true,
      showQuickJumper: true,
    } : undefined,
    
    // 状态
    isLoading,
    error,
    
    // 方法
    refetch,
    createProject: (data: ProjectCreateRequest) => createProjectMutation.mutate(data),
    updateProject: (projectId: string, data: ProjectUpdateRequest) => 
      updateProjectMutation.mutate({ projectId, data }),
    deleteProject: (projectId: string) => deleteProjectMutation.mutate(projectId),
    duplicateProject: (projectId: string, data: { title: string; description?: string }) =>
      duplicateProjectMutation.mutate({ projectId, data }),
    
    // 加载状态
    isCreating: createProjectMutation.isLoading,
    isUpdating: updateProjectMutation.isLoading,
    isDeleting: deleteProjectMutation.isLoading,
    isDuplicating: duplicateProjectMutation.isLoading,
  }
}

export const useProject = (projectId: string) => {
  const queryClient = useQueryClient()
  const { setCurrentProject } = useProjectStore()

  // 获取单个项目
  const {
    data: project,
    isLoading,
    error
  } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => projectService.getProject(projectId),
    enabled: !!projectId,
    onSuccess: (data: Project) => {
      setCurrentProject(data)
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.detail || '获取项目详情失败'
      message.error(errorMessage)
    }
  })

  return {
    project,
    isLoading,
    error,
    refetch: () => queryClient.invalidateQueries(['project', projectId])
  }
}

export const useProjectStatistics = (projectId: string) => {
  const { setProjectStatistics } = useProjectStore()

  // 获取项目统计信息
  const {
    data: statistics,
    isLoading,
    error
  } = useQuery({
    queryKey: ['projectStatistics', projectId],
    queryFn: () => projectService.getProjectStatistics(projectId),
    enabled: !!projectId,
    onSuccess: (data) => {
      setProjectStatistics(data)
    }
  })

  return {
    statistics,
    isLoading,
    error
  }
}

export const useRecentProjects = (limit: number = 10) => {
  // 获取最近的项目
  const {
    data: recentProjects,
    isLoading,
    error
  } = useQuery({
    queryKey: ['recentProjects', limit],
    queryFn: () => projectService.getRecentProjects(limit)
  })

  return {
    recentProjects: recentProjects || [],
    isLoading,
    error
  }
}

export const useProjectsOverview = () => {
  // 获取项目概览数据
  const {
    data: overview,
    isLoading,
    error
  } = useQuery({
    queryKey: ['projectsOverview'],
    queryFn: () => projectService.getProjectsOverview(),
    refetchInterval: 5 * 60 * 1000, // 每5分钟刷新一次
  })

  return {
    overview,
    isLoading,
    error
  }
}