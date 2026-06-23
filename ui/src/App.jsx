import { useState } from 'react'

function App() {
  const [message, setMessage] = useState('')
  const [response, setResponse] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setResponse('')
    try {
      const res = await fetch('http://localhost:7070/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: message }),
      })
      const data = await res.json()
      setResponse(data.response || data.error || JSON.stringify(data))
    } catch (err) {
      setResponse('Error: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: '2rem', maxWidth: 600, margin: '0 auto' }}>
      <h1>Gateway Tester</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Enter your message"
          style={{ width: '100%', padding: '0.5rem', fontSize: '1rem', boxSizing: 'border-box' }}
        />
        <button
          type="submit"
          disabled={loading || !message.trim()}
          style={{ marginTop: '0.5rem', padding: '0.5rem 1rem', fontSize: '1rem' }}
        >
          {loading ? 'Sending...' : 'Send to Gateway'}
        </button>
      </form>
      {response && (
        <pre style={{ marginTop: '1rem', padding: '1rem', background: '#f5f5f5', borderRadius: 4, whiteSpace: 'pre-wrap' }}>
          {response}
        </pre>
      )}
    </div>
  )
}

export default App
