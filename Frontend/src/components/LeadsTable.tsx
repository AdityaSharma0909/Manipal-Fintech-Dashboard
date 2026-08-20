import React, { useState, useMemo } from 'react';
import { Search, ChevronUp, ChevronDown, ChevronLeft, ChevronRight, Download, Filter, MoreHorizontal, TrendingUp } from 'lucide-react';
import { Lead, Application } from '../types';

interface LeadsTableProps {
  leads: Lead[];
  applications?: Application[];
  darkMode: boolean;
  loading?: boolean;
  totalCount?: number;
  onSelectCustomer?: (lead: Lead) => void;
}

const statusColors: Record<string, string> = {
  ACTIVE: 'bg-emerald-100 text-emerald-700 border-emerald-200',
  APPLICATION_CREATED: 'bg-blue-100 text-blue-700 border-blue-200',
  DISBURSED: 'bg-indigo-100 text-indigo-700 border-indigo-200',
  DISBURSEMENT_READY: 'bg-indigo-100 text-indigo-700 border-indigo-200',
  BT_FUND_DISBURSED: 'bg-indigo-100 text-indigo-700 border-indigo-200',
  REJECTED: 'bg-rose-100 text-rose-700 border-rose-200',
  REJECTED_BY_UNDERWRITING: 'bg-rose-100 text-rose-700 border-rose-200',
  APPLICATION_REJECTED_BY_BRANCH_EXECUTIVE: 'bg-rose-100 text-rose-700 border-rose-200',
  DRAFT: 'bg-gray-100 text-gray-700 border-gray-200',
  // legacy mock fallbacks
  Active: 'bg-emerald-100 text-emerald-700 border-emerald-200',
  Trial: 'bg-blue-100 text-blue-700 border-blue-200',
  'At Risk': 'bg-amber-100 text-amber-700 border-amber-200',
  Churned: 'bg-rose-100 text-rose-700 border-rose-200',
};

const planColors: Record<string, string> = {
  Starter: 'bg-gray-100 text-gray-600',
  Pro: 'bg-purple-100 text-purple-700',
  Business: 'bg-blue-100 text-brand-blue dark:bg-brand-blue/15 dark:text-blue-300',
  Enterprise: 'bg-gradient-to-r from-brand-blue to-blue-500 text-white shadow-sm',
};

type SortKey = keyof Lead;

