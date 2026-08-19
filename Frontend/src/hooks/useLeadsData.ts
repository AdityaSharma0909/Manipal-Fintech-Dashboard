import { useState, useEffect, useCallback, useRef } from 'react';
import { Lead } from '../types';

interface UseLeadsDataReturn {
  leads: Lead[];
  loading: boolean;
  isPolling: boolean;
  error: string | null;
  totalCount: number;
  refetch: () => void;
  lastSync: Date | null;
}

const POLL_INTERVAL_MS = 10 * 1000; // 10 seconds


/** Stable numeric hash from a string (no randomness). */
const stableHash = (str: string): number => {
  let h = 0;
  for (let i = 0; i < str.length; i++) {
    h = (Math.imul(31, h) + str.charCodeAt(i)) | 0;
  }
  return Math.abs(h);
};

const mapBackendLeadToFrontend = (lead: any, idx: number): Lead => {
  // --- Region: derived from branch / city / state ---
  const state = (lead.state || lead.city || lead.assigned_to?.branch_name || '').toLowerCase();
  let region = 'South';
  if (state.includes('delhi') || state.includes('chandigarh') || state.includes('haryana') || state.includes('punjab') || state.includes('uttar pradesh')) region = 'North';
  else if (state.includes('mumbai') || state.includes('pune') || state.includes('gujarat') || state.includes('maharashtra') || state.includes('goa') || state.includes('madhya pradesh') || state.includes('rajasthan')) region = 'West';
  else if (state.includes('kolkata') || state.includes('bhubaneswar') || state.includes('odisha') || state.includes('bihar') || state.includes('west bengal') || state.includes('assam')) region = 'East';
  else if (idx % 4 === 0) region = 'North';
  else if (idx % 4 === 1) region = 'West';
  else if (idx % 4 === 2) region = 'East';

  // --- Industry: derived from lending_type ---
  const lendingType = (lead.product_subcategory || lead.lending_type || lead.loan_type || '').toLowerCase();
  let industry = 'Fintech';
  if (lendingType.includes('health') || lendingType.includes('wellness')) industry = 'Healthcare';
  else if (lendingType.includes('home')) industry = 'E-Commerce';
  else if (lendingType.includes('education') || lendingType.includes('edu')) industry = 'EdTech';
  else if (lendingType.includes('sme') || lendingType.includes('business') || lendingType.includes('msme')) industry = 'SaaS';
  else if (lendingType.includes('gold')) industry = 'Manufacturing';
  else if (lendingType.includes('personal')) industry = 'Logistics';

  // --- Plan: derived from lending type ---
  const plans = ['Starter', 'Pro', 'Business', 'Enterprise'];
  let planIdx = idx % plans.length;
  if (lendingType.includes('business') || lendingType.includes('sme')) planIdx = 2;
  else if (lendingType.includes('home') || lendingType.includes('lap')) planIdx = 3;
  else if (lendingType.includes('gold') || lendingType.includes('personal')) planIdx = 1;

  // --- Status: preserve real database status ---
  const status = (lead.status || 'DRAFT').toUpperCase();

  // --- Health Score: derived from real status (no random) ---
  const healthMap: Record<string, number> = {
    CONVERTED: 92, DISBURSED: 90, APPROVED: 88, INTERESTED: 75,
    UNDER_REVIEW: 72, CONTACTED: 68, NEW: 70, NEW_LEAD: 65,
    CLOSED_LOST: 28, REJECTED: 25, NPA: 15, BAD_STANDING: 20,
    APPLICATION_CREATED: 75, ACTIVE: 85
  };
  const health_score = healthMap[status] ?? 60;

  // --- Revenue: derived from lending_type (no random) ---
  const revenueMap: Record<string, number> = {
    'home loan': 125000, 'home': 125000,
    'business loan': 85000, 'business': 85000, 'sme': 95000, 'msme': 78000,
    'personal loan': 42000, 'personal': 42000,
    'gold loan': 35000, 'gold': 35000,
    'lap': 110000, 'education': 55000,
  };
  let revenue = 50000;
  for (const [key, val] of Object.entries(revenueMap)) {
    if (lendingType.includes(key)) { revenue = val; break; }
  }

  // --- Other numeric fields: stable hash from lead_id (deterministic, not random) ---
  const leadId = lead.id || lead.lead_id || lead.uuid || (idx + 1);
  const seed = stableHash(String(leadId));
  const ai_requests = 200 + (seed % 4800);
  const users = 5 + (seed % 145);
  const projects = 1 + (seed % 9);
  const storage = 2 + (seed % 78);

  // --- Name / Contact ---
  const clientName = lead.customer_name || lead.first_name || lead.account?.first_name || `Lead ${idx + 1}`;
  const clientPhone = lead.contact_number || lead.phone || lead.account?.phone_no || '';
  const clientEmail = lead.email_address || lead.email || lead.account?.email_id || `client-${idx + 1}@manipalfintech.com`;
  const clientOrg = lead.lending_partner || lead.lender_name || lead.lender?.lender_name || 'Manipal Fintech Sourced';

  return {
    id: leadId,
    name: clientName,
    email: clientEmail,
    phone: clientPhone,
    organization: clientOrg,
    industry,
    plan: plans[planIdx] as any,
    status,
    created_at: lead.created_at || new Date().toISOString(),
    updated_at: lead.updated_at || new Date().toISOString(),
    region,
    city: lead.city || lead.state || 'Unknown',
    ai_requests,
    health_score,
    revenue,
    users,
    projects,
    storage,
    last_active: lead.updated_at || lead.created_at || new Date().toISOString(),
    product_subcategory: lead.product_subcategory || lead.lending_type || 'Unknown',
  };
};


