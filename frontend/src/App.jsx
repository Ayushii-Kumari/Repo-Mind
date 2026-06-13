import { useState, useEffect } from 'react'
import Navbar from './components/Navbar.jsx'
import Hero from './components/Hero.jsx'
import AnalysisPanel from './components/AnalysisPanel.jsx'

export default function App() {
  const [theme, setTheme] = useState(() =>
    window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  )
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [activeAgent, setActiveAgent] = useState(null)
  const [error, setError] = useState(null)
  const [repoUrl, setRepoUrl] = useState('')

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  const toggleTheme = () => setTheme(t => t === 'dark' ? 'light' : 'dark')

  const analyze = async (url) => {
    if (!url || !url.includes('github.com')) {
      setError('Please enter a valid GitHub URL.')
      return
    }
    setRepoUrl(url)
    setError(null)
    setResult(null)
    setLoading(true)

    const agents = ['planner', 'repo_reader', 'explainer', 'docs', 'diagram']
    for (const a of agents) {
      setActiveAgent(a)
      await new Promise(r => setTimeout(r, 600))
    }

    try {
      const resp = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_url: url }),
      })
      if (!resp.ok) {
        const err = await resp.json()
        throw new Error(err.detail || 'Analysis failed')
      }
      const data = await resp.json()
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
      setActiveAgent(null)
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar theme={theme} onToggleTheme={toggleTheme} />
      {!result && !loading ? (
        <Hero onAnalyze={analyze} error={error} />
      ) : (
        <AnalysisPanel
          result={result}
          loading={loading}
          activeAgent={activeAgent}
          error={error}
          repoUrl={repoUrl}
          onReset={() => { setResult(null); setError(null); }}
        />
      )}
    </div>
  )
}
