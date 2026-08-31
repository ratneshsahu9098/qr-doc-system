import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { documents, qr } from '../services/api'

function DocumentDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [doc, setDoc] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showReplace, setShowReplace] = useState(false)
  const [replaceFile, setReplaceFile] = useState(null)
  const [replacing, setReplacing] = useState(false)
  const [editing, setEditing] = useState(false)
  const [editForm, setEditForm] = useState({ title: '', description: '' })

  useEffect(() => {
    loadDocument()
  }, [id])

  const loadDocument = async () => {
    try {
      const res = await documents.get(id)
      setDoc(res.data)
      setEditForm({ title: res.data.title, description: res.data.description })
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleUpdate = async (e) => {
    e.preventDefault()
    try {
      await documents.update(id, editForm)
      setEditing(false)
      loadDocument()
    } catch (err) {
      alert('Update failed')
    }
  }

  const handleReplace = async (e) => {
    e.preventDefault()
    if (!replaceFile) return

    setReplacing(true)
    const formData = new FormData()
    formData.append('file', replaceFile)

    try {
      await documents.replace(id, formData)
      setShowReplace(false)
      setReplaceFile(null)
      loadDocument()
    } catch (err) {
      alert(err.response?.data?.error || 'Replace failed')
    } finally {
      setReplacing(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm('Delete this document permanently?')) return
    try {
      await documents.delete(id)
      navigate('/admin')
    } catch (err) {
      alert('Delete failed')
    }
  }

  if (loading) return <div className="loading">Loading...</div>
  if (!doc) return <div className="loading">Document not found</div>

  return (
    <div className="detail-page">
      <div className="detail-header">
        <h1>Document Details</h1>
        <button className="btn btn-logout" onClick={() => navigate('/admin')}>Back to Dashboard</button>
      </div>

      <div className="detail-container">
        <div className="detail-card">
          {editing ? (
            <form onSubmit={handleUpdate}>
              <h2>Edit Document</h2>
              <div className="form-group">
                <label>Title</label>
                <input
                  type="text"
                  value={editForm.title}
                  onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={editForm.description}
                  onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                  rows={3}
                />
              </div>
              <div className="detail-actions">
                <button type="submit" className="btn btn-primary btn-sm">Save</button>
                <button type="button" className="btn btn-outline btn-sm" onClick={() => setEditing(false)}>Cancel</button>
              </div>
            </form>
          ) : (
            <>
              <div className="detail-field">
                <label>Document Code</label>
                <div className="value"><span className="code">{doc.code}</span></div>
              </div>
              <div className="detail-field">
                <label>Title</label>
                <div className="value">{doc.title}</div>
              </div>
              <div className="detail-field">
                <label>Description</label>
                <div className="value">{doc.description || 'No description'}</div>
              </div>
              <div className="detail-field">
                <label>Created</label>
                <div className="value">{new Date(doc.created_at).toLocaleString()}</div>
              </div>
              <div className="detail-field">
                <label>Last Updated</label>
                <div className="value">{new Date(doc.updated_at).toLocaleString()}</div>
              </div>

              <div className="qr-preview">
                <p style={{ marginBottom: 12, fontWeight: 500 }}>QR Code</p>
                <img src={qr.get(doc.id)} alt={`QR for ${doc.code}`} />
                <p style={{ marginTop: 8, fontSize: '0.85rem', color: '#666' }}>
                  Public URL: /d/{doc.code}
                </p>
              </div>

              <div className="detail-actions">
                <button className="btn btn-outline btn-sm" onClick={() => setEditing(true)}>
                  Edit Details
                </button>
                <button className="btn btn-outline btn-sm" onClick={() => setShowReplace(true)}>
                  Replace PDF
                </button>
                <button className="btn btn-outline btn-sm" onClick={() => window.open(qr.get(doc.id), '_blank')}>
                  Download QR
                </button>
                <button className="btn btn-danger btn-sm" onClick={handleDelete}>
                  Delete
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      {showReplace && (
        <div className="modal-overlay" onClick={() => setShowReplace(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Replace PDF</h2>
            <p style={{ marginBottom: 16, color: '#666' }}>
              The document code ({doc.code}) will remain the same. The QR code will still work.
            </p>
            <form onSubmit={handleReplace}>
              <div className="form-group">
                <label>New PDF File</label>
                <input
                  type="file"
                  accept=".pdf"
                  onChange={(e) => setReplaceFile(e.target.files[0])}
                  required
                />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-outline" onClick={() => setShowReplace(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={replacing || !replaceFile}>
                  {replacing ? 'Replacing...' : 'Replace PDF'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default DocumentDetail
