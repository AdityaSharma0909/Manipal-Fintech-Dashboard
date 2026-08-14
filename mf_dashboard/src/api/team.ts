import { axiosInstance } from "./client";
import type { GlobalFilters } from "./client";
import type { TeamData } from "./dashboardClient";

export const getTeam = async (filters: GlobalFilters): Promise<TeamData> => {
  const params: Record<string, string> = {};
  if (filters.fromDate) params.from_date = filters.fromDate;
  if (filters.toDate) params.to_date = filters.toDate;
  if (filters.branchId) params.branch_id = filters.branchId;

  const response = await axiosInstance.get<TeamData>("/dashboard/team/", { params });
  return response.data;
};
