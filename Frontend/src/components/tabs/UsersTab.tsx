import React, { useState } from 'react';
import { Employee, ComprehensiveDashboardStats } from '../../types';
import { Users, UserCheck, ShieldCheck, Building2, TrendingUp, Search, Award, Info } from 'lucide-react';
import KPICard from '../KPICard';

interface UsersTabProps {
  employees?: Employee[];
  stats: ComprehensiveDashboardStats | null;
  darkMode: boolean;
  loading: boolean;
}

const UsersTab: React.FC<UsersTabProps> = ({ employees = [], stats, darkMode, loading }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('ALL');

  const empStats = stats?.employeesStats;
  const employeeList = stats?.employeesList && stats.employeesList.length > 0 ? stats.employeesList : employees;

  const filteredEmployees = employeeList.filter((emp) => {
    const name = `${emp.first_name || ''} ${emp.last_name || ''}`.toLowerCase();
    const matchesSearch =
      name.includes(searchTerm.toLowerCase()) ||
      (emp.username || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (emp.employee_id || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (emp.phone || '').includes(searchTerm);

    const matchesRole = roleFilter === 'ALL' || emp.role === roleFilter;

    return matchesSearch && matchesRole;
  });

  const totalEmployees = empStats?.total || employeeList.length;
  const activeEmployees = empStats?.active || employeeList.filter((e) => e.is_active).length;
  const salesOfficersCount = empStats?.salesOfficersCount || 0;
  const branchManagersCount = empStats?.branchManagersCount || 0;

  return (
    <div className="space-y-6">
      {/* ── Top Employee KPIs with Data Source Attribution ──────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Total Staff / Employees"
          value={totalEmployees}
          description="Registered employees in workforce"
          icon="Users"
          color="blue"
          apiEndpoint="/user/employee"
          darkMode={darkMode}
        />
        <KPICard
          title="Active Employees"
          value={activeEmployees}
          description={`${totalEmployees - activeEmployees} inactive staff members`}
          icon="UserCheck"
          color="emerald"
          apiEndpoint="/user/employee"
          darkMode={darkMode}
        />
        <KPICard
          title="Sales Officers (SO)"
          value={salesOfficersCount}
          description="Field sales & origination officers"
          icon="Award"
          color="indigo"
          apiEndpoint="/user/by_role/ (or /user/employee)"
          darkMode={darkMode}
        />
        <KPICard
          title="Managers & Regional Heads"
          value={branchManagersCount}
          description="Branch & regional head leadership"
          icon="ShieldCheck"
          color="purple"
          apiEndpoint="/user/by_role/ (or /user/employee)"
          darkMode={darkMode}
        />
      </div>

      {/* ── Role & Branch Distribution Grid ──────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Role Breakdown */}
        <div className={`p-5 rounded-2xl border flex flex-col justify-between ${darkMode ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200'} shadow-sm`}>
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className={`text-sm font-bold flex items-center gap-2 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                <ShieldCheck size={16} className="text-purple-500" />
                Role Hierarchy Distribution
              </h3>
              <div className="relative group/tooltip">
                <Info size={14} className={`${darkMode ? 'text-gray-500 group-hover/tooltip:text-gray-300' : 'text-gray-400 group-hover/tooltip:text-gray-600'} transition-colors cursor-pointer`} />
                <div className={`absolute right-0 top-full mt-1.5 hidden group-hover/tooltip:flex flex-col whitespace-nowrap z-50 px-2.5 py-1 rounded-lg text-[10px] font-mono shadow-xl border pointer-events-none ${
                  darkMode ? 'bg-gray-800 border-gray-700 text-gray-200' : 'bg-gray-900 border-gray-800 text-white'
                }`}>
                  <span className="text-[9px] text-gray-400 font-sans uppercase font-bold tracking-wider">Data Source</span>
                  <span>/user/by_role/ & /user/employee</span>
                </div>
              </div>
            </div>
            <div className="space-y-3">
              {(empStats?.byRole || []).map((r) => {
                const pct = totalEmployees > 0 ? Math.round((r.count / totalEmployees) * 100) : 0;
                return (
                  <div key={r.role} className="space-y-1">
                    <div className="flex justify-between text-xs font-semibold">
                      <span className={darkMode ? 'text-gray-300' : 'text-gray-700'}>{r.role}</span>
                      <span className={darkMode ? 'text-gray-400' : 'text-gray-500'}>
                        {r.count} staff ({pct}%)
                      </span>
                    </div>
                    <div className={`h-2 rounded-full overflow-hidden ${darkMode ? 'bg-gray-800' : 'bg-gray-100'}`}>
                      <div className="h-full bg-purple-500" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Branch Allocation */}
        <div className={`p-5 rounded-2xl border flex flex-col justify-between ${darkMode ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200'} shadow-sm`}>
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className={`text-sm font-bold flex items-center gap-2 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                <Building2 size={16} className="text-blue-500" />
                Branch Staff Allocation
              </h3>
              <div className="relative group/tooltip">
                <Info size={14} className={`${darkMode ? 'text-gray-500 group-hover/tooltip:text-gray-300' : 'text-gray-400 group-hover/tooltip:text-gray-600'} transition-colors cursor-pointer`} />
                <div className={`absolute right-0 top-full mt-1.5 hidden group-hover/tooltip:flex flex-col whitespace-nowrap z-50 px-2.5 py-1 rounded-lg text-[10px] font-mono shadow-xl border pointer-events-none ${
                  darkMode ? 'bg-gray-800 border-gray-700 text-gray-200' : 'bg-gray-900 border-gray-800 text-white'
                }`}>
                  <span className="text-[9px] text-gray-400 font-sans uppercase font-bold tracking-wider">Data Source</span>
                  <span>/user/employee</span>
                </div>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3 max-h-48 overflow-y-auto pr-1">
              {(empStats?.byBranch || []).map((b) => (
                <div key={b.branch} className={`flex items-center justify-between p-2.5 rounded-lg border text-xs ${
                  darkMode ? 'bg-gray-800/30 border-gray-700 text-gray-300' : 'bg-gray-50 border-gray-200 text-gray-700'
                }`}>
                  <span className="font-semibold truncate max-w-[120px]">{b.branch}</span>
                  <span className="font-bold px-2 py-0.5 rounded bg-brand-blue/10 text-brand-blue">{b.count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* ── Employee Performance Roster Table ────────────────────────── */}
      <div className={`p-5 rounded-2xl border ${darkMode ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200'} shadow-sm`}>
        <div className="flex items-center justify-between flex-wrap gap-4 mb-4">
          <div>
            <div className="flex items-center gap-2">
              <h3 className={`text-base font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>Employee Roster & Conversions</h3>
              <div className="relative group/tooltip">
                <Info size={14} className={`${darkMode ? 'text-gray-500 group-hover/tooltip:text-gray-300' : 'text-gray-400 group-hover/tooltip:text-gray-600'} transition-colors cursor-pointer`} />
                <div className={`absolute left-0 top-full mt-1.5 hidden group-hover/tooltip:flex flex-col whitespace-nowrap z-50 px-2.5 py-1 rounded-lg text-[10px] font-mono shadow-xl border pointer-events-none ${
                  darkMode ? 'bg-gray-800 border-gray-700 text-gray-200' : 'bg-gray-900 border-gray-800 text-white'
                }`}>
                  <span className="text-[9px] text-gray-400 font-sans uppercase font-bold tracking-wider">Data Source</span>
                  <span>/user/employee & /user/employee/applications</span>
                </div>
              </div>
            </div>
            <p className={`text-xs mt-0.5 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
              Showing {filteredEmployees.length} of {totalEmployees} employee records
            </p>
          </div>

          <div className="flex items-center gap-3 flex-wrap">
            <input
              type="text"
              placeholder="Search employee, username, phone..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className={`px-3 py-1.5 rounded-xl border text-xs font-medium focus:outline-none ${
                darkMode ? 'bg-gray-800 border-gray-700 text-white placeholder-gray-500' : 'bg-white border-gray-300 text-gray-900'
              }`}
            />
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className={`px-3 py-1.5 rounded-xl border text-xs font-medium focus:outline-none ${
                darkMode ? 'bg-gray-800 border-gray-700 text-white' : 'bg-white border-gray-300 text-gray-900'
              }`}
            >
              <option value="ALL">All Roles</option>
              <option value="SALES_OFFICER">SALES_OFFICER</option>
              <option value="BRANCH_MANAGER">BRANCH_MANAGER</option>
              <option value="REGIONAL_HEAD">REGIONAL_HEAD</option>
              <option value="CREDIT_OFFICER">CREDIT_OFFICER</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className={`border-b text-[11px] font-semibold uppercase tracking-wider ${darkMode ? 'border-gray-800 text-gray-400' : 'border-gray-200 text-gray-500'}`}>
                <th className="py-3 px-3">Employee Name</th>
                <th className="py-3 px-3">Role</th>
                <th className="py-3 px-3">Branch</th>
                <th className="py-3 px-3">Contact</th>
                <th className="py-3 px-3">Leads Handled</th>
                <th className="py-3 px-3">Apps Handled</th>
                <th className="py-3 px-3">Disbursed Apps</th>
                <th className="py-3 px-3">Conversion Rate</th>
                <th className="py-3 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y text-xs font-medium">
              {filteredEmployees.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-gray-500">
                    No employees matching filters found.
                  </td>
                </tr>
              ) : (
                filteredEmployees.map((emp) => {
                  const name = `${emp.first_name || ''} ${emp.last_name || ''}`.trim() || emp.username;
                  const leadsHandled = (emp as any).leadsHandled || 0;
                  const appsHandled = (emp as any).appsHandled || 0;
                  const disbursedApps = (emp as any).disbursedApps || 0;
                  const convRate = (emp as any).conversionRate || 0;

                  return (
                    <tr key={emp.user_id} className={`hover:bg-brand-blue/5 transition-colors ${darkMode ? 'border-gray-800 text-gray-300' : 'border-gray-100 text-gray-800'}`}>
                      <td className="py-3 px-3">
                        <div className="font-bold text-brand-blue">{name}</div>
                        <div className="text-[10px] text-gray-500">Code: {emp.employee_id || emp.username}</div>
                      </td>
                      <td className="py-3 px-3">
                        <span className="px-2 py-0.5 rounded bg-purple-500/10 text-purple-600 font-bold text-[10px]">
                          {emp.role}
                        </span>
                      </td>
                      <td className="py-3 px-3">{emp.branch_name || 'Main Branch'}</td>
                      <td className="py-3 px-3 font-mono">{emp.phone || 'N/A'}</td>
                      <td className="py-3 px-3 font-bold text-blue-600">{leadsHandled}</td>
                      <td className="py-3 px-3 font-bold text-purple-600">{appsHandled}</td>
                      <td className="py-3 px-3 font-bold text-emerald-600">{disbursedApps}</td>
                      <td className="py-3 px-3">
                        <div className="flex items-center gap-1 font-bold text-emerald-600">
                          <TrendingUp size={12} /> {convRate}%
                        </div>
                      </td>
                      <td className="py-3 px-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          emp.is_active !== false ? 'bg-emerald-500/10 text-emerald-600' : 'bg-gray-500/10 text-gray-500'
                        }`}>
                          {emp.is_active !== false ? 'ACTIVE' : 'INACTIVE'}
                        </span>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default UsersTab;
