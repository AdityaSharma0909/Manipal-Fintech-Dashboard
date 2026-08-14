import React from "react";

interface KpiCardProps {
  icon: string;
  label: string;
  value: string | number;
  color?: "blue" | "violet" | "emerald" | "amber" | "rose";
  badge?: string;
  badgeType?: "up" | "down" | "neutral";
}

export const KpiCard: React.FC<KpiCardProps> = ({
  icon,
  label,
  value,
  color = "blue",
  badge,
  badgeType = "neutral",
}) => (
  <div className={`kpi-card ${color}`}>
    <div className="kpi-header">
      <div className={`kpi-icon ${color}`}>{icon}</div>
      {badge && <span className={`kpi-badge ${badgeType}`}>{badge}</span>}
    </div>
    <div className={`kpi-value ${color}`}>{value}</div>
    <div className="kpi-label">{label}</div>
  </div>
);

interface SectionProps {
  icon: string;
  iconColor?: "blue" | "violet" | "emerald" | "amber";
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}

export const Section: React.FC<SectionProps> = ({
  icon,
  iconColor = "blue",
  title,
  subtitle,
  children,
}) => (
  <section>
    <div className="section-header">
      <div className={`section-icon ${iconColor}`}>{icon}</div>
      <div>
        <div className="section-title">{title}</div>
        {subtitle && <div className="section-subtitle">{subtitle}</div>}
      </div>
    </div>
    {children}
  </section>
);

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{ value: number; name: string }>;
  label?: string;
  formatter?: (value: number) => string;
}

export const ChartTooltip: React.FC<CustomTooltipProps> = ({
  active,
  payload,
  label,
  formatter,
}) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="custom-tooltip">
      {label && <div className="tooltip-label">{label}</div>}
      {payload.map((p, i) => (
        <div key={i} className="tooltip-value">
          {formatter ? formatter(p.value) : p.value.toLocaleString("en-IN")}
        </div>
      ))}
    </div>
  );
};

export const LoadingState: React.FC = () => (
  <div className="loading-overlay">
    <div className="spinner" />
    <span>Loading analytics…</span>
  </div>
);

export const ErrorState: React.FC<{ message: string }> = ({ message }) => (
  <div className="error-card">
    <span>⚠️</span>
    <span>
      {message}{" "}
      <strong>
        Make sure the Django server is running and DASHBOARD_API_KEY is set.
      </strong>
    </span>
  </div>
);

/** Format large INR numbers as ₹1.23 Cr / ₹45.6 L / ₹12,345 */
export const formatInr = (val: number): string => {
  if (val >= 1_00_00_000) return `₹${(val / 1_00_00_000).toFixed(2)} Cr`;
  if (val >= 1_00_000) return `₹${(val / 1_00_000).toFixed(1)} L`;
  return `₹${val.toLocaleString("en-IN")}`;
};

export const formatPct = (val: number) => `${val.toFixed(1)}%`;
