import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

function History({ apiUrl }) {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await fetch(`${apiUrl}/api/history`)
        if (res.ok) {
          const data = await res.json()
          setItems(data)
        }
      } catch {
        // silently fail
      } finally {
        setLoading(false)
      }
    }
    fetchHistory()
  }, [apiUrl])

  const getVerdictColor = (verdict) => {
    switch (verdict) {
      case 'Safe': return 'text-green-400 bg-green-500/10'
      case 'Suspicious': return 'text-yellow-400 bg-yellow-500/10'
      case 'Likely Phishing': return 'text-orange-400 bg-orange-500/10'
      case 'Phishing': return 'text-red-400 bg-red-500/10'
      default: return 'text-gray-400 bg-gray-500/10'
    }
  }

  const getScoreColor = (score) => {
    if (score <= 20) return 'text-green-400'
    if (score <= 45) return 'text-yellow-400'
    if (score <= 70) return 'text-orange-400'
    return 'text-red-400'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <svg className="animate-spin h-8 w-8 text-sp-red" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Analysis History</h1>
        <Link
          to="/"
          className="text-sm bg-sp-red hover:bg-sp-red-hover text-white font-semibold px-4 py-2 rounded-lg transition-colors"
        >
          New Analysis
        </Link>
      </div>

      {items.length === 0 ? (
        <div className="bg-sp-card border border-sp-border rounded-xl p-12 text-center">
          <svg className="w-12 h-12 text-sp-text mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          <p className="text-sp-text">No emails analyzed yet.</p>
          <Link to="/" className="text-sp-red hover:underline text-sm mt-2 inline-block">
            Analyze your first email
          </Link>
        </div>
      ) : (
        <div className="space-y-2">
          {items.map((item) => (
            <Link
              key={item.id}
              to={`/results/${item.id}`}
              className="block bg-sp-card border border-sp-border rounded-xl p-4 hover:bg-white/[0.02] transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3">
                    <span className="text-white font-medium text-sm truncate">{item.filename}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${getVerdictColor(item.ai_verdict_label)}`}>
                      {item.ai_verdict_label}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 mt-1">
                    <span className="text-sp-text text-xs truncate">{item.subject || 'No subject'}</span>
                    <span className="text-sp-text text-xs">&mdash;</span>
                    <span className="text-sp-text text-xs truncate">{item.sender}</span>
                  </div>
                </div>
                <div className="flex items-center gap-3 flex-shrink-0 ml-4">
                  <span className={`text-lg font-bold ${getScoreColor(item.risk_score)}`}>
                    {item.risk_score}
                  </span>
                  <svg className="w-4 h-4 text-sp-text" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

export default History
