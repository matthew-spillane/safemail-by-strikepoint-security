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
      <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link to="/" className="flex items-center gap-3">
            <img
              src="/logoclose.png"
              onError={(e) => { e.target.onerror = null; e.target.src = '/logoclose.svg'; }}
              alt="Strikepoint"
              className="h-8 w-8"
            />
            <span className="font-bold text-lg text-white tracking-tight">SafeMail</span>
          </Link>
        </div>

        <div className="flex items-center gap-2">
          <Link to="/" className={linkClass('/')}>
            Home
          </Link>
          <Link to="/history" className={linkClass('/history')}>
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
