import React, { useState, useEffect } from 'react';
import {
  Users,
  FileText,
  CheckCircle2,
  TrendingUp,
  TrendingDown,
  Minus,
  DollarSign,
  UserCheck,
  Award,
  ShieldCheck,
  Building2,
  MapPin,
  Layers,
  Clock,
  Info,
  LogIn,
} from 'lucide-react';

export interface KPICardProps {
  title: string;
  value: string | number;
  description?: string;
  icon?: React.ReactNode | string;
  color?: 'blue' | 'indigo' | 'emerald' | 'purple' | 'amber' | 'cyan' | 'rose';
  apiEndpoint?: string;
  change?: number;
  trend?: {
    text: string;
    direction?: 'up' | 'down' | 'neutral';
  };
  sparkline?: number[];
  darkMode?: boolean;
  delayMs?: number;
}


const useAnimatedCounter = (value: string | number, delayMs: number = 0) => {
  const [displayValue, setDisplayValue] = useState<string | number>(value);

  useEffect(() => {
    if (
      typeof window !== 'undefined' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches
    ) {
      setDisplayValue(value);
      return;
    }

    const strVal = String(value ?? '');
    const match = strVal.match(/^([^0-9.]*)([0-9.]+)(.*)$/);
    if (!match) {
      setDisplayValue(value);
      return;
    }

    const prefix = match[1] || '';
    const targetNum = parseFloat(match[2]);
    const suffix = match[3] || '';
    const hasDecimal = match[2].includes('.');
    const decimalPlaces = hasDecimal ? (match[2].split('.')[1] || '').length : 0;

    if (isNaN(targetNum) || targetNum === 0) {
      setDisplayValue(value);
      return;
    }

    let animationFrameId: number;
    let timerId: ReturnType<typeof setTimeout>;

    timerId = setTimeout(() => {
      const duration = 350;
      const startTime = performance.now();

      const animate = (currentTime: number) => {
        const elapsed = currentTime - startTime;
        const progress = Math.min(1, elapsed / duration);
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const currentNum = targetNum * easeOut;

        const formatted = hasDecimal
          ? currentNum.toFixed(decimalPlaces)
          : Math.round(currentNum).toLocaleString();

        setDisplayValue(`${prefix}${formatted}${suffix}`);

        if (progress < 1) {
          animationFrameId = requestAnimationFrame(animate);
        } else {
          setDisplayValue(value);
        }
      };

      animationFrameId = requestAnimationFrame(animate);
    }, delayMs);

    return () => {
      clearTimeout(timerId);
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
    };
  }, [value, delayMs]);

  return displayValue;
};

const getIconElement = (icon: React.ReactNode | string, colorStyle: string) => {
  if (React.isValidElement(icon)) {
    return icon;
  }
  const iconStr = String(icon || '').toLowerCase();
  switch (iconStr) {
    case 'users':
      return <Users className={colorStyle} size={18} />;
    case 'filetext':
    case 'file-text':
      return <FileText className={colorStyle} size={18} />;
    case 'checkcircle':
    case 'check-circle':
    case 'checkcircle2':
      return <CheckCircle2 className={colorStyle} size={18} />;
    case 'trendingup':
    case 'trending-up':
      return <TrendingUp className={colorStyle} size={18} />;
    case 'dollarsign':
    case 'dollar-sign':
      return <DollarSign className={colorStyle} size={18} />;
    case 'usercheck':
    case 'user-check':
      return <UserCheck className={colorStyle} size={18} />;
    case 'award':
      return <Award className={colorStyle} size={18} />;
    case 'shieldcheck':
    case 'shield-check':
      return <ShieldCheck className={colorStyle} size={18} />;
    case 'building2':
      return <Building2 className={colorStyle} size={18} />;
    case 'clock':
      return <Clock className={colorStyle} size={18} />;
    case 'login':
    case 'login-in':
    case 'loginin':
      return <LogIn className={colorStyle} size={18} />;

    default:
      return <Users className={colorStyle} size={18} />;
  }
};

