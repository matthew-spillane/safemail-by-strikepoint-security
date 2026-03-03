function AIVerdictCard({ verdict }) {
  if (!verdict) return null

  const getVerdictColor = () => {
    switch (verdict.verdict) {
      case 'Safe':
        return { bg: 'bg-green-500/10', border: 'border-green-500/20', text: 'text-green-400' }
      case 'Suspicious':
        return { bg: 'bg-yellow-500/10', border: 'border-yellow-500/20', text: 'text-yellow-400' }
      case 'Likely Phishing':
        return { bg: 'bg-orange-500/10', border: 'border-orange-500/20', text: 'text-orange-400' }
      case 'Phishing':
        return { bg: 'bg-red-500/10', border: 'border-red-500/20', text: 'text-red-400' }
      default:
        return { bg: 'bg-gray-500/10', border: 'border-gray-500/20', text: 'text-gray-400' }
    }
  }

  const colors = getVerdictColor()

  return (
    <div className={`bg-sp-card border ${colors.border} rounded-xl p-6`}>
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-white font-bold text-lg flex items-center gap-2">
            <svg className="w-5 h-5 text-sp-red" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            AI Analyst Verdict
          </h3>
          <p className="text-sp-text text-sm mt-1">Powered by Claude AI</p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`text-sm font-medium px-3 py-1 rounded-full ${colors.bg} ${colors.text}`}>
            {verdict.verdict}
          </span>
          <span className="text-xs text-sp-text bg-sp-border/50 px-2 py-1 rounded-full">
            {verdict.confidence} confidence
          </span>
        </div>
      </div>
      <p className="text-sp-text text-sm leading-relaxed">{verdict.explanation}</p>
    </div>
  )
}

export default AIVerdictCard
