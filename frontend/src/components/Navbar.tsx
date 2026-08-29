"use client";

import React from "react";
import { Zap, Bell, Terminal, ShieldCheck, LogOut, User as UserIcon } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();

  const displayName = user?.full_name || user?.username || "ML Engineer";
  const displayRole = user?.role ? user.role.replace("_", " ").toUpperCase() : "ML ENGINEER";

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
        <div className="flex items-center gap-2 text-xs text-gray-300 bg-surface px-3 py-1.5 rounded-md border border-surface-border">
          <ShieldCheck className="w-4 h-4 text-volt-emerald" />
          <span className="font-medium text-white">{displayName}</span>
          <span className="text-gray-500 font-mono">|</span>
          <span className="text-gray-400">RBAC: {displayRole}</span>
        </div>

        <button 
          title="Notifications"
          className="p-2 rounded-md hover:bg-surface text-gray-400 hover:text-white transition"
        >
          <Bell className="w-4 h-4" />
        </button>

        <button 
          title="Terminal Console"
          className="p-2 rounded-md hover:bg-surface text-gray-400 hover:text-white transition"
        >
          <Terminal className="w-4 h-4" />
        </button>

        <button
          onClick={logout}
          title="Sign Out of Volt Platform"
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 text-red-400 hover:text-red-300 text-xs font-medium transition"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span>Logout</span>
        </button>
      </div>
    </header>
  );
};

