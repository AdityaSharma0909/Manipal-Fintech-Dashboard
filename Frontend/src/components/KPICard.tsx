import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area } from 'recharts';

interface KPICardProps {
  title: string;
  value: string;
  change?: number;
  description: string;
  icon: React.ReactNode;
  iconBg: string;
  sparkline?: number[];
  sparkColor?: string;
  badge?: string;
  badgeColor?: string;
  darkMode: boolean;
  delay?: number;
}

const KPICard: React.FC<KPICardProps> = ({
  title, value, change, description, icon, iconBg, sparkline, sparkColor, badge, badgeColor, darkMode
}) => {
  const hasBottomRow = change !== undefined || (sparkline !== undefined && sparkline.length > 0);
  const positive = change !== undefined ? change >= 0 : true;
  const sparkData = sparkline ? sparkline.map((v, i) => ({ v, i })) : [];

  return (
    <div className={`group relative rounded-2xl p-5 border transition-all duration-300 hover:-translate-y-1 hover:shadow-lg cursor-pointer overflow-hidden ${
      darkMode
        ? 'bg-gray-900/40 border-gray-800 hover:border-brand-blue/50 hover:shadow-brand-blue/5'
        : 'bg-white border-gray-200/60 hover:border-brand-blue/30 hover:shadow-brand-blue/5'
    }`}>
      {/* Subtle gradient overlay */}
      <div className={`absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 ${
        darkMode ? 'bg-gradient-to-br from-brand-blue/5 to-brand-gold/5' : 'bg-gradient-to-br from-brand-blue/5 to-brand-gold/5'
      } rounded-2xl`} />

      <div className="relative">
        {/* Top row */}
        <div className="flex items-start justify-between mb-3">
          <div className={`w-10 h-10 rounded-xl ${iconBg} flex items-center justify-center shadow-sm flex-shrink-0`}>
            {icon}
          </div>
          {badge && (
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${badgeColor}`}>{badge}</span>
          )}
        </div>

        {/* Value */}
        <div className="mb-1">
          <span className={`text-2xl font-bold tracking-tight ${darkMode ? 'text-white' : 'text-gray-900'}`}>{value}</span>
        </div>

        <p className={`text-xs font-medium mb-0.5 ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>{title}</p>
        <p className={`text-xs ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>{description}</p>

        {/* Bottom row */}
        {hasBottomRow && (
          <div className="flex items-end justify-between mt-3 pt-3 border-t border-dashed" style={{ borderColor: darkMode ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)' }}>
            {change !== undefined && (
              <div className={`flex items-center gap-1 text-xs font-semibold ${positive ? 'text-emerald-500' : 'text-rose-500'}`}>
                {positive ? <TrendingUp size={13} /> : <TrendingDown size={13} />}
                <span>{positive ? '+' : ''}{change}%</span>
                <span className={`font-normal ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>vs last month</span>
              </div>
            )}
            {sparkline && sparkline.length > 0 && sparkColor && (
              <div className="w-20 h-8">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={sparkData} margin={{ top: 2, right: 0, bottom: 2, left: 0 }}>
                    <defs>
                      <linearGradient id={`spark-${sparkColor.replace('#', '')}`} x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={sparkColor} stopOpacity={0.3} />
                        <stop offset="95%" stopColor={sparkColor} stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <Area
                      type="monotone"
                      dataKey="v"
                      stroke={sparkColor}
                      strokeWidth={1.5}
                      fill={`url(#spark-${sparkColor.replace('#', '')})`}
                      dot={false}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default KPICard;
