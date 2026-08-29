"use client";

import React, { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { Navbar } from "@/components/Navbar";
import { Sidebar } from "@/components/Sidebar";
import { useAuth } from "@/context/AuthContext";
import { Zap, Loader2 } from "lucide-react";

export const AppShell: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const pathname = usePathname();
  const router = useRouter();
  const { user, token, isLoading } = useAuth();

  const isLoginPage = pathname === "/login";

  useEffect(() => {
    if (!isLoading) {
      if (!isLoginPage && (!user || !token)) {
        router.replace("/login");
      }
    }
  }, [user, token, isLoading, isLoginPage, router]);

  // If on login route, render standalone login view
  if (isLoginPage) {
    return <>{children}</>;
  }

  // Loading state while restoring auth session from localStorage
  if (isLoading) {
    return (
      <div className="min-h-screen w-full flex flex-col items-center justify-center bg-background text-gray-400 space-y-4">
        <div className="p-3 rounded-2xl bg-gradient-to-tr from-brand-600 to-volt-cyan shadow-xl shadow-brand-500/20 animate-pulse">
          <Zap className="w-8 h-8 text-white" />
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-300 font-mono">
          <Loader2 className="w-4 h-4 animate-spin text-volt-cyan" />
          <span>Verifying Volt Secure Session...</span>
        </div>
      </div>
    );
  }

  // If not authenticated and not loading, render loading placeholder while redirect triggers
  if (!user || !token) {
    return (
      <div className="min-h-screen w-full flex flex-col items-center justify-center bg-background text-gray-400">
        <Loader2 className="w-6 h-6 animate-spin text-volt-cyan" />
      </div>
    );
  }

  // Authenticated: Render complete Volt platform workspace
  return (
    <div className="flex flex-col min-h-screen bg-background text-gray-100">
      <Navbar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-8 overflow-y-auto max-w-7xl mx-auto w-full">
          {children}
        </main>
      </div>
    </div>
  );
};
