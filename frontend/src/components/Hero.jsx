import { useState } from 'react'
import { Search, Github, Zap, GitBranch, FileCode, Network } from 'lucide-react'

const EXAMPLES = [
  'https://github.com/tiangolo/fastapi',
  'https://github.com/langchain-ai/langchain',
  'https://github.com/streamlit/streamlit',
  'https://github.com/openai/openai-python',
]

const FEATURES = [
  { icon: <FileCode size={18} />, label: 'Project Summary', desc: 'What the repo does, in plain English' },
  { icon: <GitBranch size={18} />, label: 'Folder Explorer', desc: 'Every folder explained by AI' },
  { icon: <Network size={18} />, label: 'Architecture Diagram', desc: 'Visual flow of all components' },
  { icon: <Zap size={18} />, label: 'Setup Guide', desc: 'Copy-paste commands to run it' },
]

export default function Hero({ onAnalyze, error }) {
  const [url, setUrl] = useState('')

  const handleKey = (e) => { if (e.key === 'Enter') onAnalyze(url) }

  return (
    <main style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '72px 24px 48px' }}>
      {/* Headline */}
      <div style={{ textAlign: 'center', maxWidth: 620, marginBottom: 48 }}>
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: 6,
          fontSize: 12, fontWeight: 600, letterSpacing: '0.08em',
          color: 'var(--accent2)', background: 'var(--accent-bg)',
          border: '1px solid var(--accent)', borderRadius: 20,
          padding: '4px 12px', marginBottom: 24, fontFamily: 'var(--mono)',
        }}>
          <Zap size={12} /> POWERED BY GROQ · LLAMA 3.3 70B
        </div>
        <h1 style={{
          fontSize: 'clamp(28px, 5vw, 48px)', fontWeight: 700,
          lineHeight: 1.15, color: 'var(--text)', marginBottom: 16,
          letterSpacing: '-0.02em',
        }}>
          Understand any GitHub<br />repository instantly
        </h1>
        <p style={{ fontSize: 17, color: 'var(--text2)', lineHeight: 1.65 }}>
          Paste a GitHub URL — AI agents analyze the code, explain the architecture, and answer your questions.
        </p>
      </div>

      {/* Search bar */}
      <div style={{ width: '100%', maxWidth: 600, marginBottom: 12 }}>
        <div style={{
          display: 'flex', gap: 0,
          background: 'var(--bg2)', border: `1.5px solid ${error ? 'var(--red)' : 'var(--border)'}`,
          borderRadius: 12, overflow: 'hidden',
          boxShadow: 'var(--shadow)',
          transition: 'border-color 0.18s',
        }}
          onFocus={() => { }} 
        >
          <div style={{ padding: '0 14px', display: 'flex', alignItems: 'center', color: 'var(--text3)' }}>
            <Github size={18} />
          </div>
          <input
            value={url}
            onChange={e => setUrl(e.target.value)}
            onKeyDown={handleKey}
            placeholder="https://github.com/owner/repository"
            style={{
              flex: 1, padding: '14px 0', background: 'transparent',
              border: 'none', outline: 'none', color: 'var(--text)',
              fontSize: 15, fontFamily: 'var(--mono)',
            }}
          />
          <button
            onClick={() => onAnalyze(url)}
            style={{
              padding: '0 24px', background: 'var(--accent)',
              border: 'none', color: 'white', fontWeight: 600,
              fontSize: 14, cursor: 'pointer', whiteSpace: 'nowrap',
              transition: 'opacity 0.18s',
            }}
            onMouseOver={e => e.target.style.opacity = '0.85'}
            onMouseOut={e => e.target.style.opacity = '1'}
          >
            Analyze repo
          </button>
        </div>
        {error && (
          <p style={{ color: 'var(--red)', fontSize: 13, marginTop: 8, paddingLeft: 4 }}>⚠ {error}</p>
        )}
      </div>

      {/* Example chips */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center', marginBottom: 64 }}>
        <span style={{ fontSize: 13, color: 'var(--text3)', marginRight: 4, lineHeight: '28px' }}>Try:</span>
        {EXAMPLES.map(ex => (
          <button key={ex} onClick={() => { setUrl(ex); onAnalyze(ex) }}
            style={{
              fontSize: 12, fontFamily: 'var(--mono)', padding: '4px 12px',
              borderRadius: 20, border: '1px solid var(--border)',
              background: 'var(--bg2)', color: 'var(--text2)',
              cursor: 'pointer', transition: 'all 0.18s',
            }}
            onMouseOver={e => { e.currentTarget.style.borderColor = 'var(--accent)'; e.currentTarget.style.color = 'var(--accent2)' }}
            onMouseOut={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.color = 'var(--text2)' }}
          >
            {ex.replace('https://github.com/', '')}
          </button>
        ))}
      </div>

      {/* Feature cards */}
      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: 16, width: '100%', maxWidth: 860,
      }}>
        {FEATURES.map(f => (
          <div key={f.label} style={{
            background: 'var(--bg2)', border: '1px solid var(--border)',
            borderRadius: 12, padding: '20px',
          }}>
            <div style={{ color: 'var(--accent2)', marginBottom: 10 }}>{f.icon}</div>
            <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 4 }}>{f.label}</div>
            <div style={{ fontSize: 13, color: 'var(--text2)' }}>{f.desc}</div>
          </div>
        ))}
      </div>
    </main>
  )
}
