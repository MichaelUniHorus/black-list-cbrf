import { useEffect, useRef, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { locationsApi } from '../services/api'
import type { Location } from '../types'

declare global {
  interface Window {
    ymaps: any
  }
}

export default function MapPage() {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<any>(null)
  const [mapReady, setMapReady] = useState(false)

  const { data: locations, isLoading } = useQuery({
    queryKey: ['locations'],
    queryFn: () => locationsApi.getAll({ limit: 5000, has_coordinates: true }),
  })

  useEffect(() => {
    if (window.ymaps && !mapInstanceRef.current && mapRef.current) {
      window.ymaps.ready(() => {
        const map = new window.ymaps.Map(mapRef.current, {
          center: [55.76, 37.64],
          zoom: 5,
          controls: ['zoomControl', 'searchControl', 'typeSelector', 'fullscreenControl'],
        })
        
        mapInstanceRef.current = map
        setMapReady(true)
      })
    }
  }, [])

  useEffect(() => {
    if (mapReady && mapInstanceRef.current && locations && locations.length > 0) {
      mapInstanceRef.current.geoObjects.removeAll()
      
      const clusterer = new window.ymaps.Clusterer({
        preset: 'islands#redClusterIcons',
        groupByCoordinates: false,
        clusterDisableClickZoom: false,
        clusterHideIconOnBalloonOpen: false,
        geoObjectHideIconOnBalloonOpen: false,
      })
      
      const placemarks = locations.map((location: Location) => {
        if (!location.latitude || !location.longitude) return null
        
        const placemark = new window.ymaps.Placemark(
          [location.latitude, location.longitude],
          {
            balloonContentHeader: `<strong>${location.address}</strong>`,
            balloonContentBody: `
              <div class="space-y-2">
                ${location.phone ? `<p><strong>Телефон:</strong> ${location.phone}</p>` : ''}
                ${location.working_hours ? `<p><strong>Часы работы:</strong> ${location.working_hours}</p>` : ''}
                <p><strong>Источник:</strong> ${location.source}</p>
              </div>
            `,
          },
          {
            preset: 'islands#redDotIcon',
          }
        )
        
        return placemark
      }).filter(Boolean)
      
      clusterer.add(placemarks)
      mapInstanceRef.current.geoObjects.add(clusterer)
      
      if (placemarks.length > 0) {
        mapInstanceRef.current.setBounds(clusterer.getBounds(), {
          checkZoomRange: true,
          zoomMargin: 50,
        })
      }
    }
  }, [mapReady, locations])

  return (
    <div className="relative h-[calc(100vh-4rem)]">
      {isLoading && (
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-10 bg-white px-4 py-2 rounded-lg shadow-lg">
          <p className="text-sm text-gray-600">Загрузка данных...</p>
        </div>
      )}
      
      {locations && locations.length > 0 && (
        <div className="absolute top-4 left-4 z-10 bg-white px-4 py-2 rounded-lg shadow-lg">
          <p className="text-sm font-medium text-gray-900">
            Найдено точек: <span className="text-red-600">{locations.length}</span>
          </p>
        </div>
      )}
      
      <div ref={mapRef} className="w-full h-full" />
    </div>
  )
}
