export interface ReportConfig {
  name: string;
  pages: string[];
  metrics: string[];
  fromDate?: string;
  toDate?: string;
  format: "excel" | "csv" | "pdf";
}

export interface ScheduledReport {
  id: string;
  name: string;
  frequency: "daily" | "weekly" | "monthly";
  recipients: string;
  lastSent?: string;
  nextRun: string;
  status: "active" | "paused";
}

// Memory-based state store for dashboard reports demo
let reportsList: ReportConfig[] = [];
let scheduledReports: ScheduledReport[] = [
  {
    id: "1",
    name: "Executive Weekly Summary",
    frequency: "weekly",
    recipients: "cxo@manipalfintech.com, board@manipalfintech.com",
    lastSent: "2026-08-04",
    nextRun: "2026-08-11",
    status: "active",
  },
  {
    id: "2",
    name: "NPA & Loan Delinquency Alert",
    frequency: "daily",
    recipients: "risk-mgmt@manipalfintech.com",
    lastSent: "2026-08-09",
    nextRun: "2026-08-10",
    status: "active",
  },
  {
    id: "3",
    name: "Branch Conversion & BM Leaderboard",
    frequency: "monthly",
    recipients: "ops-heads@manipalfintech.com",
    lastSent: "2026-08-01",
    nextRun: "2026-09-01",
    status: "paused",
  }
];

export const getReports = async (): Promise<ReportConfig[]> => {
  return reportsList;
};

export const createReport = async (report: ReportConfig): Promise<ReportConfig> => {
  reportsList.push(report);
  return report;
};

export const getScheduledReports = async (): Promise<ScheduledReport[]> => {
  return scheduledReports;
};

export const toggleScheduledReport = async (id: string): Promise<ScheduledReport | null> => {
  const rep = scheduledReports.find(r => r.id === id);
  if (rep) {
    rep.status = rep.status === "active" ? "paused" : "active";
    return rep;
  }
  return null;
};

export const deleteScheduledReport = async (id: string): Promise<boolean> => {
  const index = scheduledReports.findIndex(r => r.id === id);
  if (index !== -1) {
    scheduledReports.splice(index, 1);
    return true;
  }
  return false;
};
