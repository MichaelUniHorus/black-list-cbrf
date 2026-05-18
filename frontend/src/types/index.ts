export interface Organization {
  id: number
  name: string
  inn: string | null
  ogrn: string | null
  legal_address: string | null
  website: string | null
  cbr_date_added: string | null
  cbr_reason: string | null
  cbr_category: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Location {
  id: number
  organization_id: number
  organization?: Organization
  address: string
  latitude: number | null
  longitude: number | null
  source: 'cbr' | 'yandex_geocode' | 'yandex_search'
  status: 'pending' | 'verified' | 'failed'
  yandex_org_id: string | null
  phone: string | null
  working_hours: string | null
  created_at: string
  updated_at: string
}

export interface OrganizationDetail extends Organization {
  locations: Location[]
  enrichment_tasks: EnrichmentTask[]
}

export interface EnrichmentTask {
  id: number
  organization_id: number
  task_type: 'geocode' | 'search_branches' | 'full_enrichment'
  status: 'pending' | 'running' | 'completed' | 'failed'
  celery_task_id: string | null
  result: string | null
  error_message: string | null
  started_at: string | null
  completed_at: string | null
  created_at: string
  updated_at: string
}

export interface Stats {
  total_organizations: number
  total_locations: number
  organizations_with_locations: number
  coverage_percent: number
}
