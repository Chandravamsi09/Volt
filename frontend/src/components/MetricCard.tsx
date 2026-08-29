import React from "react";

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: string;
  trend?: "up" | "down" | "neutral";
  icon: React.ReactNode;
}

export const MetricCard: React.FC<MetricCardProps> = ({ title, value, change, trend, icon }) => {
  return (
    <div className="p-5 rounded-xl bg-surface border border-surface-border hover:border-gray-700 transition relative overflow-hidden group">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">{title}</span>
        <div className="p-2 rounded-lg bg-background border border-surface-border text-gray-300 group-hover:text-white transition">
          {icon}
        </div>
      </div>
      <div className="mt-4 flex items-baseline gap-2">
        <span className="text-2xl font-bold text-white tracking-tight">{value}</span>
        {change && (
          <span
            className={`text-xs font-medium ${
              trend === "up"
                ? "text-volt-emerald"
                : trend === "down"
                ? "text-rose-400"
                : "text-gray-400"
            }`}
          >
            {change}
          </span>
        )}
      </div>
    </div>
  );
};
