import { useState } from 'react'
import {
  LayoutDashboard, FolderTree, GitBranch,
  Terminal, MessageSquare, HelpCircle, ArrowLeft,
  Star, Cpu, Code2, Layers
} from 'lucide-react'
import AgentPipeline from './AgentPipeline.jsx'
import Chat from './Chat.jsx'

const TABS = [
  { id: 'summary',      label: 'Summary',       icon: <LayoutDashboard size={15} /> },
  { id: 'folders',      label: 'Folders',        icon: <FolderTree size={15} /> },
  { id: 'architecture', label: 'Architecture',   icon: <GitBranch size={15} /> },
  { id: 'setup',        label: 'Setup',          icon: <Terminal size={15} /> },
  { id: 'chat',         label: 'Chat',           icon: <MessageSquare size={15} /> },
  { id: 'questions',    label: 'Questions',      icon: <HelpCircle size={15} /> },
]

function Badge({ children, color = 'var(--accent)' }) {
  return (
    <span style={{
      fontSize: 12, padding: '2px 10px', borderRadius: 20, fontWeight: 500,
      background: color + '18', border: `1px solid ${color}55`, color: color,
      fontFamily: 'var(--mono)',
    }}>
      {children}
    </span>
  )
}

function CodeBlock({ children }) {
  return (
    <pre style={{
      fontFamily: 'var(--mono)', fontSize: 13, lineHeight: 1.7,
      background: 'var(--bg)', border: '1px solid var(--border)',
      borderRadius: 8, padding: '16px 20px', overflowX: 'auto',
      color: 'var(--text)',
    }}>
      {children}
    </pre>
  )
}

