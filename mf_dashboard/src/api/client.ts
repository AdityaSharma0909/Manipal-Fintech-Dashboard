import axios from "axios";
import { QueryClient } from "@tanstack/react-query";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const API_KEY = import.meta.env.VITE_DASHBOARD_API_KEY ?? "37777cbe702135cd41ec8eefdb08ce5da2cc3925d8235efd998394bb5b07c14d";

export const axiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: {
    "X-Dashboard-API-Key": API_KEY,
    "Content-Type": "application/json",
  },
});

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000, // 30 seconds cache
    },
  },
});

export interface GlobalFilters {
  fromDate?: string;
  toDate?: string;
  branchId?: string;
  lendingPartner?: string;
  leadStatus?: string;
  loanStatus?: string;
}
