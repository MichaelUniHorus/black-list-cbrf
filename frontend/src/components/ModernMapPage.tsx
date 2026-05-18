import { useEffect, useState, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { locationsApi } from '../services/api'
import type { Location } from '../types'
import { MapContainer, TileLayer, Marker, Popup, useMap, GeoJSON } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { MapPin, Navigation, Phone, Clock, Building2, Filter } from 'lucide-react'
import altaiKraiBoundary from '../data/altai-krai-boundary.json'

// Fix for default marker icons
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

// Custom marker icon
const customIcon = L.divIcon({
  className: 'custom-marker',
  html: `
    <div style="
      background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
      width: 36px;
      height: 36px;
      border-radius: 50%;
      border: 3px solid white;
      box-shadow: 0 4px 12px rgba(220, 38, 38, 0.4);
      display: flex;
      align-items: center;
      justify-content: center;
    ">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
        <circle cx="12" cy="10" r="3"></circle>
      </svg>
    </div>
  `,
  iconSize: [36, 36],
  iconAnchor: [18, 36],
  popupAnchor: [0, -36],
})

// Component to handle map centering
function MapController({ selectedLocation }: { selectedLocation: Location | null }) {
  const map = useMap()

  useEffect(() => {
    if (selectedLocation && selectedLocation.latitude && selectedLocation.longitude) {
      map.panTo([selectedLocation.latitude, selectedLocation.longitude], {
        animate: true,
        duration: 1,
      })
    }
  }, [selectedLocation, map])

  return null
}

export default function ModernMapPage() {
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null)
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const [selectedCity, setSelectedCity] = useState<string>('all')
  const mapRef = useRef<L.Map | null>(null)

  const { data: locations, isLoading } = useQuery({
    queryKey: ['locations'],
    queryFn: () => locationsApi.getAll({ limit: 5000, has_coordinates: true }),
  })

  // Получаем уникальные города из адресов
  const cities = locations ? Array.from(new Set(
    locations.map(loc => {
      const match = loc.address.match(/г\. ([^,]+)/)
      return match ? match[1].trim() : null
    }).filter((city): city is string => city !== null)
  )).sort() : []

  // Фильтруем локации по выбранному городу
  const filteredLocations = selectedCity === 'all' 
    ? locations 
    : locations?.filter(loc => loc.address.includes(`г. ${selectedCity}`))

  const handleLocationClick = (location: Location) => {
    setSelectedLocation(location)
  }

  const handleBuildRoute = (location: Location) => {
    if (location.latitude && location.longitude && mapRef.current) {
      mapRef.current.flyTo([location.latitude, location.longitude], 16, {
        duration: 1
      })
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-slate-200/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-red-600 rounded-xl flex items-center justify-center shadow-lg shadow-red-500/20">
                <MapPin className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-slate-900 to-slate-700 bg-clip-text text-transparent">
                  Open Black
                </h1>
                <p className="text-sm text-slate-500">Карта нелегальных кредиторов</p>
              </div>
            </div>
            
            {locations && (
              <div className="flex items-center gap-6">
                <div className="text-right">
                  <p className="text-2xl font-bold text-slate-900">{locations.length}</p>
                  <p className="text-xs text-slate-500 uppercase tracking-wider">Точек на карте</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex flex-col lg:flex-row h-[calc(100vh-5rem)]">
        {/* Map Section */}
        <div className="flex-1 relative">
          {isLoading && (
            <div className="absolute inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center z-10">
              <div className="text-center">
                <div className="w-12 h-12 border-4 border-red-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-slate-600 font-medium">Загрузка данных...</p>
              </div>
            </div>
          )}
          
          {locations && locations.length > 0 && (
            <MapContainer
              center={[52.5, 82.5]}
              zoom={7}
              className="w-full h-full"
              style={{ background: 'linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 100%)' }}
              ref={(map) => { mapRef.current = map }}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                className="opacity-90"
              />
              <MapController selectedLocation={selectedLocation} />
              
              {/* Границы Алтайского края */}
              <GeoJSON
                data={altaiKraiBoundary as any}
                style={{
                  fillColor: '#dc2626',
                  fillOpacity: 0.08,
                  color: '#dc2626',
                  weight: 3,
                  opacity: 0.6,
                  dashArray: '8, 12'
                }}
              />
              
              {filteredLocations?.map((location) => {
                if (!location.latitude || !location.longitude) return null
                
                return (
                  <Marker
                    key={location.id}
                    position={[location.latitude, location.longitude]}
                    icon={customIcon}
                  >
                    <Popup className="custom-popup">
                      <div className="p-2 min-w-[200px]">
                        <h3 className="font-semibold text-slate-900 mb-2">{location.organization?.name || 'Организация'}</h3>
                        <p className="text-sm text-slate-600 mb-2">{location.address}</p>
                        {location.phone && (
                          <p className="text-sm text-slate-600 flex items-center gap-2 mb-1">
                            <Phone className="w-4 h-4" />
                            {location.phone}
                          </p>
                        )}
                        {location.working_hours && (
                          <p className="text-sm text-slate-600 flex items-center gap-2 mb-1">
                            <Clock className="w-4 h-4" />
                            {location.working_hours}
                          </p>
                        )}
                        <p className="text-xs text-slate-400 mt-2">Источник: {location.source}</p>
                      </div>
                    </Popup>
                  </Marker>
                )
              })}
            </MapContainer>
          )}
          
          {!isLoading && (!locations || locations.length === 0) && (
            <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-slate-50 to-blue-50">
              <div className="text-center p-8">
                <div className="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <MapPin className="w-10 h-10 text-slate-400" />
                </div>
                <h3 className="text-xl font-semibold text-slate-900 mb-2">Нет данных</h3>
                <p className="text-slate-500 mb-4">Запустите backend и загрузите данные из ЦБ РФ</p>
              </div>
            </div>
          )}
        </div>

        {/* Sidebar - Locations List */}
        <div className={`w-full lg:w-96 bg-white/90 backdrop-blur-md border-l border-slate-200/50 flex flex-col transition-all duration-300 ${isSidebarCollapsed ? 'lg:w-0 lg:overflow-hidden' : ''}`}>
          {/* Sidebar Header */}
          <div className="p-4 border-b border-slate-200/50 bg-gradient-to-r from-slate-50 to-white">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-lg font-semibold text-slate-900 flex items-center gap-2">
                <Building2 className="w-5 h-5 text-red-500" />
                Филиалы
              </h2>
              <button
                onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
                className="lg:hidden p-2 hover:bg-slate-100 rounded-lg transition-colors"
              >
                <Navigation className="w-5 h-5 text-slate-600" />
              </button>
            </div>
            
            {/* Фильтр по городам */}
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-slate-400" />
              <select
                value={selectedCity}
                onChange={(e) => setSelectedCity(e.target.value)}
                className="flex-1 px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition-all"
              >
                <option value="all">Все города ({locations?.length || 0})</option>
                {cities.map(city => {
                  const count = locations?.filter(loc => loc.address.includes(`г. ${city}`)).length || 0
                  return (
                    <option key={city} value={city}>
                      {city} ({count})
                    </option>
                  )
                })}
              </select>
            </div>
          </div>

          {/* Locations List */}
          <div className="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-3 max-h-[calc(100vh-8rem)]">
            {filteredLocations && filteredLocations.length > 0 ? (
              filteredLocations.map((location: Location, index: number) => (
                <div
                  key={location.id}
                  onClick={() => handleLocationClick(location)}
                  className={`
                    group relative bg-white rounded-2xl border border-slate-200/50 p-4 
                    cursor-pointer transition-all duration-300
                    hover:shadow-xl hover:shadow-red-500/10 hover:-translate-y-1 hover:border-red-200
                    ${selectedLocation?.id === location.id ? 'border-red-400 shadow-lg shadow-red-500/10' : ''}
                    animate-in fade-in slide-in-from-right
                  `}
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-red-50 to-red-100 rounded-xl flex items-center justify-center flex-shrink-0 group-hover:from-red-500 group-hover:to-red-600 transition-colors">
                      <MapPin className="w-5 h-5 text-red-500 group-hover:text-white transition-colors" />
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-slate-900 mb-1 line-clamp-2 group-hover:text-red-600 transition-colors">
                        {location.organization?.name || 'Организация'}
                      </h3>
                      <p className="text-sm text-slate-600 mb-2 line-clamp-2">
                        {location.address}
                      </p>
                      
                      <div className="space-y-1">
                        {location.phone && (
                          <p className="text-xs text-slate-500 flex items-center gap-1.5">
                            <Phone className="w-3.5 h-3.5" />
                            <span className="line-clamp-1">{location.phone}</span>
                          </p>
                        )}
                        {location.working_hours && (
                          <p className="text-xs text-slate-500 flex items-center gap-1.5">
                            <Clock className="w-3.5 h-3.5" />
                            <span className="line-clamp-1">{location.working_hours}</span>
                          </p>
                        )}
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleBuildRoute(location)
                    }}
                    className="mt-3 w-full py-2 px-4 bg-gradient-to-r from-red-500 to-red-600 text-white text-sm font-medium rounded-xl hover:from-red-600 hover:to-red-700 transition-all duration-200 flex items-center justify-center gap-2 shadow-lg shadow-red-500/20 hover:shadow-red-500/30"
                  >
                    <Navigation className="w-4 h-4" />
                    Место на карте
                  </button>
                </div>
              ))
            ) : (
              <div className="text-center py-12">
                <MapPin className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                <p className="text-slate-500">Нет данных для отображения</p>
              </div>
            )}
          </div>
        </div>
      </div>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: #f1f5f9;
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #cbd5e1;
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #94a3b8;
        }
        .leaflet-container {
          font-family: inherit;
        }
        .custom-popup .leaflet-popup-content-wrapper {
          border-radius: 12px;
          box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
        }
        .custom-popup .leaflet-popup-tip {
          background: white;
        }
        @keyframes fade-in {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        @keyframes slide-in-from-right {
          from {
            opacity: 0;
            transform: translateX(20px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        .animate-in {
          animation: fade-in 0.5s ease-out forwards;
        }
        .slide-in-from-right {
          animation: slide-in-from-right 0.5s ease-out forwards;
        }
      `}</style>
    </div>
  )
}
