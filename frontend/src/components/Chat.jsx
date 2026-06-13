import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User } from 'lucide-react'

export default function Chat({ repoUrl }) {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Ask me anything about this repository — architecture, specific files, design decisions, or how to extend it.' }
  ])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [statusText, setStatusText] = useState('')
  const bottomRef = useRef(null)

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const send = async () => {
    if (!input.trim() || sending) return
    const question = input.trim()
    setInput('')
    setMessages(m => [...m, { role: 'user', content: question }])
    setSending(true)
    setStatusText('Searching vector database...')
    try {
      const resp = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_url: repoUrl, question }),
      })

      if (!resp.ok) {
        let errMessage = 'Error getting response.'
        try {
          const data = await resp.json()
          errMessage = data.detail || errMessage
        } catch {}
        setMessages(m => [...m, { role: 'assistant', content: errMessage }])
        setSending(false)
        setStatusText('')
        return
      }

      let assistantStarted = false

      const reader = resp.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { value, done } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop()

        for (const line of lines) {
          if (!line.trim()) continue
          try {
            const data = JSON.parse(line)
            if (data.type === 'status') {
              setStatusText(data.content)
            } else if (data.type === 'content') {
              setStatusText('') // Hide status once content begins
              if (!assistantStarted) {
                // First content token — add the message bubble now
                assistantStarted = true
                setMessages(m => [...m, { role: 'assistant', content: data.content }])
              } else {
                setMessages(m => {
                  const last = m[m.length - 1]
                  if (last && last.role === 'assistant') {
                    return [...m.slice(0, -1), { ...last, content: last.content + data.content }]
                  }
                  return m
                })
              }
            } else if (data.type === 'error') {
              setMessages(m => {
                const last = m[m.length - 1]
                if (last && last.role === 'assistant') {
                  return [...m.slice(0, -1), { ...last, content: last.content + `\nError: ${data.content}` }]
                }
                return m
              })
            }
          } catch (e) {
            console.error("Failed to parse JSON stream line", line, e)
          }
        }
      }
    } catch {
      setMessages(m => [...m, { role: 'assistant', content: 'Network error. Is the backend running?' }])
    } finally {
      setSending(false)
      setStatusText('')
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 480 }}>
      <style>{`
        @keyframes statusDotPulse {
          0%, 100% { transform: scale(0.6); opacity: 0.4; }
          50% { transform: scale(1.2); opacity: 1; }
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(4px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulse {
          0%, 100% { opacity: 0.6; }
          50% { opacity: 1; }
        }
      `}</style>
      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: 16 }}>
        {messages.map((m, i) => (
          <div key={i} style={{ display: 'flex', gap: 12, alignItems: 'flex-start', flexDirection: m.role === 'user' ? 'row-reverse' : 'row' }}>
            <div style={{
              width: 32, height: 32, borderRadius: 8, flexShrink: 0,
              background: m.role === 'assistant' ? 'var(--accent-bg)' : 'var(--bg3)',
              border: `1px solid ${m.role === 'assistant' ? 'var(--accent)' : 'var(--border)'}`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: m.role === 'assistant' ? 'var(--accent2)' : 'var(--text2)',
            }}>
              {m.role === 'assistant' ? <Bot size={16} /> : <User size={16} />}
            </div>
            <div style={{
              maxWidth: '75%', padding: '10px 14px', borderRadius: 10, fontSize: 14, lineHeight: 1.6,
              background: m.role === 'user' ? 'var(--accent-bg)' : 'var(--bg3)',
              border: `1px solid ${m.role === 'user' ? 'var(--accent)' : 'var(--border)'}`,
              color: 'var(--text)', whiteSpace: 'pre-wrap',
            }}>
              {m.content}
            </div>
          </div>
        ))}
        {sending && statusText && (
          <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start', animation: 'fadeIn 0.3s ease' }}>
            <div style={{
              width: 32, height: 32, borderRadius: 8, flexShrink: 0,
              background: 'var(--accent-bg)', border: '1px solid var(--accent)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: 'var(--accent2)',
            }}>
              <Bot size={16} style={{ animation: 'pulse 1.5s infinite ease-in-out' }} />
            </div>
            <div style={{
              padding: '10px 14px', borderRadius: 10,
              background: 'var(--bg3)', border: '1px solid var(--border)',
              color: 'var(--text)', fontSize: 14, display: 'flex', alignItems: 'center', gap: 8,
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}>
              <span className="agent-status-indicator" style={{ display: 'inline-flex', gap: 3 }}>
                <span className="dot" style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--accent)', animation: 'statusDotPulse 1.2s infinite ease-in-out' }}></span>
                <span className="dot" style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--accent)', animation: 'statusDotPulse 1.2s infinite ease-in-out', animationDelay: '0.2s' }}></span>
                <span className="dot" style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--accent)', animation: 'statusDotPulse 1.2s infinite ease-in-out', animationDelay: '0.4s' }}></span>
              </span>
              <span style={{ fontWeight: 500, color: 'var(--text2)' }}>{statusText}</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      {/* Input */}
      <div style={{ padding: '12px 16px', borderTop: '1px solid var(--border)', display: 'flex', gap: 8 }}>
        <input
          value={input} onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
          placeholder="Ask about this repo..."
          style={{
            flex: 1, padding: '10px 14px', borderRadius: 8,
            border: '1px solid var(--border)', background: 'var(--bg)',
            color: 'var(--text)', fontSize: 14, outline: 'none', fontFamily: 'var(--font)',
          }}
        />
        <button onClick={send} disabled={sending || !input.trim()}
          style={{
            padding: '0 16px', borderRadius: 8, border: 'none',
            background: 'var(--accent)', color: 'white', cursor: 'pointer',
            opacity: (sending || !input.trim()) ? 0.5 : 1,
          }}>
          <Send size={16} />
        </button>
      </div>
    </div>
  )
}
