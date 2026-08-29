import React from "react";
import { Zap, Bell, Terminal, ShieldCheck } from "lucide-react";

export const Navbar: React.FC = () => {
  return (
    <header className="h-16 border-b border-surface-border bg-surface/50 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-gradient-to-tr from-brand-600 to-volt-cyan shadow-lg shadow-brand-500/20">
          <Zap className="w-5 h-5 text-white animate-pulse" />
        </div>
        <div>
          <span className="font-bold text-lg tracking-wider text-white">VOLT</span>
          <span className="text-xs ml-2 px-2 py-0.5 rounded-full bg-volt-emerald/10 text-volt-emerald border border-volt-emerald/20 font-mono">
            v1.0.0-PROD
          </span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-xs text-gray-400 bg-surface px-3 py-1.5 rounded-md border border-surface-border">
          <ShieldCheck className="w-4 h-4 text-volt-emerald" />
          <span>RBAC: ML Engineer</span>
        </div>
        <button className="p-2 rounded-md hover:bg-surface text-gray-400 hover:text-white transition">
          <Bell className="w-4 h-4" />
        </button>
        <button className="p-2 rounded-md hover:bg-surface text-gray-400 hover:text-white transition">
          <Terminal className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};
