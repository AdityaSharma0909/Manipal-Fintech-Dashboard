export interface Lead {
  id: string;
  lead_code?: string;
  customer_id?: string;
  name: string;
  email: string;
  phone: string;
  product_category?: string;
  product_subcategory?: string;
  product_display?: string;
  lead_type?: string;
  source?: string;
  crm_type?: string;
  state?: string;
  pincode?: string;
  amount?: number;
  status: string;
  created_at: string;
  modified_at?: string;
  created_by?: string;
  assigned_to?: string;
  punched_by?: string;
  team?: string;
  application_id?: string;
  prescreen_status?: boolean;
  isFreshOnboardingSubmitted?: boolean;
  lending_partner?: string;
  // Legacy / display properties for backwards compatibility
  organization?: string;
  industry?: string;
  plan?: string;
  region?: string;
  city?: string;
  revenue?: number;
  health_score?: number;
}

export interface Application {
  application_id: string;
  lead_code?: string;
  customer_id?: string;
  name: string;
  date: string;
  status: string;
  amount: number;
  disbursed_amount: number;
  loan_type?: string;
  product_category?: string;
  product_subcategory?: string;
  lead_type?: string;
  mobile_number?: string;
  email_address?: string;
  pincode?: string;
  state?: string;
  district?: string;
  bank_branch?: string;
  lending_partner?: string;
  prescreen_submitted?: boolean;
  isFreshOnboardingSubmitted?: boolean;
  punched_by?: string;
  punched_by_name?: string;
  assigned_rh?: string;
  assigned_rh_name?: string;
  rh_remarks?: string;
}

export interface Employee {
  user_id: string;
  username: string;
  employee_id?: string;
  first_name: string;
  last_name: string;
  phone: string;
  email?: string;
  role: string;
  designation?: string;
  team?: string;
  is_active: boolean;
  date_of_joining?: string;
  state?: string;
  district?: string;
  city?: string;
  pincode?: string;
  assigned_to?: string;
  assign_so?: string;
  branch_name?: string;
  branch_code?: string;
  // Computed metrics
  leads_handled_count?: number;
  applications_handled_count?: number;
  disbursed_applications_count?: number;
  conversion_rate?: number;
}

export interface ApiResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
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

export type TabId = 'overview' | 'leads' | 'applications' | 'employees' | 'analytics' | 'settings';