const colorMap = {
  blue: {
    bg: 'bg-blue-500/10 dark:bg-blue-500/20',
    iconColor: 'text-blue-600 dark:text-blue-400',
  },
  indigo: {
    bg: 'bg-indigo-500/10 dark:bg-indigo-500/20',
    iconColor: 'text-indigo-600 dark:text-indigo-400',
  },
  emerald: {
    bg: 'bg-emerald-500/10 dark:bg-emerald-500/20',
    iconColor: 'text-emerald-600 dark:text-emerald-400',
  },
  purple: {
    bg: 'bg-purple-500/10 dark:bg-purple-500/20',
    iconColor: 'text-purple-600 dark:text-purple-400',
  },
  amber: {
    bg: 'bg-amber-500/10 dark:bg-amber-500/20',
    iconColor: 'text-amber-600 dark:text-amber-400',
  },
  cyan: {
    bg: 'bg-cyan-500/10 dark:bg-cyan-500/20',
    iconColor: 'text-cyan-600 dark:text-cyan-400',
  },
  rose: {
    bg: 'bg-rose-500/10 dark:bg-rose-500/20',
    iconColor: 'text-rose-600 dark:text-rose-400',
  },
};

const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  description,
  icon = 'Users',
  color = 'blue',
  apiEndpoint,
  change,
  trend,
  darkMode = false,
  delayMs = 0,
}) => {
  const cStyle = colorMap[color] || colorMap.blue;
  const animatedValue = useAnimatedCounter(value, delayMs);

  return (
    <div
      className={`group relative rounded-2xl p-5 border transition-all duration-300 hover:shadow-md cursor-pointer overflow-hidden ${
        darkMode
          ? 'bg-gray-900/70 border-gray-800 hover:border-gray-700'
          : 'bg-white border-gray-200/80 hover:border-gray-300 shadow-sm'
      }`}
    >
      {/* 1. Header Row: [Icon] → [KPI Title] → [Data Source Info Icon] */}
      <div className="flex items-center justify-between gap-2 mb-3">
        <div className="flex items-center gap-2.5">
          <div className={`w-8 h-8 rounded-xl flex items-center justify-center shadow-xs flex-shrink-0 ${cStyle.bg}`}>
            {getIconElement(icon, cStyle.iconColor)}
          </div>
          <h3 className={`text-xs font-bold uppercase tracking-wider ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
            {title}
          </h3>
        </div>

        {apiEndpoint && (
          <div className="relative group/tooltip">
            <Info size={14} className={`${darkMode ? 'text-gray-500 group-hover/tooltip:text-gray-300' : 'text-gray-400 group-hover/tooltip:text-gray-600'} transition-colors`} />
            <div className={`absolute right-0 top-full mt-1.5 hidden group-hover/tooltip:flex flex-col whitespace-nowrap z-50 px-2.5 py-1 rounded-lg text-[10px] font-mono shadow-xl border pointer-events-none ${
              darkMode ? 'bg-gray-800 border-gray-700 text-gray-200' : 'bg-gray-900 border-gray-800 text-white'
            }`}>
              <span className="text-[9px] text-gray-400 font-sans uppercase font-bold tracking-wider">Data Source</span>
              <span>{apiEndpoint}</span>
            </div>
          </div>
        )}
      </div>

      {/* 2. Main Value */}
      <div className="mb-1">
        <span className={`text-2xl font-extrabold tracking-tight ${darkMode ? 'text-white' : 'text-gray-900'}`}>
          {animatedValue}
        </span>
      </div>

      {/* 3. Short Description */}
      {description && (
        <p className={`text-xs font-medium ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
          {description}
        </p>
      )}

      {/* 4. Trend Indicator */}
      {trend ? (
        <div className="flex items-center gap-1 mt-2 text-xs font-semibold">
          {trend.direction === 'up' && (
            <span className="flex items-center gap-1 text-emerald-500 font-bold">
              <TrendingUp size={12} />
              <span>{trend.text}</span>
            </span>
          )}
          {trend.direction === 'down' && (
            <span className="flex items-center gap-1 text-rose-500 font-bold">
              <TrendingDown size={12} />
              <span>{trend.text}</span>
            </span>
          )}
          {(!trend.direction || trend.direction === 'neutral') && (
            <span className={`flex items-center gap-1 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
              <Minus size={12} />
              <span>{trend.text}</span>
            </span>
          )}
        </div>
      ) : change !== undefined ? (
        <div className="flex items-center gap-1 mt-2 text-xs font-semibold text-emerald-500">
          <TrendingUp size={12} />
          <span>+{change}%</span>
        </div>
      ) : null}
    </div>
  );
};


export default KPICard;

