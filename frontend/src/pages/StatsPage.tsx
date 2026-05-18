import { useQuery } from '@tanstack/react-query'
import { statsApi } from '../services/api'
import { BarChart3, MapPin, Building2, Percent } from 'lucide-react'

export default function StatsPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['stats'],
    queryFn: statsApi.get,
  })

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <p>Загрузка статистики...</p>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">
        Статистика
      </h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={<Building2 className="h-8 w-8 text-red-600" />}
          title="Всего организаций"
          value={stats?.total_organizations || 0}
        />
        
        <StatCard
          icon={<MapPin className="h-8 w-8 text-blue-600" />}
          title="Всего точек"
          value={stats?.total_locations || 0}
        />
        
        <StatCard
          icon={<BarChart3 className="h-8 w-8 text-green-600" />}
          title="С локациями"
          value={stats?.organizations_with_locations || 0}
        />
        
        <StatCard
          icon={<Percent className="h-8 w-8 text-purple-600" />}
          title="Покрытие"
          value={`${stats?.coverage_percent || 0}%`}
        />
      </div>
    </div>
  )
}

function StatCard({ icon, title, value }: { icon: React.ReactNode; title: string; value: string | number }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">{value}</p>
        </div>
        <div>{icon}</div>
      </div>
    </div>
  )
}
