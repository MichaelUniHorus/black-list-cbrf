import { Outlet, Link } from 'react-router-dom'
import { MapPin, BarChart3 } from 'lucide-react'

export default function Layout() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="flex items-center space-x-2">
              <MapPin className="h-8 w-8 text-red-600" />
              <span className="text-xl font-bold text-gray-900">
                Open Black
              </span>
            </Link>
            
            <nav className="flex space-x-8">
              <Link
                to="/"
                className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900 hover:text-red-600"
              >
                <MapPin className="h-4 w-4 mr-2" />
                Карта
              </Link>
              <Link
                to="/stats"
                className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-red-600"
              >
                <BarChart3 className="h-4 w-4 mr-2" />
                Статистика
              </Link>
            </nav>
          </div>
        </div>
      </header>
      
      <main>
        <Outlet />
      </main>
    </div>
  )
}
