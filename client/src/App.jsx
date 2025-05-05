import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
// import Signup from './Signup'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <Router>
      <Routes>
        <Route path='/' element={<Signup />} />
      </Routes>
    </Router>
  )
}

export default App
