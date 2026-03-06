import { useState } from 'react'
import { useLocation, Link } from 'react-router-dom'
import AIVerdictCard from '../components/AIVerdictCard'
import RiskGauge from '../components/RiskGauge'
import SummaryBar from '../components/SummaryBar'
import CheckCard from '../components/CheckCard'

function Results() {
  const location = useLocation()
  const result = location.state?.result || null
  const error = result ? null : 'Result not found'
  const [copied, setCopied] = useState(false)

  const handleCopyLink = () => {
    navigator.clipboard.writeText(window.location.href)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (error) {
    return (
      <div className="text-center py-20">
        <p className="text-red-400 mb-4">{error}</p>
        <Link to="/" className="text-sp-red hover:underline">Go back</Link>
      </div>
    )
  }

  if (!result) return null

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Analysis Results</h1>
          <p className="text-sp-text text-sm mt-1">
            {result.filename} &mdash; {result.subject || 'No subject'}
          </p>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <button
            onClick={handleCopyLink}
            className="text-sm text-sp-text hover:text-white border border-sp-border rounded-lg px-3 py-2 transition-colors"
          >
            {copied ? 'Copied!' : 'Copy Report Link'}
          </button>
          <Link
            to="/"
            className="text-sm bg-sp-red hover:bg-sp-red-hover text-white font-semibold px-3 py-2 rounded-lg transition-colors"
          >
            Scan Another
          </Link>
        </div>
      </div>

      {/* AI Verdict */}
      <AIVerdictCard verdict={result.ai_verdict} />

      {/* Risk Score & Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-sp-card border border-sp-border rounded-xl p-6 flex items-center justify-center">
          <RiskGauge score={result.risk_score} verdict={result.risk_verdict} />
        </div>
        <div className="md:col-span-2 space-y-4">
          <SummaryBar summary={result.summary} />
          {/* Email metadata */}
          <div className="bg-sp-card border border-sp-border rounded-xl p-5 space-y-2">
            <h3 className="text-white font-bold text-sm mb-3">Email Details</h3>
            <Detail label="From" value={result.from} />
            <Detail label="To" value={result.to} />
            {result.reply_to && <Detail label="Reply-To" value={result.reply_to} />}
            <Detail label="Subject" value={result.subject} />
            <Detail label="Date" value={result.date} />
          </div>
        </div>
      </div>

      {/* URL List */}
      {result.urls && result.urls.length > 0 && (
        <div className="bg-sp-card border border-sp-border rounded-xl p-5">
          <h3 className="text-white font-bold text-sm mb-3">Embedded URLs ({result.urls.length})</h3>
          <div className="space-y-2">
            {result.urls.map((u, i) => (
              <div key={i} className="flex items-start gap-2 text-sm">
                <span className={`mt-0.5 w-2 h-2 rounded-full flex-shrink-0 ${u.suspicious ? 'bg-red-400' : 'bg-green-400'}`} />
                <div>
                  <span className="text-sp-text break-all">{u.url}</span>
                  {u.flags && u.flags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-1">
                      {u.flags.map((flag, j) => (
                        <span key={j} className="text-xs bg-red-500/10 text-red-400 px-2 py-0.5 rounded-full">
                          {flag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Attachment List */}
      {result.attachments && result.attachments.length > 0 && (
        <div className="bg-sp-card border border-sp-border rounded-xl p-5">
          <h3 className="text-white font-bold text-sm mb-3">Attachments ({result.attachments.length})</h3>
          <div className="space-y-2">
            {result.attachments.map((a, i) => (
              <div key={i} className="flex items-center gap-2 text-sm">
                <span className={`w-2 h-2 rounded-full flex-shrink-0 ${a.risky ? 'bg-red-400' : 'bg-green-400'}`} />
                <span className="text-sp-text">
                  {a.filename} <span className="text-sp-text/60">({a.content_type})</span>
                </span>
                {a.risky && (
                  <span className="text-xs bg-red-500/10 text-red-400 px-2 py-0.5 rounded-full">
                    High risk file type
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Detailed Checks */}
      <div>
        <h2 className="text-white font-bold text-lg mb-3">Detailed Results</h2>
        <div className="space-y-2">
          {result.checks.map((check, i) => (
            <CheckCard key={i} check={check} />
          ))}
        </div>
      </div>

      {/* Bottom actions */}
      <div className="flex items-center justify-center gap-3 pt-4">
        <button
          onClick={handleCopyLink}
          className="text-sm text-sp-text hover:text-white border border-sp-border rounded-lg px-4 py-2.5 transition-colors"
        >
          {copied ? 'Copied!' : 'Copy Report Link'}
        </button>
        <Link
          to="/"
          className="text-sm bg-sp-red hover:bg-sp-red-hover text-white font-semibold px-4 py-2.5 rounded-lg transition-colors"
        >
          Scan Another
        </Link>
      </div>
    </div>
  )
}

function Detail({ label, value }) {
  return (
    <div className="flex items-start gap-2 text-sm">
      <span className="text-sp-text w-20 flex-shrink-0">{label}</span>
      <span className="text-white break-all">{value || 'N/A'}</span>
    </div>
  )
}

export default Results
