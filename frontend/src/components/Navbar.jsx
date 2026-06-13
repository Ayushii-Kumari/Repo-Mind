import { Sun, Moon, Github, Cpu } from 'lucide-react'

const s = {
  nav: {
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    padding: '0 28px', height: '56px',
    background: 'var(--bg2)', borderBottom: '1px solid var(--border)',
    position: 'sticky', top: 0, zIndex: 100,
    backdropFilter: 'blur(12px)',
  },
  logo: {
    display: 'flex', alignItems: 'center', gap: '8px',
    fontWeight: 600, fontSize: '16px', color: 'var(--text)',
    textDecoration: 'none',
  },
  logoIcon: {
    width: 28, height: 28, borderRadius: 8,
    background: 'var(--accent)', display: 'flex',
    alignItems: 'center', justifyContent: 'center',
  },
  right: { display: 'flex', alignItems: 'center', gap: '10px' },
  badge: {
    fontSize: '11px', fontWeight: 600, letterSpacing: '0.05em',
    padding: '3px 10px', borderRadius: '20px',
    background: 'var(--accent-bg)', color: 'var(--accent2)',
    border: '1px solid var(--accent)',
    fontFamily: 'var(--mono)',
  },
  themeBtn: {
    width: 36, height: 36, borderRadius: 8,
    border: '1px solid var(--border)', background: 'var(--bg3)',
    color: 'var(--text2)', cursor: 'pointer',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    transition: 'all 0.18s ease',
  },
}

export default function Navbar({ theme, onToggleTheme }) {
  return (
    <nav style={s.nav}>
      <a href="/" style={s.logo}>
        <div style={s.logoIcon}>
          <Cpu size={16} color="white" />
        </div>
        RepoMind
      </a>
      <div style={s.right}>
        <span style={s.badge}>Agentic AI · 5 agents</span>
        <a
          href="https://github.com/Ayushii-Kumari/Repo-Mind" target="_blank" rel="noreferrer"
          style={{ ...s.themeBtn, textDecoration: 'none' }}
        >
          <Github size={16} />
        </a>
        <button style={s.themeBtn} onClick={onToggleTheme} title="Toggle theme">
          {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
        </button>
      </div>
    </nav>
  )
}
