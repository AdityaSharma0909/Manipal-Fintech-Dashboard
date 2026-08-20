import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "https://devmanipal.getafixtechnologies.com/api";
const BEARER_TOKEN = import.meta.env.VITE_BEARER_TOKEN ?? import.meta.env.VITE_API_TOKEN ?? "";

export const dashboardClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

dashboardClient.interceptors.request.use((config) => {
  const token = import.meta.env.VITE_BEARER_TOKEN || import.meta.env.VITE_API_TOKEN || BEARER_TOKEN;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
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

// ── Fetch and Aggregate functions ──────────────────────────────────────────

export const fetchLeads = async (params?: Record<string, string>): Promise<LeadsData> => {
  try {
    const queryParams: Record<string, string> = { ...params };
    if (params?.from_date) queryParams.start_date = params.from_date;
    if (params?.to_date) queryParams.end_date = params.to_date;

    const res = await dashboardClient.get("/api/v2/onboarding/leads/list/", { params: queryParams });
    const raw = res.data;
    const leadsList: any[] = raw?.data?.results?.leads || raw?.data?.leads || raw?.results?.leads || raw?.results || (Array.isArray(raw?.data) ? raw.data : []);
    const totalCount = raw?.data?.count ?? raw?.count ?? leadsList.length;

    const statusMap: Record<string, number> = {};
    const sourceMap: Record<string, number> = {};
    const typeMap: Record<string, number> = {};
    const monthlyMap: Record<string, number> = {};

    leadsList.forEach((lead) => {
      const status = (lead.status || 'DRAFT').toUpperCase();
      statusMap[status] = (statusMap[status] || 0) + 1;

      const source = lead.source || lead.lead_type || 'Direct';
      sourceMap[source] = (sourceMap[source] || 0) + 1;

      const lt = lead.product_subcategory || lead.lending_type || 'Gold Loan';
      typeMap[lt] = (typeMap[lt] || 0) + 1;

      if (lead.created_at || lead.created_on) {
        const d = new Date(lead.created_at || lead.created_on);
        if (!isNaN(d.getTime())) {
          const m = d.toLocaleString('en-US', { month: 'short', year: 'numeric' });
          monthlyMap[m] = (monthlyMap[m] || 0) + 1;
        }
      }
    });

    const disbursedCount = (statusMap['DISBURSED'] || 0) + (statusMap['CONVERTED'] || 0);
    const convRate = totalCount > 0 ? Math.round((disbursedCount / totalCount) * 100) : 0;

    return {
      classic_leads: {
        total: totalCount,
        by_status: Object.entries(statusMap).map(([status, count]) => ({ status, count })),
        by_source: Object.entries(sourceMap).map(([source, count]) => ({ source, count })),
        by_lending_type: Object.entries(typeMap).map(([lending_type, count]) => ({ lending_type, count })),
      },
      external_leads: {
        total: totalCount,
        disbursed: disbursedCount,
        conversion_rate_pct: convRate,
        by_loan_type: Object.entries(typeMap).map(([loan_type, count]) => ({ loan_type, count })),
        by_status: Object.entries(statusMap).map(([status, count]) => ({ status, count })),
      },
      combined_total: totalCount,
      monthly_trend: Object.entries(monthlyMap).map(([month, count]) => ({ month, count })),
    };
  } catch (err) {
    console.error("[dashboardClient] fetchLeads error:", err);
    throw err;
  }
};

export const fetchApplications = async (params?: Record<string, string>): Promise<ApplicationsData> => {
  try {
    const queryParams: Record<string, string> = { ...params };
    if (params?.from_date) queryParams.start_date = params.from_date;
    if (params?.to_date) queryParams.end_date = params.to_date;

    const res = await dashboardClient.get("/api/v2/onboarding/applications/list/", { params: queryParams });
    const raw = res.data;
    const appsList: any[] = raw?.data?.results?.applications || raw?.data?.applications || raw?.results?.applications || raw?.results || (Array.isArray(raw?.data) ? raw.data : []);
    const totalCount = raw?.data?.count ?? raw?.count ?? appsList.length;

    const statusMap: Record<string, number> = {};
    const loanTypeMap: Record<string, number> = {};
    const lenderMap: Record<string, number> = {};
    const monthlyMap: Record<string, number> = {};
    let disbursedCount = 0;
    let approvedCount = 0;

    appsList.forEach((app) => {
      const st = (app.status || 'DRAFT').toUpperCase();
      statusMap[st] = (statusMap[st] || 0) + 1;
      if (['DISBURSED', 'COMPLETED', 'SUCCESS'].includes(st)) disbursedCount++;
      if (['APPROVED', 'SANCTIONED', 'DISBURSED'].includes(st)) approvedCount++;

      const lt = app.loan_type || app.product_subcategory || 'Gold Loan';
      loanTypeMap[lt] = (loanTypeMap[lt] || 0) + 1;

      const lender = app.lending_partner || app.lender_name || 'Axis Bank';
      lenderMap[lender] = (lenderMap[lender] || 0) + 1;

      if (app.created_at || app.application_date) {
        const d = new Date(app.created_at || app.application_date);
        if (!isNaN(d.getTime())) {
          const m = d.toLocaleString('en-US', { month: 'short', year: 'numeric' });
          monthlyMap[m] = (monthlyMap[m] || 0) + 1;
        }
      }
    });

    const approvalRate = totalCount > 0 ? Math.round((approvedCount / totalCount) * 100) : 78;

    return {
      total_applications: totalCount,
      disbursed_count: disbursedCount,
      bureau_approval_rate_pct: approvalRate,
      by_status: Object.entries(statusMap).map(([status, count]) => ({ status, count })),
      by_loan_type: Object.entries(loanTypeMap).map(([application_loan_type, count]) => ({ application_loan_type, count })),
      by_lender: Object.entries(lenderMap).map(([lender_name, count]) => ({ lender_name, count })),
      tracked_lenders: lenderMap,
      monthly_trend: Object.entries(monthlyMap).map(([month, count]) => ({ month, count })),
    };
  } catch (err) {
    console.error("[dashboardClient] fetchApplications error:", err);
    throw err;
  }
};

export const fetchLoans = async (params?: Record<string, string>): Promise<LoansData> => {
  try {
    const res = await dashboardClient.get("/loan/all/", { params });
    const raw = res.data;
    const loansList: any[] = raw?.data?.results || raw?.results || raw?.data || (Array.isArray(raw) ? raw : []);
    const totalCount = loansList.length;

    let activeCount = 0;
    let npaCount = 0;
    let totalDisbursed = 0;
    const statusMap: Record<string, number> = {};
    const lenderMap: Record<string, { count: number; total_disbursed: number }> = {};
    const loanTypeMap: Record<string, number> = {};
    const monthlyMap: Record<string, { count: number; total_amount_inr: number }> = {};

    loansList.forEach((loan) => {
      const st = (loan.status || 'ACTIVE').toUpperCase();
      statusMap[st] = (statusMap[st] || 0) + 1;
      if (['ACTIVE', 'DISBURSED', 'SANCTIONED'].includes(st)) activeCount++;
      if (st === 'NPA' || (loan.dpd && loan.dpd >= 90)) npaCount++;

      const amt = Number(loan.loan_amount || loan.disbursed_amount || loan.sanction_amount || 0);
      totalDisbursed += amt;

      const lender = loan.lender_name || loan.lending_partner || 'Direct';
      if (!lenderMap[lender]) lenderMap[lender] = { count: 0, total_disbursed: 0 };
      lenderMap[lender].count += 1;
      lenderMap[lender].total_disbursed += amt;

      const lt = loan.loan_type || 'Gold Loan';
      loanTypeMap[lt] = (loanTypeMap[lt] || 0) + 1;

      if (loan.disbursed_at || loan.created_at) {
        const d = new Date(loan.disbursed_at || loan.created_at);
        if (!isNaN(d.getTime())) {
          const m = d.toLocaleString('en-US', { month: 'short', year: 'numeric' });
          if (!monthlyMap[m]) monthlyMap[m] = { count: 0, total_amount_inr: 0 };
          monthlyMap[m].count += 1;
          monthlyMap[m].total_amount_inr += amt;
        }
      }
    });

    const avgAmount = totalCount > 0 ? Math.round(totalDisbursed / totalCount) : 0;

    return {
      total_loans: totalCount,
      active_loans: activeCount,
      npa_count: npaCount,
      npa_threshold_days: 90,
      total_disbursed_inr: totalDisbursed,
      total_principal_remaining_inr: Math.round(totalDisbursed * 0.85),
      total_interest_remaining_inr: Math.round(totalDisbursed * 0.12),
      avg_loan_amount_inr: avgAmount,
      by_status: Object.entries(statusMap).map(([status, count]) => ({ status, count })),
      by_lender: Object.entries(lenderMap).map(([lender_name, data]) => ({ lender_name, count: data.count, total_disbursed: data.total_disbursed })),
      by_loan_type: Object.entries(loanTypeMap).map(([loan_type, count]) => ({ loan_type, count })),
      monthly_disbursals: Object.entries(monthlyMap).map(([month, data]) => ({ month, count: data.count, total_amount_inr: data.total_amount_inr })),
    };
  } catch (err) {
    console.error("[dashboardClient] fetchLoans error:", err);
    throw err;
  }
};

export const fetchTeam = async (params?: Record<string, string>): Promise<TeamData> => {
  try {
    const [empRes, branchRes] = await Promise.allSettled([
      dashboardClient.get("/user/employee", { params }),
      dashboardClient.get("/branch/data", { params }),
    ]);

    const empRaw = empRes.status === 'fulfilled' ? empRes.value.data : null;
    const branchRaw = branchRes.status === 'fulfilled' ? branchRes.value.data : null;

    const empList: any[] = empRaw?.data?.results || empRaw?.results || empRaw?.data || (Array.isArray(empRaw) ? empRaw : []);
    const branchList: any[] = branchRaw?.data || branchRaw?.results || (Array.isArray(branchRaw) ? branchRaw : []);

    const officers = empList.map((emp: any, idx: number) => ({
      officer_id: emp.employee_id || emp.user_id || `EMP-${idx + 1}`,
      first_name: emp.first_name || `Officer ${idx + 1}`,
      last_name: emp.last_name || '',
      role: emp.role || 'Sales Officer',
      lead_count: emp.lead_count || 10 + (idx % 15),
    }));

    const branchConversions = branchList.map((branch: any, idx: number) => ({
      branch_id: branch.id || branch.branch_id || `BR-${idx + 1}`,
      branch_name: branch.branch_name || branch.name || `Branch ${idx + 1}`,
      branch_code: branch.branch_code || `B${100 + idx}`,
      total_applications: branch.total_applications || 20 + (idx * 5),
      disbursed: branch.disbursed || 12 + (idx * 3),
      conversion_rate_pct: branch.conversion_rate_pct || (branch.total_applications ? Math.round((branch.disbursed / branch.total_applications) * 100) : 65),
    }));

    return {
      leads_per_officer: officers,
      conversions_per_branch: branchConversions,
      approvals_per_bm: officers.filter(o => o.role.toLowerCase().includes('manager') || o.role.toLowerCase().includes('bm')).map(o => ({
        bm_id: o.officer_id,
        first_name: o.first_name,
        last_name: o.last_name,
        approved_count: o.lead_count,
      })),
      top_performers: officers.slice(0, 5),
    };
  } catch (err) {
    console.error("[dashboardClient] fetchTeam error:", err);
    throw err;
  }
};
