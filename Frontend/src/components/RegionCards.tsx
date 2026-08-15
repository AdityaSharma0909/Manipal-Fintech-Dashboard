import React from 'react';
import { TrendingUp, TrendingDown, Users, DollarSign, Heart } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area } from 'recharts';
import { RegionData } from '../types';

interface RegionCardsProps {
  regions: RegionData[];
  darkMode: boolean;
}

const regionColors: Record<string, { icon: string; gradient: string; text: string }> = {
  North: { icon: '⬆️', gradient: 'from-blue-500 to-indigo-500', text: 'text-blue-600' },
  South: { icon: '⬇️', gradient: 'from-emerald-500 to-teal-500', text: 'text-emerald-600' },
  East: { icon: '➡️', gradient: 'from-amber-500 to-orange-500', text: 'text-amber-600' },
  West: { icon: '⬅️', gradient: 'from-purple-500 to-pink-500', text: 'text-purple-600' },
  International: { icon: '🌐', gradient: 'from-rose-500 to-pink-500', text: 'text-rose-600' },
};

const RegionCards: React.FC<RegionCardsProps> = ({ regions, darkMode }) => {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
      {regions.map((region) => {
        const color = regionColors[region.name] || regionColors['North'];
        const trendData = region.trend.map((v, i) => ({ v, i }));
        const isPositive = region.growth >= 0;

        return (
          <div
            key={region.name}
            className={`rounded-2xl p-4 border transition-all duration-300 hover:-translate-y-1 hover:shadow-lg cursor-pointer ${
              darkMode
                ? 'bg-gray-800/60 border-gray-700 hover:border-gray-600'
                : 'bg-white border-gray-100 hover:border-gray-200 hover:shadow-gray-100'
            }`}
          >
            <div className="flex items-center justify-between mb-3">
              <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${color.gradient} flex items-center justify-center shadow-sm`}>
                <span className="text-xs">{region.name === 'International' ? '🌐' : region.name[0]}</span>
              </div>
              <div className={`flex items-center gap-1 text-xs font-semibold ${isPositive ? 'text-emerald-500' : 'text-rose-500'}`}>
                {isPositive ? <TrendingUp size={11} /> : <TrendingDown size={11} />}
                {region.growth}%
              </div>
            </div>

            <p className={`text-xs font-semibold mb-2 ${darkMode ? 'text-white' : 'text-gray-800'}`}>{region.name}</p>

            <div className="space-y-1.5 mb-3">
              <div className="flex items-center justify-between">
                <div className={`flex items-center gap-1 text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                  <Users size={10} />
                  <span>Users</span>
                </div>
                <span className={`text-xs font-medium ${darkMode ? 'text-gray-200' : 'text-gray-700'}`}>{region.users.toLocaleString()}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className={`flex items-center gap-1 text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                  <DollarSign size={10} />
                  <span>Revenue</span>
                </div>
                <span className={`text-xs font-medium ${darkMode ? 'text-gray-200' : 'text-gray-700'}`}>₹{(region.revenue / 1000).toFixed(0)}K</span>
              </div>
              <div className="flex items-center justify-between">
                <div className={`flex items-center gap-1 text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                  <Heart size={10} />
                  <span>Health</span>
                </div>
                <span className={`text-xs font-medium ${region.health >= 80 ? 'text-emerald-500' : region.health >= 70 ? 'text-amber-500' : 'text-rose-500'}`}>{region.health}%</span>
              </div>
            </div>

            <div className="h-8">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trendData} margin={{ top: 2, right: 0, bottom: 2, left: 0 }}>
                  <defs>
                    <linearGradient id={`region-${region.name}`} x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <Area type="monotone" dataKey="v" stroke="#6366f1" strokeWidth={1.5} fill={`url(#region-${region.name})`} dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default RegionCards;
