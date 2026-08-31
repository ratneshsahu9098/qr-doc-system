import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { documents, qr } from '../services/api'

function Dashboard() {
  const [docs, setDocs] = useState([])
  const [loading, setLoading] = useState(true)
  const [showUpload, setShowUpload] = useState(false)
  const [uploadForm, setUploadForm] = useState({ title: '', description: '', file: null })
  const [uploading, setUploading] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    loadDocuments()
  }, [])

  const loadDocuments = async () => {
    try {
      const res = await documents.list()
      setDocs(res.data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!uploadForm.file) return

    setUploading(true)
    const formData = new FormData()
    formData.append('file', uploadForm.file)
    formData.append('title', uploadForm.title || uploadForm.file.name)
    formData.append('description', uploadForm.description)

    try {
      await documents.create(formData)
      setShowUpload(false)
      setUploadForm({ title: '', description: '', file: null })
      loadDocuments()
    } catch (err) {
      alert(err.response?.data?.error || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (id, e) => {
    e.stopPropagation()
    if (!confirm('Delete this document?')) return

    try {
      await documents.delete(id)
      loadDocuments()
    } catch (err) {
      alert('Delete failed')
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    navigate('/login')
  }

  return (
    <div className="dashboard">
      <div className="header">
        <h1>QR Document System</h1>
        <div className="header-actions">
          <button className="btn btn-outline btn-sm" onClick={() => setShowUpload(true)}>
            + Upload PDF
          </button>
          <button className="btn btn-logout" onClick={handleLogout}>Logout</button>
        </div>
      </div>

      <div className="container">
        <div className="section-header">
          <h2>Documents ({docs.length})</h2>
        </div>

        {loading ? (
          <div className="loading">Loading...</div>
        ) : docs.length === 0 ? (
          <div className="empty-state">
            <h3>No documents yet</h3>
            <p>Upload your first PDF to get started</p>
          </div>
        ) : (
          <div className="doc-grid">
            {docs.map(doc => (
              <div key={doc.id} className="doc-card" onClick={() => navigate(`/admin/document/${doc.id}`)}>
                <span className="code">{doc.code}</span>
                <h3>{doc.title}</h3>
                {doc.description && <p>{doc.description}</p>}
                <p className="date">{new Date(doc.created_at).toLocaleDateString()}</p>
                <div className="actions">
                  <button className="btn btn-outline btn-sm" onClick={(e) => { e.stopPropagation(); window.open(qr.get(doc.id), '_blank') }}>
                    QR Code
                  </button>
                  <button className="btn btn-danger btn-sm" onClick={(e) => handleDelete(doc.id, e)}>
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {showUpload && (
        <div className="modal-overlay" onClick={() => setShowUpload(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Upload PDF</h2>
            <form onSubmit={handleUpload}>
              <div className="form-group">
                <label>PDF File</label>
                <input
                  type="file"
                  accept=".pdf"
                  onChange={(e) => setUploadForm({ ...uploadForm, file: e.target.files[0] })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Title</label>
                <input
                  type="text"
                  value={uploadForm.title}
                  onChange={(e) => setUploadForm({ ...uploadForm, title: e.target.value })}
                  placeholder="Document title"
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={uploadForm.description}
                  onChange={(e) => setUploadForm({ ...uploadForm, description: e.target.value })}
                  placeholder="Optional description"
                  rows={3}
                />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-outline" onClick={() => setShowUpload(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" disabled={uploading || !uploadForm.file}>
                  {uploading ? 'Uploading...' : 'Upload'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
