import { useState, useEffect, useCallback, useRef } from 'react';

export interface DashboardStats {
  leadsStats: any;
  applicationsStats: any;
  loansStats: any;
  teamStats: any;
}

interface UseDashboardStatsReturn {
  stats: DashboardStats | null;
  loading: boolean;
  isPolling: boolean;
  error: string | null;
  refetch: () => void;
  lastSync: Date | null;
  apiLatencyMs: number | null;
}

const POLL_INTERVAL_MS = 10 * 1000; // 10 seconds for near real-time updates

export const useDashboardStats = (fromDate?: string, toDate?: string): UseDashboardStatsReturn => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [isPolling, setIsPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastSync, setLastSync] = useState<Date | null>(null);
  const [apiLatencyMs, setApiLatencyMs] = useState<number | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchStats = useCallback(async (background = false) => {
    if (background) {
      setIsPolling(true);
    } else {
      setLoading(true);
    }
    setError(null);

    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    const apiKey = import.meta.env.VITE_DASHBOARD_API_KEY || '';

    const headers: Record<string, string> = {
      'X-Dashboard-API-Key': apiKey,
      'Content-Type': 'application/json',
    };

    // Build query string for date filters
    const params = new URLSearchParams();
    if (fromDate) params.set('from_date', fromDate);
    if (toDate) params.set('to_date', toDate);
    const qs = params.toString() ? `?${params.toString()}` : '';

    const startTime = performance.now();

    try {
      const [leadsRes, appsRes, loansRes, teamRes] = await Promise.allSettled([
        fetch(`${baseUrl}/dashboard/leads/${qs}`, { headers }),
        fetch(`${baseUrl}/dashboard/applications/${qs}`, { headers }),
        fetch(`${baseUrl}/dashboard/loans/${qs}`, { headers }),
        fetch(`${baseUrl}/dashboard/team/${qs}`, { headers }),
      ]);
      
      const endTime = performance.now();
      setApiLatencyMs(Math.round(endTime - startTime));

      const parseResult = async (result: PromiseSettledResult<Response>, name: string) => {
        if (result.status === 'rejected') {
          console.warn(`[DashboardStats] ${name} fetch failed:`, result.reason);
          return null;
        }
        if (!result.value.ok) {
          console.warn(`[DashboardStats] ${name} returned ${result.value.status}`);
          return null;
        }
        try {
          return await result.value.json();
        } catch (e) {
          console.warn(`[DashboardStats] ${name} JSON parse error:`, e);
          return null;
        }
      };

      const [leadsData, appsData, loansData, teamData] = await Promise.all([
        parseResult(leadsRes, 'leads'),
        parseResult(appsRes, 'applications'),
        parseResult(loansRes, 'loans'),
        parseResult(teamRes, 'team'),
      ]);

      const anySucceeded = leadsData || appsData || loansData || teamData;

      if (!anySucceeded) {
        throw new Error('All dashboard API endpoints failed to respond');
      }

      setStats({
        leadsStats: leadsData ?? {},
        applicationsStats: appsData ?? {},
        loansStats: loansData ?? {},
        teamStats: teamData ?? {},
      });
      setLastSync(new Date());
      setError(null);
    } catch (err: any) {
      console.error('[DashboardStats] Failed to load stats from backend:', err);
      setError(err.message || 'Unable to connect to Manipal Fintech backend');
    } finally {
      setLoading(false);
      setIsPolling(false);
    }
  }, [fromDate, toDate]); // eslint-disable-line react-hooks/exhaustive-deps

  // Initial fetch + polling
  useEffect(() => {
    fetchStats(false);

    timerRef.current = setInterval(() => {
      fetchStats(true);
    }, POLL_INTERVAL_MS);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [fetchStats]);

  return { stats, loading, isPolling, error, refetch: () => fetchStats(false), lastSync, apiLatencyMs };
};
