import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from 'antd'
import { useAuthStore } from './store/authStore'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Projects from './pages/Projects'
import ProjectDetail from './pages/ProjectDetail'
import DocumentEditor from './pages/DocumentEditor'
import LaTeXOptimizer from './pages/LaTeXOptimizer'

const { Content } = Layout

function App() {
  const { isAuthenticated } = useAuthStore()

  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    )
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Content style={{ padding: '0' }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/projects" element={<Projects />} />
          <Route path="/projects/:id" element={<ProjectDetail />} />
          <Route path="/projects/:projectId/documents/:documentId" element={<DocumentEditor />} />
          <Route path="/latex-optimizer" element={<LaTeXOptimizer />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Content>
    </Layout>
  )
}

export default App