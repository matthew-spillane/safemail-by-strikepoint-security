import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Results from './pages/Results'
import History from './pages/History'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  return (
    <div className="min-h-screen bg-dark-bg text-white">
      <Navbar />
      <main className="max-w-5xl mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<Home apiUrl={API_URL} />} />
          <Route path="/results/:id" element={<Results apiUrl={API_URL} />} />
          <Route path="/history" element={<History apiUrl={API_URL} />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
