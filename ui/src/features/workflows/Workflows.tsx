import ThreeDBackground from '../../components/ThreeDBackground'


import { useEffect, useState } from 'react'
import api from '../../services/api'
import type { WorkflowItem } from '../../types'

const workflowStages = [
  { id: 'input', label: 'Input', icon: '\u{1F4E5}' },
  { id: 'classify', label: 'Classify', icon: '\u2699' },
  { id: 'process', label: 'Process', icon: '\u2696' },
  { id: 'review', label: 'Review', icon: '\u{1F50D}' },
  { id: 'output', label: 'Output', icon: '\u{1F4E4}' },
]

export default function Workflows() {
  const [workflows, setWorkflows] = useState<WorkflowItem[]>([])

  useEffect(() => {
    api.get('/api/workflows').then((res) => setWorkflows(res.data.workflows ?? [])).catch(() => {})
  }, [])

  return (
    <div className="page">
      <ThreeDBackground />
      <h1><span className="gradient-text">Workflows</span></h1>

      <div className="card" style={{ marginBottom: 20 }}>
        <h3 style={{ color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', fontSize: '0.85rem', marginBottom: 20 }}>
          Automation Pipeline
        </h3>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0, flexWrap: 'wrap' }}>
          {workflowStages.map((stage, i) => (
            <div key={stage.id} style={{ display: 'flex', alignItems: 'center' }}>
              <div className="workflow-node" style={{ flexDirection: 'column', gap: 4, minWidth: 'clamp(60px, 20vw, 80px)', textAlign: 'center' }}>
                <div style={{ fontSize: '1.5rem' }}>{stage.icon}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>{stage.label}</div>
              </div>
              {i < workflowStages.length - 1 && (
                <div style={{
                  width: 40, height: 2,
                  background: 'linear-gradient(90deg, var(--primary), transparent)',
                  margin: '0 4px',
                }} />
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <h3 style={{ color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', fontSize: '0.85rem', marginBottom: 12 }}>
          Deployed Workflows
        </h3>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>File</th>
                <th>Size</th>
                <th>Process ID</th>
              </tr>
            </thead>
            <tbody>
              {workflows.map((w, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: 600 }}>{w.name}</td>
                  <td><code style={{ color: 'var(--primary)', fontSize: '0.8rem' }}>{w.file}</code></td>
                  <td>{w.size > 1024 ? `${(w.size / 1024).toFixed(1)} KB` : `${w.size} B`}</td>
                  <td><code style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{w.process_id}</code></td>
                </tr>
              ))}
              {workflows.length === 0 && (
                <tr><td colSpan={4} style={{ textAlign: 'center', opacity: 0.6, padding: 20 }}>No workflows deployed yet</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
