import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import FileUpload from '../components/FileUpload'

function Home({ apiUrl }) {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const handleUpload = async (file) => {
    setIsLoading(true)
    setError(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch(`${apiUrl}/api/analyze`, {
        method: 'POST',
        body: formData,
        credentials: 'include',
      })

      if (!res.ok) {
        throw new Error(`Analysis failed (${res.status})`)
      }

      const data = await res.json()

      if (data.error) {
        throw new Error(data.error)
      }

      navigate(`/results/${data.id}`)
    } catch (err) {
      setError(err.message || 'Failed to analyze email. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div className="text-center space-y-3">
        <h1 className="text-3xl font-bold text-white">Analyze an Email</h1>
        <p className="text-muted">
          Upload a <code className="text-white bg-dark-card px-1.5 py-0.5 rounded text-sm">.eml</code> file to check for phishing indicators, authentication issues, and suspicious content.
        </p>
      </div>

      <div className="bg-dark-card border border-dark-border rounded-xl p-6">
        <FileUpload onUpload={handleUpload} isLoading={isLoading} />
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}

      <div className="bg-dark-card border border-dark-border rounded-xl p-6">
        <h2 className="text-white font-bold text-lg mb-4">What We Check</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {[
            'SPF Authentication',
            'DKIM Authentication',
            'DMARC Authentication',
            'From/Reply-To Mismatch',
            'Display Name Spoofing',
            'Embedded URL Analysis',
            'Attachment Risk',
            'Header Path Analysis',
            'Subject Line Analysis',
            'AI Analyst Verdict',
          ].map((check) => (
            <div key={check} className="flex items-center gap-2 text-sm text-muted">
              <svg className="w-4 h-4 text-accent flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {check}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Home
