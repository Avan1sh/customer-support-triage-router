import { Routes, Route } from 'react-router-dom'
import App from './App.jsx'
import Dashboard from './Dashboard.jsx'

// Two routes: the customer storefront ("/") and the internal ops dashboard.
export default function Root() {
  return (
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/dashboard" element={<Dashboard />} />
    </Routes>
  )
}
