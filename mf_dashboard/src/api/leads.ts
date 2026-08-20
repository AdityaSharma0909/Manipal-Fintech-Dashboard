import type { GlobalFilters } from "./client";
import { fetchLeads } from "./dashboardClient";
import type { LeadsData } from "./dashboardClient";

export const getLeads = async (filters: GlobalFilters): Promise<LeadsData> => {
  const params: Record<string, string> = {};
  if (filters.fromDate) {
    params.from_date = filters.fromDate;
    params.start_date = filters.fromDate;
  }
  if (filters.toDate) {
    params.to_date = filters.toDate;
    params.end_date = filters.toDate;
  }
  if (filters.branchId) params.branch_id = filters.branchId;
  if (filters.lendingPartner) params.lending_partner = filters.lendingPartner;
  if (filters.leadStatus) params.status = filters.leadStatus;

  return fetchLeads(params);
};
