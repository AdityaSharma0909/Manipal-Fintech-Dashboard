import { axiosInstance } from "./client";
import type { GlobalFilters } from "./client";
import type { LoansData } from "./dashboardClient";

export const getLoans = async (filters: GlobalFilters): Promise<LoansData> => {
  const params: Record<string, string> = {};
  if (filters.fromDate) params.from_date = filters.fromDate;
  if (filters.toDate) params.to_date = filters.toDate;
  if (filters.branchId) params.branch_id = filters.branchId;

  const response = await axiosInstance.get<LoansData>("/dashboard/loans/", { params });
  return response.data;
};
