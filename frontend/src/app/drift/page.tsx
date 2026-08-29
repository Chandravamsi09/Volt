"use client";

import React from "react";
import { Activity, AlertTriangle, CheckCircle2, RefreshCw } from "lucide-react";

export default function DriftPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Model & Data Drift Observability</h1>
        <p className="text-sm text-gray-400 mt-1">
          Automated Kolmogorov-Smirnov statistical tests, Population Stability Index (PSI), and auto-retraining triggers.
        </p>
      </div>

      {/* Feature Drift Evaluation Table */}
      <div className="p-6 rounded-xl bg-surface border border-surface-border space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-volt-emerald" />
            <h2 className="text-base font-semibold text-white">Feature Drift Matrix (Production vs Baseline)</h2>
          </div>
          <button className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-background border border-surface-border text-xs text-gray-300 hover:text-white transition">
            <RefreshCw className="w-3 h-3" /> Recompute Metrics
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-xs text-gray-400 uppercase bg-background border-b border-surface-border">
              <tr>
                <th className="px-4 py-3">Feature Name</th>
                <th className="px-4 py-3">Metric Type</th>
                <th className="px-4 py-3">PSI Value</th>
                <th className="px-4 py-3">KS p-Value</th>
                <th className="px-4 py-3">Threshold</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-border">
              {[
                { name: "transaction_amount_30d", metric: "PSI / KS", psi: "0.041", ks: "0.482", thresh: "< 0.25", status: "STABLE" },
                { name: "device_trust_score", metric: "PSI / KS", psi: "0.082", ks: "0.315", thresh: "< 0.25", status: "STABLE" },
                { name: "ip_velocity_6h", metric: "PSI / KS", psi: "0.284", ks: "0.009", thresh: "< 0.25", status: "DRIFT DETECTED" },
                { name: "account_age_days", metric: "PSI / KS", psi: "0.019", ks: "0.891", thresh: "< 0.25", status: "STABLE" },
              ].map((row, i) => (
                <tr key={i} className="hover:bg-background/50">
                  <td className="px-4 py-3 font-mono font-medium text-white">{row.name}</td>
                  <td className="px-4 py-3 text-xs text-gray-400">{row.metric}</td>
                  <td className="px-4 py-3 font-mono text-xs">{row.psi}</td>
                  <td className="px-4 py-3 font-mono text-xs">{row.ks}</td>
                  <td className="px-4 py-3 text-xs text-gray-500 font-mono">{row.thresh}</td>
                  <td className="px-4 py-3">
                    {row.status === "STABLE" ? (
                      <span className="flex items-center gap-1.5 text-xs text-volt-emerald font-semibold">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Stable
                      </span>
                    ) : (
                      <span className="flex items-center gap-1.5 text-xs text-rose-400 font-semibold">
                        <AlertTriangle className="w-3.5 h-3.5" /> Drift Alert
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
