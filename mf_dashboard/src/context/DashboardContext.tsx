import React, { createContext, useContext, useState, useEffect } from "react";
import type { GlobalFilters } from "../api/client";

export type DatePreset = "today" | "week" | "month" | "custom";

interface DashboardContextProps {
  preset: DatePreset;
  setPreset: (preset: DatePreset) => void;
  fromDate: string;
  setFromDate: (date: string) => void;
  toDate: string;
  setToDate: (date: string) => void;
  branchId: string;
  setBranchId: (id: string) => void;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  filters: GlobalFilters;
  resetAllFilters: () => void;
}

const DashboardContext = createContext<DashboardContextProps | undefined>(undefined);

export const DashboardProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [preset, setPreset] = useState<DatePreset>("month");
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [branchId, setBranchId] = useState("");
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    const today = new Date();
    if (preset === "today") {
      const dateStr = today.toISOString().split("T")[0];
      setFromDate(dateStr);
      setToDate(dateStr);
    } else if (preset === "week") {
      const first = today.getDate() - today.getDay();
      const firstDay = new Date(today.setDate(first));
      setFromDate(firstDay.toISOString().split("T")[0]);
      setToDate(new Date().toISOString().split("T")[0]);
    } else if (preset === "month") {
      const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
      setFromDate(firstDay.toISOString().split("T")[0]);
      setToDate(new Date().toISOString().split("T")[0]);
    }
  }, [preset]);

  const resetAllFilters = () => {
    setPreset("month");
    setBranchId("");
    setSearchQuery("");
  };

  const filters: GlobalFilters = {
    fromDate,
    toDate,
    branchId: branchId || undefined,
  };

  return (
    <DashboardContext.Provider
      value={{
        preset,
        setPreset,
        fromDate,
        setFromDate,
        toDate,
        setToDate,
        branchId,
        setBranchId,
        searchQuery,
        setSearchQuery,
        filters,
        resetAllFilters,
      }}
    >
      {children}
    </DashboardContext.Provider>
  );
};

export const useDashboard = () => {
  const context = useContext(DashboardContext);
  if (!context) {
    throw new Error("useDashboard must be used within a DashboardProvider");
  }
  return context;
};
