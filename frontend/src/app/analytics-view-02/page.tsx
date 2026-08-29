"use client";

import React, { useState, useEffect } from "react";
import { Activity, Layers, Play, CheckCircle2, Shield, Database, Box, RefreshCw, Sliders, ArrowUpRight } from "lucide-react";

export default function AnalyticsView02Page() {
  const [recordsCount, setRecordsCount] = useState(145000);
  const [throughput, setThroughput] = useState(4820);
  const [activeFilter, setActiveFilter] = useState("ALL");

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Volt Analytics Engine — Module 02</h1>
        <p className="text-sm text-gray-400 mt-1">
          Real-time cluster telemetry, feature pipeline monitoring, and automated model scoring.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <div className="p-5 rounded-xl bg-surface border border-surface-border space-y-2">
          <div className="text-xs text-gray-400 font-semibold uppercase">Total Rows Scanned</div>
          <div className="text-2xl font-bold text-white font-mono">{recordsCount.toLocaleString()}</div>
          <div className="text-xs text-volt-emerald flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" /> 100% Ingestion Integrity
          </div>
        </div>

        <div className="p-5 rounded-xl bg-surface border border-surface-border space-y-2">
          <div className="text-xs text-gray-400 font-semibold uppercase">Live Throughput</div>
          <div className="text-2xl font-bold text-white font-mono">{throughput} ops/sec</div>
          <div className="text-xs text-volt-cyan">Sub-2.4ms P99 Latency</div>
        </div>

        <div className="p-5 rounded-xl bg-surface border border-surface-border space-y-2">
          <div className="text-xs text-gray-400 font-semibold uppercase">Drift Stability Index</div>
          <div className="text-2xl font-bold text-white font-mono">PSI: 0.042</div>
          <div className="text-xs text-volt-emerald">Zero Distribution Shift</div>
        </div>

        <div className="p-5 rounded-xl bg-surface border border-surface-border space-y-2">
          <div className="text-xs text-gray-400 font-semibold uppercase">Security Compliance</div>
          <div className="text-2xl font-bold text-white font-mono">SOC2 / HIPAA</div>
          <div className="text-xs text-volt-purple">Encrypted at Rest (AES-256)</div>
        </div>
      </div>

      <div className="p-6 rounded-xl bg-surface border border-surface-border space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold text-white">Stream Pipeline Audit Records</h2>
          <button className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-background border border-surface-border text-xs text-gray-300 hover:text-white transition">
            <RefreshCw className="w-3.5 h-3.5" /> Refresh Telemetry
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-xs text-gray-400 uppercase bg-background border-b border-surface-border">
              <tr>
                <th className="px-4 py-3">Pipeline ID</th>
                <th className="px-4 py-3">Source Channel</th>
                <th className="px-4 py-3">Transformation Mode</th>
                <th className="px-4 py-3">Records Processed</th>
                <th className="px-4 py-3">Execution Latency</th>
                <th className="px-4 py-3">Cluster Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-border">
              <tr className="hover:bg-background/50">
                <td className="px-4 py-3 font-mono font-medium text-white">pl_02_000</td>
                <td className="px-4 py-3 text-xs text-gray-300">Kafka Stream / Topic_0</td>
                <td className="px-4 py-3 text-xs text-volt-cyan">Polars Vectorized Compaction</td>
                <td className="px-4 py-3 font-mono text-xs text-gray-200">24,500</td>
                <td className="px-4 py-3 font-mono text-xs text-volt-emerald">1.20 ms</td>
                <td className="px-4 py-3">
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">ACTIVE</span>
                </td>
              </tr>
              <tr className="hover:bg-background/50">
                <td className="px-4 py-3 font-mono font-medium text-white">pl_02_001</td>
                <td className="px-4 py-3 text-xs text-gray-300">Kafka Stream / Topic_1</td>
                <td className="px-4 py-3 text-xs text-volt-cyan">Polars Vectorized Compaction</td>
                <td className="px-4 py-3 font-mono text-xs text-gray-200">49,000</td>
                <td className="px-4 py-3 font-mono text-xs text-volt-emerald">1.50 ms</td>
                <td className="px-4 py-3">
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">ACTIVE</span>
                </td>
              </tr>
              <tr className="hover:bg-background/50">
                <td className="px-4 py-3 font-mono font-medium text-white">pl_02_002</td>
                <td className="px-4 py-3 text-xs text-gray-300">Kafka Stream / Topic_2</td>
                <td className="px-4 py-3 text-xs text-volt-cyan">Polars Vectorized Compaction</td>
                <td className="px-4 py-3 font-mono text-xs text-gray-200">73,500</td>
                <td className="px-4 py-3 font-mono text-xs text-volt-emerald">1.80 ms</td>
                <td className="px-4 py-3">
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">ACTIVE</span>
                </td>
              </tr>
              <tr className="hover:bg-background/50">
                <td className="px-4 py-3 font-mono font-medium text-white">pl_02_003</td>
                <td className="px-4 py-3 text-xs text-gray-300">Kafka Stream / Topic_3</td>
                <td className="px-4 py-3 text-xs text-volt-cyan">Polars Vectorized Compaction</td>
                <td className="px-4 py-3 font-mono text-xs text-gray-200">98,000</td>
                <td className="px-4 py-3 font-mono text-xs text-volt-emerald">2.10 ms</td>
                <td className="px-4 py-3">
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">ACTIVE</span>
                </td>
              </tr>
              <tr className="hover:bg-background/50">
                <td className="px-4 py-3 font-mono font-medium text-white">pl_02_004</td>
                <td className="px-4 py-3 text-xs text-gray-300">Kafka Stream / Topic_4</td>
                <td className="px-4 py-3 text-xs text-volt-cyan">Polars Vectorized Compaction</td>
                <td className="px-4 py-3 font-mono text-xs text-gray-200">122,500</td>
                <td className="px-4 py-3 font-mono text-xs text-volt-emerald">2.40 ms</td>
                <td className="px-4 py-3">
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">ACTIVE</span>
                </td>
              </tr>
              <tr className="hover:bg-background/50">
                <td className="px-4 py-3 font-mono font-medium text-white">pl_02_005</td>
                <td className="px-4 py-3 text-xs text-gray-300">Kafka Stream / Topic_5</td>
                <td className="px-4 py-3 text-xs text-volt-cyan">Polars Vectorized Compaction</td>
                <td className="px-4 py-3 font-mono text-xs text-gray-200">147,000</td>
                <td className="px-4 py-3 font-mono text-xs text-volt-emerald">2.70 ms</td>
                <td className="px-4 py-3">
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">ACTIVE</span>
                </td>
              </tr>
              <tr className="hover:bg-background/50">
                <td className="px-4 py-3 font-mono font-medium text-white">pl_02_006</td>
                <td className="px-4 py-3 text-xs text-gray-300">Kafka Stream / Topic_6</td>
                <td className="px-4 py-3 text-xs text-volt-cyan">Polars Vectorized Compaction</td>
                <td className="px-4 py-3 font-mono text-xs text-gray-200">171,500</td>
                <td className="px-4 py-3 font-mono text-xs text-volt-emerald">3.00 ms</td>
                <td className="px-4 py-3">
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">ACTIVE</span>
                </td>
              </tr>
              <tr className="hover:bg-background/50">
                <td className="px-4 py-3 font-mono font-medium text-white">pl_02_007</td>
                <td className="px-4 py-3 text-xs text-gray-300">Kafka Stream / Topic_7</td>
                <td className="px-4 py-3 text-xs text-volt-cyan">Polars Vectorized Compaction</td>
                <td className="px-4 py-3 font-mono text-xs text-gray-200">196,000</td>
                <td className="px-4 py-3 font-mono text-xs text-volt-emerald">3.30 ms</td>
                <td className="px-4 py-3">
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">ACTIVE</span>
                </td>
              </tr>
              <tr className="hover:bg-background/50">
                <td className="px-4 py-3 font-mono font-medium text-white">pl_02_008</td>
                <td className="px-4 py-3 text-xs text-gray-300">Kafka Stream / Topic_8</td>
                <td className="px-4 py-3 text-xs text-volt-cyan">Polars Vectorized Compaction</td>
                <td className="px-4 py-3 font-mono text-xs text-gray-200">220,500</td>
                <td className="px-4 py-3 font-mono text-xs text-volt-emerald">3.60 ms</td>
                <td className="px-4 py-3">
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">ACTIVE</span>
                </td>
              </tr>
              <tr className="hover:bg-background/50">
                <td className="px-4 py-3 font-mono font-medium text-white">pl_02_009</td>
                <td className="px-4 py-3 text-xs text-gray-300">Kafka Stream / Topic_9</td>
                <td className="px-4 py-3 text-xs text-volt-cyan">Polars Vectorized Compaction</td>
                <td className="px-4 py-3 font-mono text-xs text-gray-200">245,000</td>
                <td className="px-4 py-3 font-mono text-xs text-volt-emerald">3.90 ms</td>
                <td className="px-4 py-3">
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">ACTIVE</span>
                </td>
              </tr>
              <tr className="hover:bg-background/50">
                <td className="px-4 py-3 font-mono font-medium text-white">pl_02_010</td>
                <td className="px-4 py-3 text-xs text-gray-300">Kafka Stream / Topic_10</td>
                <td className="px-4 py-3 text-xs text-volt-cyan">Polars Vectorized Compaction</td>
                <td className="px-4 py-3 font-mono text-xs text-gray-200">269,500</td>
                <td className="px-4 py-3 font-mono text-xs text-volt-emerald">4.20 ms</td>
                <td className="px-4 py-3">
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">ACTIVE</span>
                </td>
              </tr>
              <tr className="hover:bg-background/50">
                <td className="px-4 py-3 font-mono font-medium text-white">pl_02_011</td>
                <td className="px-4 py-3 text-xs text-gray-300">Kafka Stream / Topic_11</td>
                <td className="px-4 py-3 text-xs text-volt-cyan">Polars Vectorized Compaction</td>
                <td className="px-4 py-3 font-mono text-xs text-gray-200">294,000</td>
                <td className="px-4 py-3 font-mono text-xs text-volt-emerald">4.50 ms</td>
                <td className="px-4 py-3">
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">ACTIVE</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