const LeadsTable: React.FC<LeadsTableProps> = ({ leads, applications = [], darkMode, loading }) => {
  const [search, setSearch] = useState('');
  const [sortKey, setSortKey] = useState<SortKey>('created_at');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState('All');
  const pageSize = 8;

  const filtered = useMemo(() => {
    let data = [...leads];

    if (statusFilter !== 'All') {
      const sf = statusFilter.toUpperCase();
      data = data.filter((l) => {
        const leadSt = (l.status || '').toUpperCase();
        const appSt = ((l as any).application_status || '').toUpperCase();

        if (sf === 'DISBURSED') {
          return leadSt.includes('DISBURS') || appSt.includes('DISBURS') || leadSt === 'DISBURSED';
        }
        if (sf === 'REJECTED') {
          return leadSt.includes('REJECT') || appSt.includes('REJECT') || leadSt === 'REJECTED';
        }
        if (sf === 'APPLICATION_CREATED') {
          return leadSt === 'APPLICATION_CREATED' || Boolean(l.application_id) || appSt.length > 0;
        }
        return leadSt === sf || appSt === sf;
      });

      // If DISBURSED or REJECTED status filter is selected, include matching records from applications list
      if ((sf === 'DISBURSED' || sf === 'REJECTED') && applications.length > 0) {
        const matchingApps = applications.filter((a) => {
          const ast = (a.status || '').toUpperCase();
          if (sf === 'DISBURSED') return ast.includes('DISBURS') || ast === 'DISBURSED';
          if (sf === 'REJECTED') return ast.includes('REJECT') || ast === 'REJECTED';
          return ast === sf;
        });

        const appLeads: Lead[] = matchingApps.map((a) => ({
          id: a.application_id,
          lead_code: a.lead_code || a.application_id,
          name: a.name || `Applicant ${a.application_id}`,
          email: a.email_address || 'N/A',
          phone: a.mobile_number || 'N/A',
          product_category: a.product_category || 'Loan',
          product_subcategory: a.product_subcategory || a.loan_type || 'Gold Loan',
          status: a.status || sf,
          created_at: a.date || new Date().toISOString(),
          amount: a.amount || a.disbursed_amount || 0,
          lending_partner: a.lending_partner || 'AXIS',
          organization: a.lending_partner || 'Fintech Partner',
          industry: a.loan_type || 'Loan',
          plan: 'Enterprise',
          region: a.state || 'Karnataka',
          health_score: sf === 'DISBURSED' ? 95 : 45,
          revenue: a.disbursed_amount || a.amount || 0,
          ai_requests: 10,
        }));

        const existingIds = new Set(data.map((d) => d.id));
        appLeads.forEach((al) => {
          if (!existingIds.has(al.id)) {
            data.push(al);
          }
        });
      }
    }

    if (search) {
      const q = search.toLowerCase();
      data = data.filter(
        (l) =>
          l.name?.toLowerCase().includes(q) ||
          l.email?.toLowerCase().includes(q) ||
          l.organization?.toLowerCase().includes(q) ||
          l.city?.toLowerCase().includes(q) ||
          l.status?.toLowerCase().includes(q) ||
          l.lending_partner?.toLowerCase().includes(q)
      );
    }

    return data.sort((a, b) => {
      const av = a[sortKey] ?? '';
      const bv = b[sortKey] ?? '';
      const cmp = String(av).localeCompare(String(bv), undefined, { numeric: true });
      return sortDir === 'asc' ? cmp : -cmp;
    });
  }, [leads, applications, search, sortKey, sortDir, statusFilter]);


  const pages = Math.ceil(filtered.length / pageSize);
  const paged = filtered.slice((page - 1) * pageSize, page * pageSize);

  const sort = (key: SortKey) => {
    if (sortKey === key) setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    else { setSortKey(key); setSortDir('desc'); }
  };

  const SortIcon = ({ k }: { k: SortKey }) => (
    <span className="ml-1 inline-flex flex-col">
      {sortKey === k ? (sortDir === 'asc' ? <ChevronUp size={10} /> : <ChevronDown size={10} />) : <ChevronDown size={10} className="opacity-30" />}
    </span>
  );

  const exportCSV = () => {
    const headers = ['Lead ID', 'Lead Code', 'Customer Name', 'Phone', 'Email', 'Product Category', 'Product Subcategory', 'Lead Type', 'Lending Partner', 'Amount (INR)', 'Status', 'State', 'Created At'];
    const rows = filtered.map(l => [
      `"${l.id || ''}"`,
      `"${l.lead_code || ''}"`,
      `"${(l.name || '').replace(/"/g, '""')}"`,
      `"${l.phone || ''}"`,
      `"${l.email || ''}"`,
      `"${l.product_category || ''}"`,
      `"${l.product_subcategory || ''}"`,
      `"${l.lead_type || ''}"`,
      `"${l.lending_partner || ''}"`,
      l.amount || 0,
      `"${l.status || ''}"`,
      `"${l.state || ''}"`,
      `"${l.created_at || ''}"`
    ]);
    const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `manipal_leads_export_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className={`rounded-2xl border overflow-hidden ${darkMode ? 'bg-gray-800/60 border-gray-700' : 'bg-white border-gray-100'}`}>
      {/* Table Header Controls */}
      <div className={`flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 px-5 py-4 border-b ${darkMode ? 'border-gray-700' : 'border-gray-100'}`}>
        <div>
          <h3 className={`text-sm font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>Customer Intelligence</h3>
          <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>{filtered.length} records</p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {/* Status Filter */}
          {['All', 'ACTIVE', 'APPLICATION_CREATED', 'DISBURSED', 'REJECTED'].map(s => (
            <button
              key={s}
              onClick={() => { setStatusFilter(s); setPage(1); }}
              className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${
                statusFilter === s
                  ? 'bg-brand-blue text-white shadow-sm'
                  : darkMode ? 'bg-gray-800 text-gray-300 hover:bg-gray-700' : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
              }`}
            >{s}</button>
          ))}
          <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs ${darkMode ? 'bg-gray-700 border-gray-600 text-gray-300' : 'bg-gray-50 border-gray-200 text-gray-500'}`}>
            <Search size={12} />
            <input
              value={search}
              onChange={e => { setSearch(e.target.value); setPage(1); }}
              placeholder="Search..."
              className="bg-transparent outline-none w-28"
            />
          </div>
          <button onClick={exportCSV} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium border transition-all ${darkMode ? 'border-gray-600 text-gray-300 hover:bg-gray-700' : 'border-gray-200 text-gray-600 hover:bg-gray-50'}`}>
            <Download size={12} /> Export
          </button>
          <button
            onClick={() => setStatusFilter(statusFilter === 'All' ? 'ACTIVE' : 'All')}
            title="Toggle Filter"
            className={`p-1.5 rounded-xl border transition-all cursor-pointer ${
              statusFilter !== 'All'
                ? 'border-brand-blue bg-blue-50 text-brand-blue'
                : darkMode ? 'border-gray-600 text-gray-300 hover:bg-gray-700' : 'border-gray-200 text-gray-600 hover:bg-gray-50'
            }`}
          >
            <Filter size={12} />
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className={darkMode ? 'bg-gray-700/40' : 'bg-gray-50'}>
              {[
                { key: 'name' as SortKey, label: 'Customer' },
                { key: 'organization' as SortKey, label: 'Organization' },
                { key: 'industry' as SortKey, label: 'Industry' },
                { key: 'plan' as SortKey, label: 'Plan' },
                { key: 'status' as SortKey, label: 'Status' },
                { key: 'region' as SortKey, label: 'Region' },
                { key: 'health_score' as SortKey, label: 'Health' },
                { key: 'revenue' as SortKey, label: 'Revenue' },
                { key: 'ai_requests' as SortKey, label: 'AI Reqs' },
              ].map(col => (
                <th
                  key={col.key}
                  onClick={() => sort(col.key)}
                  className={`px-4 py-3 text-left font-semibold cursor-pointer select-none whitespace-nowrap transition-colors ${
                    darkMode ? 'text-gray-300 hover:text-white' : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {col.label}<SortIcon k={col.key} />
                </th>
              ))}
              <th className={`px-4 py-3 text-left font-semibold ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}></th>
            </tr>
          </thead>
          <tbody>
            {loading && leads.length === 0 ? (
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i}>
                  {Array.from({ length: 10 }).map((_, j) => (
                    <td key={j} className="px-4 py-3">
                      <div className={`h-3 rounded-full animate-pulse ${darkMode ? 'bg-gray-700' : 'bg-gray-100'}`} style={{ width: `${40 + Math.random() * 60}%` }} />
                    </td>
                  ))}
                </tr>
              ))
            ) : paged.map((lead, i) => (
              <tr
                key={lead.id}
                className={`transition-colors border-t group ${
                  darkMode ? 'border-gray-800/50 hover:bg-gray-850/20' : 'border-gray-100/50 hover:bg-blue-50/20'
                }`}
              >
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className={`w-7 h-7 rounded-lg text-white text-xs font-bold flex items-center justify-center flex-shrink-0`}
                      style={{ background: `hsl(${(i * 47) % 360}, 65%, 55%)` }}>
                      {lead.name?.slice(0, 1) ?? '?'}
                    </div>
                    <div>
                      <p className={`font-medium ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>{lead.name}</p>
                      <p className={`text-gray-400 text-xs`}>{lead.email?.split('@')[0]}...</p>
                    </div>
                  </div>
                </td>
                <td className={`px-4 py-3 font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>{lead.organization ?? '—'}</td>
                <td className={`px-4 py-3 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>{lead.industry ?? '—'}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded-md text-xs font-medium ${planColors[lead.plan ?? ''] ?? 'bg-gray-100 text-gray-600'}`}>
                    {lead.plan ?? '—'}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${
                    (darkMode ? 'border-opacity-30 ' : '') + (statusColors[lead.status ?? ''] ?? 'bg-gray-100 text-gray-600 border-gray-200')
                  }`}>{lead.status ?? '—'}</span>
                </td>
                <td className={`px-4 py-3 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>{lead.region ?? '—'}</td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1.5">
                    <div className={`h-1.5 w-16 rounded-full ${darkMode ? 'bg-gray-700' : 'bg-gray-100'} overflow-hidden`}>
                      <div
                        className="h-full rounded-full"
                        style={{
                          width: `${lead.health_score ?? 0}%`,
                          background: (lead.health_score ?? 0) >= 80 ? '#10b981' : (lead.health_score ?? 0) >= 65 ? '#f59e0b' : '#ef4444'
                        }}
                      />
                    </div>
                    <span className={`text-xs font-medium ${(lead.health_score ?? 0) >= 80 ? 'text-emerald-500' : (lead.health_score ?? 0) >= 65 ? 'text-amber-500' : 'text-rose-500'}`}>
                      {lead.health_score ?? '—'}
                    </span>
                  </div>
                </td>
                <td className={`px-4 py-3 font-medium ${darkMode ? 'text-gray-200' : 'text-gray-700'}`}>
                  ₹{((lead.revenue ?? 0) / 1000).toFixed(1)}K
                </td>
                <td className={`px-4 py-3 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                  <div className="flex items-center gap-1">
                    <TrendingUp size={10} className="text-brand-blue" />
                    {(lead.ai_requests ?? 0).toLocaleString()}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => alert(`Customer Details for ${lead.name}:\n• Organization: ${lead.organization || 'N/A'}\n• Email: ${lead.email || 'N/A'}\n• Status: ${lead.status}`)}
                    className={`opacity-0 group-hover:opacity-100 p-1 rounded-lg transition-all cursor-pointer ${darkMode ? 'hover:bg-gray-600 text-gray-400' : 'hover:bg-gray-100 text-gray-400'}`}
                  >
                    <MoreHorizontal size={14} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className={`flex items-center justify-between px-5 py-3 border-t ${darkMode ? 'border-gray-700' : 'border-gray-100'}`}>
        <span className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
          Showing {Math.min((page - 1) * pageSize + 1, filtered.length)}–{Math.min(page * pageSize, filtered.length)} of {filtered.length}
        </span>
        <div className="flex items-center gap-1">
          <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}
            className={`p-1.5 rounded-lg transition-all ${darkMode ? 'text-gray-400 hover:bg-gray-700 disabled:opacity-30' : 'text-gray-400 hover:bg-gray-100 disabled:opacity-30'}`}>
            <ChevronLeft size={14} />
          </button>
          {Array.from({ length: Math.min(pages, 5) }, (_, i) => i + 1).map(p => (
            <button key={p} onClick={() => setPage(p)}
              className={`w-7 h-7 rounded-lg text-xs font-medium transition-all ${
                page === p ? 'bg-brand-blue text-white shadow-sm' : darkMode ? 'text-gray-400 hover:bg-gray-700' : 'text-gray-500 hover:bg-gray-100'
              }`}>{p}</button>
          ))}
          <button onClick={() => setPage(p => Math.min(pages, p + 1))} disabled={page === pages}
            className={`p-1.5 rounded-lg transition-all ${darkMode ? 'text-gray-400 hover:bg-gray-700 disabled:opacity-30' : 'text-gray-400 hover:bg-gray-100 disabled:opacity-30'}`}>
            <ChevronRight size={14} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default LeadsTable;
