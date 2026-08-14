import { axiosInstance } from "./client";
import type { GlobalFilters } from "./client";
import type { LeadsData } from "./dashboardClient"; // reuse existing TS types

export const getLeads = async (filters: GlobalFilters): Promise<LeadsData> => {
  const params: Record<string, string> = {};
  if (filters.fromDate) params.from_date = filters.fromDate;
  if (filters.toDate) params.to_date = filters.toDate;
  if (filters.branchId) params.branch_id = filters.branchId;

  const response = await axiosInstance.get<LeadsData>("/dashboard/leads/", { params });
  return response.data;
};
