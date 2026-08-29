import React from "react";
import Link from "next/link";
import { LayoutDashboard, GitFork, Database, Box, Activity, Bot } from "lucide-react";

interface NavItemProps {
  href: string;
  icon: React.ReactNode;
  label: string;
}

const NavItem: React.FC<NavItemProps> = ({ href, icon, label }) => {
  return (
    <Link
      href={href}
      className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-gray-300 hover:text-white hover:bg-surface border border-transparent hover:border-surface-border transition"
    >
      {icon}
      <span>{label}</span>
    </Link>
  );
};

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 border-r border-surface-border bg-background p-4 flex flex-col justify-between shrink-0 min-h-[calc(100vh-4rem)]">
      <div className="space-y-6">
        <div>
          <div className="px-3 text-xs font-semibold uppercase tracking-wider text-gray-500 mb-2">
            Platform Engine
          </div>
          <nav className="space-y-1">
            <NavItem href="/" icon={<LayoutDashboard className="w-4 h-4 text-brand-500" />} label="Overview" />
            <NavItem href="/pipelines" icon={<GitFork className="w-4 h-4 text-volt-cyan" />} label="Pipelines & Lakehouse" />
            <NavItem href="/feature-store" icon={<Database className="w-4 h-4 text-volt-amber" />} label="Feature Store" />
            <NavItem href="/models" icon={<Box className="w-4 h-4 text-volt-purple" />} label="Model Vault & Serving" />
            <NavItem href="/drift" icon={<Activity className="w-4 h-4 text-volt-emerald" />} label="Drift & Observability" />
          </nav>
        </div>

        <div>
          <div className="px-3 text-xs font-semibold uppercase tracking-wider text-gray-500 mb-2">
            Intelligence
          </div>
          <nav className="space-y-1">
            <NavItem href="/llm" icon={<Bot className="w-4 h-4 text-pink-400" />} label="LLM & Multi-Agent RAG" />
          </nav>
        </div>
      </div>

      <div className="p-3 rounded-lg bg-surface border border-surface-border">
        <div className="text-xs text-gray-400">Cluster Status</div>
        <div className="flex items-center gap-2 mt-1">
          <div className="w-2 h-2 rounded-full bg-volt-emerald animate-ping" />
          <span className="text-xs font-medium text-white">4 Worker Nodes Active</span>
        </div>
      </div>
    </aside>
  );
};
