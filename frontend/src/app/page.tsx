import React from "react";
import { MetricCard } from "@/components/MetricCard";
import { Database, Zap, Box, Activity, Layers, ArrowUpRight, Cpu } from "lucide-react";

export default function OverviewPage() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Platform Control Center</h1>
        <p className="text-sm text-gray-400 mt-1">
          Real-time metrics across ingestion pipelines, lakehouse storage, feature store, and live inference endpoints.
        </p>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <MetricCard
          title="Lakehouse Records"
          value="48.2M"
          change="+12.4% today"
          trend="up"
          icon={<Database className="w-5 h-5 text-volt-cyan" />}
        />
        <MetricCard
          title="Online Feature Store"
          value="18,450 req/s"
          change="sub-3.2ms latency"
          trend="up"
          icon={<Zap className="w-5 h-5 text-volt-amber" />}
        />
        <MetricCard
          title="Active Model Deployments"
          value="14 Models"
          change="3 Canary rollouts"
          trend="neutral"
          icon={<Box className="w-5 h-5 text-volt-purple" />}
        />
        <MetricCard
          title="Population Drift Status"
          value="Healthy"
          change="0 active alerts"
          trend="up"
          icon={<Activity className="w-5 h-5 text-volt-emerald" />}
        />
      </div>

      {/* Real-time Subsystem Status & DAG summary */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Pipeline Architecture */}
        <div className="lg:col-span-2 p-6 rounded-xl bg-surface border border-surface-border space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Layers className="w-5 h-5 text-brand-500" />
              <h2 className="text-base font-semibold text-white">Active Lakehouse Pipelines</h2>
            </div>
            <span className="text-xs px-2.5 py-1 rounded bg-brand-500/10 text-brand-400 border border-brand-500/20 font-mono">
              6 Active DAGs
            </span>
          </div>

          <div className="space-y-3 pt-2">
            {[
              { name: "customer_telemetry_stream", type: "Streaming (Kafka)", rows: "1.4M / hr", status: "RUNNING", color: "bg-emerald-500" },
              { name: "financial_transactions_etl", type: "Batch (DuckDB/Parquet)", rows: "12.8M rows", status: "COMPLETED", color: "bg-blue-500" },
              { name: "user_feature_store_sync", type: "Materializer (Redis)", rows: "840k keys", status: "RUNNING", color: "bg-amber-500" },
              { name: "churn_risk_daily_training", type: "Distributed XGBoost", rows: "2.1M rows", status: "SCHEDULED", color: "bg-purple-500" },
            ].map((p, i) => (
              <div key={i} className="flex items-center justify-between p-3.5 rounded-lg bg-background border border-surface-border">
                <div className="flex items-center gap-3">
                  <div className={`w-2 h-2 rounded-full ${p.color}`} />
                  <div>
                    <div className="text-sm font-medium text-white">{p.name}</div>
                    <div className="text-xs text-gray-400">{p.type}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-mono text-gray-200">{p.rows}</div>
                  <div className="text-xs text-gray-500">{p.status}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right 1 Col: Serving Gateway Telemetry */}
        <div className="p-6 rounded-xl bg-surface border border-surface-border space-y-4">
          <div className="flex items-center gap-2">
            <Cpu className="w-5 h-5 text-volt-cyan" />
            <h2 className="text-base font-semibold text-white">Inference Engine</h2>
          </div>

          <div className="space-y-4 pt-2">
            <div className="p-4 rounded-lg bg-background border border-surface-border">
              <div className="text-xs text-gray-400">P99 Inference Latency</div>
              <div className="text-xl font-bold text-white font-mono mt-1">4.18 ms</div>
              <div className="w-full bg-gray-800 h-1.5 rounded-full mt-3 overflow-hidden">
                <div className="bg-volt-cyan h-full rounded-full w-[24%]" />
              </div>
            </div>

            <div className="p-4 rounded-lg bg-background border border-surface-border">
              <div className="text-xs text-gray-400">ONNX Accelerated Graphs</div>
              <div className="text-xl font-bold text-white font-mono mt-1">98.4% CPU/GPU</div>
              <div className="w-full bg-gray-800 h-1.5 rounded-full mt-3 overflow-hidden">
                <div className="bg-volt-emerald h-full rounded-full w-[98%]" />
              </div>
            </div>

            <div className="p-4 rounded-lg bg-background border border-surface-border">
              <div className="text-xs text-gray-400">RAG Context Cache Hit Rate</div>
              <div className="text-xl font-bold text-white font-mono mt-1">91.6%</div>
              <div className="w-full bg-gray-800 h-1.5 rounded-full mt-3 overflow-hidden">
                <div className="bg-volt-purple h-full rounded-full w-[91%]" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
