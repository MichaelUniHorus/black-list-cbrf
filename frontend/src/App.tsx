import { BrowserRouter, Routes, Route } from 'react-router-dom'
import ModernMapPage from './components/ModernMapPage'
import OrganizationPage from './pages/OrganizationPage'
import StatsPage from './pages/StatsPage'
import Layout from './components/Layout'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<ModernMapPage />} />
          <Route path="organization/:id" element={<OrganizationPage />} />
          <Route path="stats" element={<StatsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
