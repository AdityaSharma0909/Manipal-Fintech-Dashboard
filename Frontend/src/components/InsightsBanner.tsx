import React, { useState } from 'react';
import { X, ChevronRight } from 'lucide-react';

interface Insight {
  id: number;
  text: string;
  type: 'success' | 'info' | 'warning';
  icon: string;
}

interface InsightsBannerProps {
  insights: Insight[];
  darkMode: boolean;
}

const typeStyles = {
  success: {
    light: 'bg-emerald-50 border-emerald-200 text-emerald-800',
    dark: 'bg-emerald-900/20 border-emerald-500/30 text-emerald-300',
    dot: 'bg-emerald-500',
  },
  info: {
    light: 'bg-indigo-50 border-indigo-200 text-indigo-800',
    dark: 'bg-indigo-900/20 border-indigo-500/30 text-indigo-300',
    dot: 'bg-indigo-500',
  },
  warning: {
    light: 'bg-amber-50 border-amber-200 text-amber-800',
    dark: 'bg-amber-900/20 border-amber-500/30 text-amber-300',
    dot: 'bg-amber-500',
  },
};

const InsightsBanner: React.FC<InsightsBannerProps> = ({ insights: initialInsights, darkMode }) => {
  const [dismissed, setDismissed] = useState<Set<number>>(new Set());
  const visible = initialInsights.filter(i => !dismissed.has(i.id));

  if (visible.length === 0) return null;

  return (
    <div className="flex gap-3 overflow-x-auto pb-1 scrollbar-hide">
      {visible.map((insight) => {
        const styles = typeStyles[insight.type];
        return (
          <div
            key={insight.id}
            className={`flex-shrink-0 flex items-start gap-2.5 px-4 py-3 rounded-xl border text-xs font-medium transition-all max-w-xs group ${
              darkMode ? styles.dark : styles.light
            }`}
          >
            <span className="text-base leading-none mt-0.5">{insight.icon}</span>
            <p className="flex-1 leading-relaxed text-xs">{insight.text}</p>
            <div className="flex items-center gap-1 flex-shrink-0">
              <button className="opacity-60 hover:opacity-100 transition-opacity">
                <ChevronRight size={12} />
              </button>
              <button
                onClick={() => setDismissed(prev => new Set([...prev, insight.id]))}
                className="opacity-60 hover:opacity-100 transition-opacity"
              >
                <X size={12} />
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default InsightsBanner;
