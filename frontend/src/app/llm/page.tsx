"use client";

import React, { useState } from "react";
import { Bot, Sparkles, Send, ShieldCheck, Database, Layers } from "lucide-react";

export default function LLMRAGPage() {
  const [prompt, setPrompt] = useState("What are the best hyperparameters for fraud detection?");
  const [response, setResponse] = useState<any>(null);

  const handleAsk = () => {
    setResponse({
      answer: "Based on historical experiment runs in Volt Model Vault, the optimal configuration for fraud classification is GradientBoosting with n_estimators=140, max_depth=6, and learning_rate=0.08, achieving an F1 score of 0.942.",
      sources: [
        { title: "Model Run Registry v2.4.1", chunk: "XGBoost & GradientBoosting trials report max ROC-AUC 0.968 at max_depth 6." },
        { title: "Feature Store Schema v1.0", chunk: "transaction_amount_30d and ip_velocity_6h show highest feature importance." }
      ],
      passed_guardrails: true,
      latency_ms: 12.4
    });
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Multi-Agent RAG & Semantic Intelligence</h1>
        <p className="text-sm text-gray-400 mt-1">
          Qdrant vector embeddings, hybrid RAG context synthesis, and collaborative agentic planning.
        </p>
      </div>

      {/* RAG Query Terminal */}
      <div className="p-6 rounded-xl bg-surface border border-surface-border space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot className="w-5 h-5 text-pink-400" />
            <h2 className="text-base font-semibold text-white">Ask Volt Knowledge Base (RAG)</h2>
          </div>
          <span className="flex items-center gap-1.5 text-xs text-volt-emerald font-semibold bg-volt-emerald/10 px-2.5 py-1 rounded border border-volt-emerald/20">
            <ShieldCheck className="w-3.5 h-3.5" /> Safety Guardrails Active
          </span>
        </div>

        <div className="flex gap-3">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Ask anything about models, pipelines, or lakehouse data..."
            className="flex-1 p-3.5 rounded-lg bg-background border border-surface-border font-sans text-sm text-white focus:outline-none focus:border-pink-500"
          />
          <button
            onClick={handleAsk}
            className="flex items-center gap-2 px-5 py-3.5 rounded-lg bg-pink-600 hover:bg-pink-500 text-white text-xs font-semibold tracking-wide transition"
          >
            <Send className="w-4 h-4" /> Synthesize
          </button>
        </div>

        {response && (
          <div className="space-y-4 pt-4 border-t border-surface-border mt-4">
            <div className="p-4 rounded-lg bg-background border border-surface-border space-y-2">
              <div className="text-xs text-pink-400 font-mono font-semibold flex items-center gap-1">
                <Sparkles className="w-3.5 h-3.5" /> SYNTHESIZED RESPONSE (Latency: {response.latency_ms}ms)
              </div>
              <p className="text-sm text-gray-200 leading-relaxed">{response.answer}</p>
            </div>

            <div className="space-y-2">
              <div className="text-xs font-mono text-gray-400 uppercase tracking-wider">Retrieved Context Sources:</div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {response.sources.map((s: any, idx: number) => (
                  <div key={idx} className="p-3 rounded-lg bg-background border border-surface-border text-xs space-y-1">
                    <div className="font-semibold text-volt-cyan">{s.title}</div>
                    <div className="text-gray-400">{s.chunk}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
