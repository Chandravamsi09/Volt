"use client";

import React, { useState } from "react";
import { Box, CheckCircle, Shield, ArrowUpRight, Cpu, Sliders } from "lucide-react";

export default function ModelsPage() {
  const [trafficSplit, setTrafficSplit] = useState(90);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Model Vault & Real-Time Serving</h1>
        <p className="text-sm text-gray-400 mt-1">
          Cryptographically verified model artifacts, automated ONNX acceleration, and Canary/AB deployment routing.
        </p>
      </div>

      {/* Model Registry List */}
      <div className="p-6 rounded-xl bg-surface border border-surface-border space-y-4">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-400">Registered Model Versions</h2>
        <div className="space-y-3">
          {[
            { name: "fraud_risk_detector", version: "v2.4.1", framework: "ONNX Runtime", stage: "PRODUCTION", f1: 0.942, latency: "2.1ms", hash: "9a8f2d...c301" },
            { name: "fraud_risk_detector", version: "v2.5.0-rc1", framework: "PyTorch MLP", stage: "CANARY (10%)", f1: 0.961, latency: "3.4ms", hash: "e41b7a...19ef" },
            { name: "customer_churn_xgboost", version: "v1.8.0", framework: "XGBoost", stage: "PRODUCTION", f1: 0.887, latency: "1.9ms", hash: "1d80ac...42b0" },
          ].map((m, i) => (
            <div key={i} className="p-4 rounded-lg bg-background border border-surface-border flex flex-wrap items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-white">{m.name}</span>
                  <span className="text-xs px-2 py-0.5 rounded bg-gray-800 font-mono text-volt-cyan">{m.version}</span>
                </div>
                <div className="text-xs text-gray-500 font-mono">
                  SHA-256: {m.hash} • Framework: {m.framework}
                </div>
              </div>

              <div className="flex items-center gap-6">
                <div className="text-right">
                  <div className="text-xs text-gray-400">F1-Score</div>
                  <div className="text-sm font-bold text-white font-mono">{m.f1}</div>
                </div>
                <div className="text-right">
                  <div className="text-xs text-gray-400">Avg Latency</div>
                  <div className="text-sm font-bold text-volt-emerald font-mono">{m.latency}</div>
                </div>
                <span
                  className={`text-xs px-2.5 py-1 rounded font-mono font-semibold ${
                    m.stage.includes("PRODUCTION")
                      ? "bg-volt-emerald/10 text-volt-emerald border border-volt-emerald/20"
                      : "bg-volt-amber/10 text-volt-amber border border-volt-amber/20"
                  }`}
                >
                  {m.stage}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Canary Traffic Routing Controller */}
      <div className="p-6 rounded-xl bg-surface border border-surface-border space-y-4">
        <div className="flex items-center gap-2">
          <Sliders className="w-5 h-5 text-volt-purple" />
          <h2 className="text-base font-semibold text-white">Canary & A/B Traffic Weight Controller</h2>
        </div>

        <div className="space-y-3 pt-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-300 font-medium">Production (v2.4.1): <span className="text-volt-cyan font-mono">{trafficSplit}%</span></span>
            <span className="text-gray-300 font-medium">Canary (v2.5.0-rc1): <span className="text-volt-purple font-mono">{100 - trafficSplit}%</span></span>
          </div>

          <input
            type="range"
            min="0"
            max="100"
            value={trafficSplit}
            onChange={(e) => setTrafficSplit(Number(e.target.value))}
            className="w-full h-2 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-brand-500"
          />
        </div>
      </div>
    </div>
  );
}
