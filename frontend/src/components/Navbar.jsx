import { Link, useLocation } from 'react-router-dom'

function Navbar() {
  const location = useLocation()

  const isActive = (path) => location.pathname === path

  return (
    <nav className="bg-[#111111] border-b border-dark-border sticky top-0 z-50">
      <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link to="/" className="flex items-center gap-3">
            <img
              src="/logoclose.png"
              onError={(e) => { e.target.onerror = null; e.target.src = '/logoclose.svg'; }}
              alt="Strikepoint"
              className="h-8 w-8"
            />
            <span className="text-white font-bold text-xl">SafeMail</span>
          </Link>
        </div>

        <div className="flex items-center gap-6">
          <Link
            to="/"
            className={`text-sm font-medium transition-colors ${
              isActive('/') ? 'text-white' : 'text-muted hover:text-white'
            }`}
          >
            Home
          </Link>
          <Link
            to="/history"
            className={`text-sm font-medium transition-colors ${
              isActive('/history') ? 'text-white' : 'text-muted hover:text-white'
            }`}
          >
            History
          </Link>
          <Link
            to="/"
            className="bg-accent hover:bg-red-700 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-colors"
          >
            New Analysis
          </Link>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
