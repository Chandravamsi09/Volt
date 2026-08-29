"use client";

import React, { useState } from "react";
import { GitFork, Play, Terminal, Database, CheckCircle2, ArrowRight } from "lucide-react";

export default function PipelinesPage() {
  const [query, setQuery] = useState("SELECT * FROM read_parquet('data/lakehouse/events/*.parquet') LIMIT 5;");
  const [queryResult, setQueryResult] = useState<string | null>(null);

  const handleRunQuery = () => {
    setQueryResult(
      JSON.stringify(
        [
          { event_id: "evt_99182", user_id: "usr_401", action: "checkout_completed", amount: 149.5, event_timestamp: "2026-08-30T02:00:00Z" },
          { event_id: "evt_99183", user_id: "usr_812", action: "cart_item_added", amount: 29.99, event_timestamp: "2026-08-30T02:00:05Z" },
        ],
        null,
        2
      )
    );
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Lakehouse DAGs & SQL Query Studio</h1>
        <p className="text-sm text-gray-400 mt-1">
          Visual DAG orchestration engine powered by DuckDB, Polars, and Apache Arrow.
        </p>
      </div>

      {/* Visual DAG Architecture */}
      <div className="p-6 rounded-xl bg-surface border border-surface-border space-y-6">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-400">Live DAG Execution Canvas</h2>
        <div className="flex flex-wrap items-center gap-4 justify-between bg-background p-6 rounded-lg border border-surface-border">
          {/* Node 1 */}
          <div className="p-4 rounded-lg bg-surface border border-volt-cyan/30 text-center min-w-[160px]">
            <div className="text-xs text-volt-cyan font-mono font-semibold">SOURCE: KAFKA</div>
            <div className="text-sm font-bold text-white mt-1">Raw Events Stream</div>
            <div className="text-xs text-emerald-400 flex items-center justify-center gap-1 mt-2">
              <CheckCircle2 className="w-3.5 h-3.5" /> 14.2k/sec
            </div>
          </div>

          <ArrowRight className="text-gray-600 hidden md:block" />

          {/* Node 2 */}
          <div className="p-4 rounded-lg bg-surface border border-brand-500/30 text-center min-w-[160px]">
            <div className="text-xs text-brand-400 font-mono font-semibold">VALIDATOR</div>
            <div className="text-sm font-bold text-white mt-1">Great Expectations</div>
            <div className="text-xs text-emerald-400 flex items-center justify-center gap-1 mt-2">
              <CheckCircle2 className="w-3.5 h-3.5" /> 100% Valid
            </div>
          </div>

          <ArrowRight className="text-gray-600 hidden md:block" />

          {/* Node 3 */}
          <div className="p-4 rounded-lg bg-surface border border-volt-amber/30 text-center min-w-[160px]">
            <div className="text-xs text-volt-amber font-mono font-semibold">TRANSFORMATION</div>
            <div className="text-sm font-bold text-white mt-1">Polars & DuckDB</div>
            <div className="text-xs text-emerald-400 flex items-center justify-center gap-1 mt-2">
              <CheckCircle2 className="w-3.5 h-3.5" /> 0.8s batch
            </div>
          </div>

          <ArrowRight className="text-gray-600 hidden md:block" />

          {/* Node 4 */}
          <div className="p-4 rounded-lg bg-surface border border-volt-purple/30 text-center min-w-[160px]">
            <div className="text-xs text-volt-purple font-mono font-semibold">SINK: LAKEHOUSE</div>
            <div className="text-sm font-bold text-white mt-1">Parquet Partition</div>
            <div className="text-xs text-emerald-400 flex items-center justify-center gap-1 mt-2">
              <CheckCircle2 className="w-3.5 h-3.5" /> Synced
            </div>
          </div>
        </div>
      </div>

      {/* Interactive SQL Console */}
      <div className="p-6 rounded-xl bg-surface border border-surface-border space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Terminal className="w-5 h-5 text-volt-cyan" />
            <h2 className="text-base font-semibold text-white">DuckDB In-Memory OLAP Console</h2>
          </div>
          <button
            onClick={handleRunQuery}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold tracking-wide transition"
          >
            <Play className="w-3.5 h-3.5 fill-current" /> Execute SQL
          </button>
        </div>

        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          rows={3}
          className="w-full p-4 rounded-lg bg-background border border-surface-border font-mono text-sm text-volt-cyan focus:outline-none focus:border-brand-500"
        />

        {queryResult && (
          <div className="mt-4">
            <div className="text-xs font-mono text-gray-400 mb-2">Query Results (JSON View):</div>
            <pre className="p-4 rounded-lg bg-background border border-surface-border font-mono text-xs text-gray-300 overflow-x-auto">
              {queryResult}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
