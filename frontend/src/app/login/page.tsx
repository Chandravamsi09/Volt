"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Zap, Lock, Mail, User as UserIcon, ArrowRight, ShieldCheck, AlertCircle, CheckCircle2, Loader2 } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

export default function LoginPage() {
  const { user, token, isLoading: authLoading, login, register } = useAuth();
  const router = useRouter();

  const [mode, setMode] = useState<"login" | "register">("login");
  const [submitting, setSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Login form state
  const [loginIdentifier, setLoginIdentifier] = useState("");
  const [loginPassword, setLoginPassword] = useState("");

  // Register form state
  const [regName, setRegName] = useState("");
  const [regEmail, setRegEmail] = useState("");
  const [regPassword, setRegPassword] = useState("");
  const [regConfirmPassword, setRegConfirmPassword] = useState("");

  useEffect(() => {
    // If already authenticated, redirect to overview dashboard
    if (!authLoading && user && token) {
      router.replace("/");
    }
  }, [user, token, authLoading, router]);

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setSuccessMessage(null);

    if (!loginIdentifier.trim() || !loginPassword) {
      setErrorMessage("Please enter your email/username and password.");
      return;
    }

    setSubmitting(true);
    const result = await login(loginIdentifier, loginPassword);
    setSubmitting(false);

    if (result.success) {
      router.push("/");
    } else {
      setErrorMessage(result.error || "Invalid username or password. Please try again.");
    }
  };

  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setSuccessMessage(null);

    if (!regName.trim() || !regEmail.trim() || !regPassword || !regConfirmPassword) {
      setErrorMessage("All registration fields are required.");
      return;
    }

    if (regPassword.length < 8) {
      setErrorMessage("Password must be at least 8 characters long.");
      return;
    }

    if (regPassword !== regConfirmPassword) {
      setErrorMessage("Passwords do not match. Please verify and try again.");
      return;
    }

    setSubmitting(true);
    const result = await register(regName, regEmail, regPassword);
    setSubmitting(false);

    if (result.success) {
      setSuccessMessage("Account created successfully! You can now sign in.");
      setMode("login");
      setLoginIdentifier(regEmail);
      setLoginPassword("");
      setRegPassword("");
      setRegConfirmPassword("");
    } else {
      setErrorMessage(result.error || "Registration failed. Email may already be in use.");
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-background px-4 py-12 relative overflow-hidden">
      {/* Background Cyber Glow Accent */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-brand-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-volt-cyan/10 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md relative z-10">
        {/* Volt Brand Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center p-3 rounded-2xl bg-gradient-to-tr from-brand-600 to-volt-cyan shadow-xl shadow-brand-500/20 mb-4">
            <Zap className="w-8 h-8 text-white animate-pulse" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-white flex items-center justify-center gap-2">
            VOLT <span className="text-xs px-2 py-0.5 rounded-full bg-volt-emerald/10 text-volt-emerald border border-volt-emerald/20 font-mono">v1.0.0</span>
          </h1>
          <p className="text-sm text-gray-400 mt-2">
            Enterprise AI/ML & Data Lakehouse Platform
          </p>
        </div>

        {/* Auth Card */}
        <div className="bg-surface border border-surface-border rounded-2xl p-7 shadow-2xl backdrop-blur-xl">
          {/* Mode Switcher Tabs */}
          <div className="flex border-b border-surface-border pb-4 mb-6">
            <button
              type="button"
              onClick={() => {
                setMode("login");
                setErrorMessage(null);
              }}
              className={`flex-1 text-center py-2 text-sm font-semibold transition border-b-2 -mb-4.5 ${
                mode === "login"
                  ? "border-volt-cyan text-white"
                  : "border-transparent text-gray-400 hover:text-gray-200"
              }`}
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={() => {
                setMode("register");
                setErrorMessage(null);
              }}
              className={`flex-1 text-center py-2 text-sm font-semibold transition border-b-2 -mb-4.5 ${
                mode === "register"
                  ? "border-volt-cyan text-white"
                  : "border-transparent text-gray-400 hover:text-gray-200"
              }`}
            >
              Create Account
            </button>
          </div>

          {/* Feedback Banners */}
          {errorMessage && (
            <div className="mb-5 p-3.5 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-xs flex items-start gap-2.5">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{errorMessage}</span>
            </div>
          )}

          {successMessage && (
            <div className="mb-5 p-3.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-start gap-2.5">
              <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{successMessage}</span>
            </div>
          )}

          {/* LOGIN FORM */}
          {mode === "login" ? (
            <form onSubmit={handleLoginSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-1.5">
                  Email or Username
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-500">
                    <Mail className="w-4 h-4" />
                  </div>
                  <input
                    type="text"
                    required
                    value={loginIdentifier}
                    onChange={(e) => setLoginIdentifier(e.target.value)}
                    placeholder="admin@volt.ai or username"
                    className="w-full pl-10 pr-4 py-2.5 bg-background border border-surface-border rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:border-volt-cyan focus:ring-1 focus:ring-volt-cyan transition"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-1.5">
                  Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-500">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    type="password"
                    required
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-10 pr-4 py-2.5 bg-background border border-surface-border rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:border-volt-cyan focus:ring-1 focus:ring-volt-cyan transition"
                  />
                </div>
              </div>

              <div className="flex items-center justify-between text-xs text-gray-400 pt-1">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    defaultChecked
                    className="rounded bg-background border-surface-border text-brand-600 focus:ring-0"
                  />
                  <span>Stay authenticated</span>
                </label>
                <span className="text-gray-500 text-[11px]">Default: admin@volt.ai</span>
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full py-2.5 px-4 rounded-lg bg-gradient-to-r from-brand-600 to-volt-cyan hover:opacity-95 text-white text-sm font-semibold shadow-lg shadow-brand-500/20 flex items-center justify-center gap-2 transition disabled:opacity-50 mt-2"
              >
                {submitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Authenticating...</span>
                  </>
                ) : (
                  <>
                    <span>Sign In to Platform</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>
          ) : (
            /* REGISTER FORM */
            <form onSubmit={handleRegisterSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-1.5">
                  Full Name
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-500">
                    <UserIcon className="w-4 h-4" />
                  </div>
                  <input
                    type="text"
                    required
                    value={regName}
                    onChange={(e) => setRegName(e.target.value)}
                    placeholder="Dr. Jane Doe"
                    className="w-full pl-10 pr-4 py-2.5 bg-background border border-surface-border rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:border-volt-cyan focus:ring-1 focus:ring-volt-cyan transition"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-1.5">
                  Work Email
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-500">
                    <Mail className="w-4 h-4" />
                  </div>
                  <input
                    type="email"
                    required
                    value={regEmail}
                    onChange={(e) => setRegEmail(e.target.value)}
                    placeholder="jane@company.com"
                    className="w-full pl-10 pr-4 py-2.5 bg-background border border-surface-border rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:border-volt-cyan focus:ring-1 focus:ring-volt-cyan transition"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-1.5">
                  Password (min 8 chars)
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-500">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    type="password"
                    required
                    minLength={8}
                    value={regPassword}
                    onChange={(e) => setRegPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-10 pr-4 py-2.5 bg-background border border-surface-border rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:border-volt-cyan focus:ring-1 focus:ring-volt-cyan transition"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-1.5">
                  Confirm Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-500">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    type="password"
                    required
                    minLength={8}
                    value={regConfirmPassword}
                    onChange={(e) => setRegConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-10 pr-4 py-2.5 bg-background border border-surface-border rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:border-volt-cyan focus:ring-1 focus:ring-volt-cyan transition"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full py-2.5 px-4 rounded-lg bg-gradient-to-r from-brand-600 to-volt-cyan hover:opacity-95 text-white text-sm font-semibold shadow-lg shadow-brand-500/20 flex items-center justify-center gap-2 transition disabled:opacity-50 mt-2"
              >
                {submitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Creating Account...</span>
                  </>
                ) : (
                  <>
                    <span>Create Account</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>
          )}

          {/* Security Footer Notice */}
          <div className="mt-6 pt-5 border-t border-surface-border flex items-center justify-center gap-2 text-xs text-gray-500">
            <ShieldCheck className="w-4 h-4 text-volt-emerald" />
            <span>End-to-End Encrypted Session & JWT Authentication</span>
          </div>
        </div>
      </div>
    </div>
  );
}
