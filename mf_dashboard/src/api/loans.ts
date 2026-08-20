import type { GlobalFilters } from "./client";
import { fetchLoans } from "./dashboardClient";
import type { LoansData } from "./dashboardClient";

export const getLoans = async (filters: GlobalFilters): Promise<LoansData> => {
  const params: Record<string, string> = {};
  if (filters.fromDate) params.from_date = filters.fromDate;
  if (filters.toDate) params.to_date = filters.toDate;
  if (filters.branchId) params.branch_id = filters.branchId;
  if (filters.loanStatus) params.status = filters.loanStatus;

  return fetchLoans(params);
};
