"use client";

import React, { useState } from "react";
import { Database, Search, Zap, RefreshCw, Layers } from "lucide-react";

export default function FeatureStorePage() {
  const [entityId, setEntityId] = useState("usr_49201");
  const [lookupResult, setLookupResult] = useState<any>(null);

  const handleLookup = () => {
    setLookupResult({
      user_id: entityId,
      avg_30d_transaction_amount: 84.52,
      transactions_count_last_24h: 3,
      chargeback_risk_score: 0.042,
      preferred_payment_method: "apple_pay",
      is_premium_tier: 1,
      last_active_timestamp: "2026-08-30T02:30:11Z",
      retrieval_latency_ms: 1.84,
    });
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Enterprise Feature Store Catalog</h1>
        <p className="text-sm text-gray-400 mt-1">
          Point-in-time correct training feature extraction (Parquet/DuckDB) & sub-5ms low-latency Redis online serving.
        </p>
      </div>

      {/* Feature Views Catalog */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {[
          { name: "user_behavior_features_v1", entity: "user_id", features: 12, ttl: "30 Days", status: "ONLINE_READY", sync: "12m ago" },
          { name: "merchant_risk_features_v2", entity: "merchant_id", features: 8, ttl: "7 Days", status: "ONLINE_READY", sync: "4m ago" },
          { name: "session_clickstream_v1", entity: "session_id", features: 19, ttl: "24 Hours", status: "ONLINE_READY", sync: "1m ago" },
        ].map((fv, i) => (
          <div key={i} className="p-5 rounded-xl bg-surface border border-surface-border space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-volt-amber font-semibold">{fv.entity}</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-volt-emerald/10 text-volt-emerald border border-volt-emerald/20 font-mono">
                {fv.status}
              </span>
            </div>
            <div className="text-sm font-bold text-white">{fv.name}</div>
            <div className="flex items-center justify-between text-xs text-gray-400 pt-2 border-t border-surface-border">
              <span>{fv.features} Features</span>
              <span>TTL: {fv.ttl}</span>
              <span className="text-gray-500">{fv.sync}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Sub-5ms Real-Time Feature Inspector */}
      <div className="p-6 rounded-xl bg-surface border border-surface-border space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-volt-amber" />
            <h2 className="text-base font-semibold text-white">Sub-5ms Online Feature Inspector</h2>
          </div>
          <button
            onClick={handleLookup}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-volt-amber/20 hover:bg-volt-amber/30 text-volt-amber border border-volt-amber/30 text-xs font-semibold tracking-wide transition"
          >
            <Search className="w-3.5 h-3.5" /> Query Online Store
          </button>
        </div>

        <div className="flex items-center gap-4">
          <input
            type="text"
            value={entityId}
            onChange={(e) => setEntityId(e.target.value)}
            placeholder="Enter Entity ID (e.g. usr_49201)"
            className="flex-1 p-3 rounded-lg bg-background border border-surface-border font-mono text-sm text-white focus:outline-none focus:border-volt-amber"
          />
        </div>

        {lookupResult && (
          <div className="p-4 rounded-lg bg-background border border-surface-border mt-4">
            <div className="flex items-center justify-between mb-3 text-xs">
              <span className="font-mono text-gray-400">Response Payload</span>
              <span className="font-mono text-volt-emerald bg-volt-emerald/10 px-2 py-0.5 rounded border border-volt-emerald/20">
                Latency: {lookupResult.retrieval_latency_ms} ms (Redis MGET)
              </span>
            </div>
            <pre className="font-mono text-xs text-gray-300 overflow-x-auto">
              {JSON.stringify(lookupResult, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
