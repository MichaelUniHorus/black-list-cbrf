import axios from 'axios'
import type { Organization, OrganizationDetail, Location, Stats } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const organizationsApi = {
  getAll: async (params?: { skip?: number; limit?: number; search?: string }) => {
    const { data } = await api.get<Organization[]>('/organizations', { params })
    return data
  },

  getById: async (id: number) => {
    const { data } = await api.post<OrganizationDetail>(`/organizations/${id}`)
    return data
  },

  enrich: async (id: number) => {
    const { data } = await api.post(`/organizations/${id}/enrich`)
    return data
  },
}

export const locationsApi = {
  getAll: async (params?: { skip?: number; limit?: number; has_coordinates?: boolean }) => {
    const { data } = await api.get<Location[]>('/locations', { params })
    return data
  },
}

export const adminApi = {
  syncCBR: async () => {
    const { data } = await api.post('/admin/sync-cbr')
    return data
  },
}

export const statsApi = {
  get: async () => {
    const { data} = await api.get<Stats>('/stats')
    return data
  },
}

export default api
