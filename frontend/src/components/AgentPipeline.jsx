const AGENTS = [
  { id: 'planner',     label: 'Planner',       icon: '🧠' },
  { id: 'repo_reader', label: 'Repo Reader',    icon: '📖' },
  { id: 'explainer',   label: 'Code Analyzer',  icon: '🔍' },
  { id: 'docs',        label: 'Docs Agent',     icon: '📝' },
  { id: 'diagram',     label: 'Diagram Agent',  icon: '🗺️' },
]

export default function AgentPipeline({ activeAgent, done }) {
  return (
    <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
      {AGENTS.map((a, i) => {
        const isDone = done || (activeAgent && AGENTS.findIndex(x => x.id === activeAgent) > i)
        const isActive = activeAgent === a.id
        return (
          <div key={a.id} style={{
            display: 'flex', alignItems: 'center', gap: 6,
            padding: '5px 12px', borderRadius: 20, fontSize: 13, fontWeight: 500,
            border: `1px solid ${isDone ? 'var(--green)' : isActive ? 'var(--accent)' : 'var(--border)'}`,
            background: isDone ? 'var(--green-bg)' : isActive ? 'var(--accent-bg)' : 'transparent',
            color: isDone ? 'var(--green)' : isActive ? 'var(--accent2)' : 'var(--text3)',
            transition: 'all 0.3s ease',
          }}>
            {isDone ? '✓' : isActive ? (
              <span style={{ display: 'inline-block', animation: 'spin 1s linear infinite' }}>⟳</span>
            ) : '○'}
            {a.label}
            <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
          </div>
        )
      })}
    </div>
  )
}
