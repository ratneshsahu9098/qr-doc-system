import React from 'react'
import { HashRouter, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import DocumentDetail from './pages/DocumentDetail'

function PrivateRoute({ children }) {
  const token = localStorage.getItem('token')
  return token ? children : <Navigate to="/login" />
}

function App() {
  return (
    <HashRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/admin" element={
          <PrivateRoute><Dashboard /></PrivateRoute>
        } />
        <Route path="/admin/document/:id" element={
          <PrivateRoute><DocumentDetail /></PrivateRoute>
        } />
        <Route path="*" element={<Navigate to="/admin" />} />
      </Routes>
    </HashRouter>
  )
}

export default App
