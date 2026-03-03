import { Link, useLocation } from 'react-router-dom'

function Navbar() {
  const location = useLocation()

  const isActive = (path) => location.pathname === path

  const linkClass = (path) =>
    `flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
      isActive(path)
        ? 'text-white bg-white/10'
        : 'text-sp-text hover:text-white hover:bg-white/5'
    }`

  return (
    <header className="sticky top-0 z-50 bg-sp-bg/90 backdrop-blur-xl border-b border-sp-border">
      <div className="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3 py-2">
          <img
            src="/logoclose.png"
            onError={(e) => { e.target.onerror = null; e.target.src = '/logoclose.svg'; }}
            alt="Strikepoint"
            className="h-7 w-auto"
          />
          <span className="font-bold text-lg text-white tracking-tight">SafeMail</span>
        </Link>

        <div className="flex items-center gap-2">
          <Link to="/" className={linkClass('/')}>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-4 0a1 1 0 01-1-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 01-1 1h-2z" />
            </svg>
            Home
          </Link>
          <Link to="/history" className={linkClass('/history')}>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            History
          </Link>
          <Link
            to="/"
            className="ml-2 px-4 py-1.5 bg-sp-red hover:bg-sp-red-hover text-white text-sm font-semibold rounded-lg transition-colors"
          >
            New Analysis
          </Link>
        </div>
      </div>
    </header>
  )
}

export default Navbar
