import axios from "axios";
import { QueryClient } from "@tanstack/react-query";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "https://devmanipal.getafixtechnologies.com/api";
const BEARER_TOKEN = import.meta.env.VITE_BEARER_TOKEN ?? import.meta.env.VITE_API_TOKEN ?? "";

export const axiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to inject Authorization Bearer token dynamically
axiosInstance.interceptors.request.use((config) => {
  const token = import.meta.env.VITE_BEARER_TOKEN || import.meta.env.VITE_API_TOKEN || BEARER_TOKEN;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to format errors
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      console.warn("[API Client] 401 Unauthorized: Please check your VITE_BEARER_TOKEN in .env");
    }
    return Promise.reject(error);
  }
);

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
