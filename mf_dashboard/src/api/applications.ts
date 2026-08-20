import type { GlobalFilters } from "./client";
import { fetchApplications } from "./dashboardClient";
import type { ApplicationsData } from "./dashboardClient";

export const getApplications = async (filters: GlobalFilters): Promise<ApplicationsData> => {
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

  return fetchApplications(params);
};
