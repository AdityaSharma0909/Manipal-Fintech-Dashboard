import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const API_KEY = import.meta.env.VITE_DASHBOARD_API_KEY ?? "";

export const dashboardClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    "X-Dashboard-API-Key": API_KEY,
    "Content-Type": "application/json",
  },
});

// ── Response types ──────────────────────────────────────────────────────────

export interface MonthlyEntry {
  month: string;
  count: number;
}

export interface LeadsData {
  classic_leads: {
    total: number;
    by_status: Array<{ status: string; count: number }>;
    by_source: Array<{ source: string; count: number }>;
    by_lending_type: Array<{ lending_type: string; count: number }>;
  };
  external_leads: {
    total: number;
    disbursed: number;
    conversion_rate_pct: number;
    by_loan_type: Array<{ loan_type: string; count: number }>;
    by_status: Array<{ status: string; count: number }>;
  };
  combined_total: number;
  monthly_trend: MonthlyEntry[];
}

export interface ApplicationsData {
  total_applications: number;
  disbursed_count: number;
  bureau_approval_rate_pct: number;
  by_status: Array<{ status: string; count: number }>;
  by_loan_type: Array<{ application_loan_type: string; count: number }>;
  by_lender: Array<{ lender_name: string; count: number }>;
  tracked_lenders: Record<string, number>;
  monthly_trend: MonthlyEntry[];
}

export interface LoansData {
  total_loans: number;
  active_loans: number;
  npa_count: number;
  npa_threshold_days: number;
  total_disbursed_inr: number;
  total_principal_remaining_inr: number;
  total_interest_remaining_inr: number;
  avg_loan_amount_inr: number;
  by_status: Array<{ status: string; count: number }>;
  by_lender: Array<{ lender_name: string; count: number; total_disbursed: number }>;
  by_loan_type: Array<{ loan_type: string; count: number }>;
  monthly_disbursals: Array<{ month: string; count: number; total_amount_inr: number }>;
}

export interface TeamData {
  leads_per_officer: Array<{
    officer_id: string;
    first_name: string;
    last_name: string;
    role: string;
    lead_count: number;
  }>;
  conversions_per_branch: Array<{
    branch_id: string;
    branch_name: string;
    branch_code: string;
    total_applications: number;
    disbursed: number;
    conversion_rate_pct: number;
  }>;
  approvals_per_bm: Array<{
    bm_id: string;
    first_name: string;
    last_name: string;
    approved_count: number;
  }>;
  top_performers: Array<{
    officer_id: string;
    first_name: string;
    last_name: string;
    lead_count: number;
  }>;
}

// ── Fetch functions ─────────────────────────────────────────────────────────

export const fetchLeads = (params?: Record<string, string>) =>
  dashboardClient.get<LeadsData>("/dashboard/leads/", { params }).then((r) => r.data);

export const fetchApplications = (params?: Record<string, string>) =>
  dashboardClient.get<ApplicationsData>("/dashboard/applications/", { params }).then((r) => r.data);

export const fetchLoans = (params?: Record<string, string>) =>
  dashboardClient.get<LoansData>("/dashboard/loans/", { params }).then((r) => r.data);

export const fetchTeam = (params?: Record<string, string>) =>
  dashboardClient.get<TeamData>("/dashboard/team/", { params }).then((r) => r.data);
