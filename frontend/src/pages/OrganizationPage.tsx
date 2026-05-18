import { useParams } from 'react-router-dom'

export default function OrganizationPage() {
  const { id } = useParams()
  
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900">
        Организация #{id}
      </h1>
      <p className="mt-4 text-gray-600">
        Детальная информация об организации (в разработке)
      </p>
    </div>
  )
}