export default function AnalysisPanel({ result, loading, activeAgent, error, repoUrl, onReset }) {
  const [tab, setTab] = useState('summary')

  return (
    <div style={{ flex: 1, padding: '24px', maxWidth: 1100, margin: '0 auto', width: '100%' }}>

      {/* Top bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20, flexWrap: 'wrap', gap: 12 }}>
        <button onClick={onReset} style={{
          display: 'flex', alignItems: 'center', gap: 6, padding: '6px 14px',
          borderRadius: 8, border: '1px solid var(--border)', background: 'var(--bg2)',
          color: 'var(--text2)', cursor: 'pointer', fontSize: 13,
        }}>
          <ArrowLeft size={14} /> New repo
        </button>

        {result && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
            <a
              href={`https://github.com/${result.owner}/${result.repo_name}`}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                fontFamily: 'var(--mono)', fontSize: 14, color: 'var(--accent2)',
                textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: 5,
                transition: 'opacity 0.15s',
              }}
              onMouseOver={e => e.currentTarget.style.opacity = '0.75'}
              onMouseOut={e => e.currentTarget.style.opacity = '1'}
              title="Open on GitHub"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" style={{ flexShrink: 0 }}>
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
              </svg>
              {result.owner}/{result.repo_name}
            </a>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--yellow)', fontSize: 13 }}>
              <Star size={14} fill="currentColor" /> {result.stars?.toLocaleString()}
            </div>
            <Badge color="var(--accent)">{result.language || 'Unknown'}</Badge>
            <Badge color={result.complexity_score >= 7 ? 'var(--red)' : result.complexity_score >= 4 ? 'var(--yellow)' : 'var(--green)'}>
              Complexity {result.complexity_score}/10
            </Badge>
          </div>
        )}
      </div>

      {/* Agent pipeline */}
      <div style={{ background: 'var(--bg2)', border: '1px solid var(--border)', borderRadius: 12, padding: '16px 20px', marginBottom: 20 }}>
        <AgentPipeline activeAgent={activeAgent} done={!!result} />
      </div>

      {/* Error */}
      {error && !loading && (
        <div style={{ background: 'var(--red-bg)', border: '1px solid var(--red)', borderRadius: 10, padding: '14px 18px', color: 'var(--red)', marginBottom: 20 }}>
          ⚠ {error}
        </div>
      )}

      {/* Loading skeleton */}
      {loading && !result && (
        <div style={{ background: 'var(--bg2)', border: '1px solid var(--border)', borderRadius: 12, padding: 40, textAlign: 'center', color: 'var(--text2)' }}>
          <div style={{ fontSize: 32, marginBottom: 12 }}>⚙️</div>
          <p style={{ fontWeight: 600 }}>Analyzing repository...</p>
          <p style={{ fontSize: 13, marginTop: 6 }}>This takes 30–60 seconds. Agents are reading and indexing your code.</p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div style={{ background: 'var(--bg2)', border: '1px solid var(--border)', borderRadius: 12, overflow: 'hidden' }}>

          {/* Tech stack */}
          {result.tech_stack?.length > 0 && (
            <div style={{ padding: '14px 20px', borderBottom: '1px solid var(--border)', display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
              <span style={{ fontSize: 12, color: 'var(--text3)', marginRight: 4 }}>Stack:</span>
              {result.tech_stack.map(t => <Badge key={t}>{t}</Badge>)}
            </div>
          )}

          {/* Tabs */}
          <div style={{ display: 'flex', borderBottom: '1px solid var(--border)', overflowX: 'auto' }}>
            {TABS.map(t => (
              <button key={t.id} onClick={() => setTab(t.id)}
                style={{
                  display: 'flex', alignItems: 'center', gap: 6,
                  padding: '12px 18px', border: 'none', background: 'transparent',
                  color: tab === t.id ? 'var(--accent2)' : 'var(--text2)',
                  borderBottom: `2px solid ${tab === t.id ? 'var(--accent)' : 'transparent'}`,
                  cursor: 'pointer', fontSize: 13, fontWeight: 500, whiteSpace: 'nowrap',
                  transition: 'all 0.15s',
                }}>
                {t.icon} {t.label}
              </button>
            ))}
          </div>

          {/* Tab content */}
          <div style={{ padding: tab === 'chat' ? 0 : '24px' }}>

            {tab === 'summary' && (
              <div>
                <h2 style={{ fontSize: 17, fontWeight: 600, marginBottom: 12 }}>Project Summary</h2>
                <p style={{ color: 'var(--text2)', lineHeight: 1.75, marginBottom: 20 }}>{result.summary}</p>
                {result.description && (
                  <p style={{ fontSize: 13, color: 'var(--text3)', fontStyle: 'italic' }}>"{result.description}"</p>
                )}
              </div>
            )}

            {tab === 'folders' && (
              <div>
                <h2 style={{ fontSize: 17, fontWeight: 600, marginBottom: 16 }}>Folder Structure</h2>
                <CodeBlock>{result.folder_structure}</CodeBlock>
                <div style={{ marginTop: 24, display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {Object.entries(result.folder_explanations || {}).map(([folder, explanation]) => (
                    <div key={folder} style={{
                      display: 'flex', gap: 16, padding: '12px 16px',
                      background: 'var(--bg)', border: '1px solid var(--border)',
                      borderLeft: '3px solid var(--accent)', borderRadius: '0 8px 8px 0',
                    }}>
                      <code style={{ fontFamily: 'var(--mono)', fontSize: 13, color: 'var(--accent2)', minWidth: 140, flexShrink: 0 }}>
                        {folder}
                      </code>
                      <span style={{ fontSize: 14, color: 'var(--text2)', lineHeight: 1.6 }}>{explanation}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {tab === 'architecture' && (
              <div>
                <h2 style={{ fontSize: 17, fontWeight: 600, marginBottom: 16 }}>Architecture Diagram</h2>
                <CodeBlock>{result.architecture_diagram}</CodeBlock>
              </div>
            )}

            {tab === 'setup' && (
              <div>
                <h2 style={{ fontSize: 17, fontWeight: 600, marginBottom: 16 }}>Setup Instructions</h2>
                <div style={{ fontSize: 14, lineHeight: 1.8, color: 'var(--text2)', whiteSpace: 'pre-wrap' }}>
                  {result.setup_instructions}
                </div>
              </div>
            )}

            {tab === 'chat' && <Chat repoUrl={repoUrl} />}

            {tab === 'questions' && (
              <div>
                <h2 style={{ fontSize: 17, fontWeight: 600, marginBottom: 16 }}>Interview Questions</h2>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {(result.interview_questions || []).map((q, i) => (
                    <div key={i} style={{
                      padding: '14px 18px', background: 'var(--bg)',
                      border: '1px solid var(--border)', borderRadius: 8,
                      fontSize: 14, lineHeight: 1.6,
                    }}>
                      <span style={{ color: 'var(--accent2)', fontWeight: 600, marginRight: 8, fontFamily: 'var(--mono)' }}>Q{i + 1}</span>
                      {q}
                    </div>
                  ))}
                </div>
              </div>
            )}

          </div>
        </div>
      )}
    </div>
  )
}
