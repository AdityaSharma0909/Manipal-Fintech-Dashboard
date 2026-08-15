export interface Lead {
  id: string | number;
  name: string;
  email: string;
  phone: string;
  organization?: string;
  industry?: string;
  plan?: string;
  status: string;
  created_at: string;
  updated_at?: string;
  region?: string;
  city?: string;
  ai_requests?: number;
  health_score?: number;
  revenue?: number;
  users?: number;
  projects?: number;
  storage?: number;
  last_active?: string;
  product_subcategory?: string;
  contact_number?: string;
  pan_number?: string;
}

export interface ApiResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Lead[];
}

export interface KPICard {
  title: string;
  value: string | number;
  change: number;
  description: string;
  icon: string;
  color: string;
  sparkline: number[];
}

export interface RegionData {
  name: string;
  users: number;
  growth: number;
  revenue: number;
  health: number;
  trend: number[];
}

export interface ActivityEvent {
  id: string;
  type: string;
  user: string;
  action: string;
  time: string;
  category: 'auth' | 'workspace' | 'upgrade' | 'ai' | 'admin' | 'report';
  avatar: string;
}

export type TabId = 'overview' | 'users' | 'activity' | 'insights' | 'performance' | 'analytics' | 'reports' | 'settings';