export const useLeadsData = (): UseLeadsDataReturn => {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [isPolling, setIsPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [lastSync, setLastSync] = useState<Date | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchLeads = useCallback(async (background = false) => {
    if (background) {
      setIsPolling(true);
    } else {
      setLoading(true);
    }
    setError(null);

    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    const apiKey = import.meta.env.VITE_DASHBOARD_API_KEY || '';

    try {
      let currentUrl: string | null = `${baseUrl}/api/v2/onboarding/leads/list/`;
      const allRawLeads: any[] = [];
      let apiTotalCount = 0;

      while (currentUrl) {
        const response = await fetch(currentUrl, {
          headers: {
            'X-Dashboard-API-Key': apiKey,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`API returned ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        const pageLeads = data?.data?.results?.leads || data?.data?.leads || data?.results?.leads || data?.results || [];
        apiTotalCount = data?.data?.count ?? data?.count ?? apiTotalCount;

        for (const item of pageLeads) {
          allRawLeads.push(item);
        }

        const rawNext: string | null = data?.data?.next ?? data?.next ?? null;
        if (rawNext) {
          try {
            const parsedNext = new URL(rawNext, baseUrl);
            const baseParsed = new URL(baseUrl);
            parsedNext.protocol = baseParsed.protocol;
            parsedNext.host = baseParsed.host;
            currentUrl = parsedNext.toString();
          } catch {
            currentUrl = rawNext;
          }
        } else {
          currentUrl = null;
        }
      }

      // Deduplicate by lead ID / UUID
      const uniqueRawLeads: any[] = [];
      const seenIds = new Set<string | number>();

      for (const item of allRawLeads) {
        const itemKey = item.id || item.lead_id || item.uuid;
        if (itemKey != null) {
          if (!seenIds.has(itemKey)) {
            seenIds.add(itemKey);
            uniqueRawLeads.push(item);
          }
        } else {
          uniqueRawLeads.push(item);
        }
      }

      const enriched = uniqueRawLeads.map((lead: any, idx: number) => mapBackendLeadToFrontend(lead, idx));

      setLeads(enriched);
      setTotalCount(apiTotalCount || enriched.length);
      setLastSync(new Date());
    } catch (err: any) {
      console.error('[LeadsData] Failed to fetch leads from Django backend:', err.message);
      setError(`Failed to fetch live data: ${err.message}`);
      setLastSync(new Date());
    } finally {
      setLoading(false);
      setIsPolling(false);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Initial fetch + polling
  useEffect(() => {
    fetchLeads(false);

    timerRef.current = setInterval(() => {
      fetchLeads(true);
    }, POLL_INTERVAL_MS);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [fetchLeads]);

  return { leads, loading, isPolling, error, totalCount, refetch: () => fetchLeads(false), lastSync };
};

