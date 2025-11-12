import { create } from 'zustand'

export interface Project {
  id: number
  title: string
  description?: string
  genre?: string
  target_audience?: string
  word_count_goal?: number
  status?: string
  created_at: string
  updated_at: string
  last_accessed?: string
  user_id: number
}

export interface ProjectStatistics {
  document_count: number
  paragraph_count: number
  total_words: number
  optimization_summary: {
    pending: number
    processing: number
    completed: number
    failed: number
  }
}

interface ProjectState {
  projects: Project[]
  currentProject: Project | null
  projectStatistics: ProjectStatistics | null
  isLoading: boolean
  error: string | null
}

interface ProjectActions {
  setProjects: (projects: Project[]) => void
  setCurrentProject: (project: Project | null) => void
  setProjectStatistics: (statistics: ProjectStatistics | null) => void
  addProject: (project: Project) => void
  updateProject: (project: Project) => void
  removeProject: (projectId: number) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearError: () => void
}

export const useProjectStore = create<ProjectState & ProjectActions>((set, get) => ({
  // State
  projects: [],
  currentProject: null,
  projectStatistics: null,
  isLoading: false,
  error: null,

  // Actions
  setProjects: (projects: Project[]) => {
    set({ projects })
  },

  setCurrentProject: (currentProject: Project | null) => {
    set({ currentProject })
  },

  setProjectStatistics: (projectStatistics: ProjectStatistics | null) => {
    set({ projectStatistics })
  },

  addProject: (project: Project) => {
    const { projects } = get()
    set({ projects: [project, ...projects] })
  },

  updateProject: (updatedProject: Project) => {
    const { projects, currentProject } = get()
    const updatedProjects = projects.map(project =>
      project.id === updatedProject.id ? updatedProject : project
    )
    set({
      projects: updatedProjects,
      currentProject: currentProject?.id === updatedProject.id ? updatedProject : currentProject
    })
  },

  removeProject: (projectId: number) => {
    const { projects, currentProject } = get()
    const filteredProjects = projects.filter(project => project.id !== projectId)
    set({
      projects: filteredProjects,
      currentProject: currentProject?.id === projectId ? null : currentProject
    })
  },

  setLoading: (isLoading: boolean) => {
    set({ isLoading })
  },

  setError: (error: string | null) => {
    set({ error })
  },

  clearError: () => {
    set({ error: null })
  },
}))