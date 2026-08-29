"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";

export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string | null;
  role: string;
  is_active: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (usernameOrEmail: string, password: string) => Promise<{ success: boolean; error?: string }>;
  register: (name: string, email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_KEY = "volt_access_token";
const USER_KEY = "volt_user_profile";

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    try {
      const storedToken = localStorage.getItem(TOKEN_KEY);
      const storedUser = localStorage.getItem(USER_KEY);

      if (storedToken && storedUser) {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
      }
    } catch (e) {
      console.error("Failed to restore authentication session:", e);
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const login = async (usernameOrEmail: string, password: string): Promise<{ success: boolean; error?: string }> => {
    try {
      const endpoint = "/api/v1/auth/login";
      const directUrl = "http://127.0.0.1:8000/api/v1/auth/login";

      let response: Response;
      try {
        response = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            username_or_email: usernameOrEmail.trim(),
            password: password,
          }),
        });
      } catch (proxyError) {
        // Fallback to direct backend URL if proxy rewrite fails
        response = await fetch(directUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            username_or_email: usernameOrEmail.trim(),
            password: password,
          }),
        });
      }

      const result = await response.json();

      if (!response.ok || !result.success) {
        const errorMsg = result.detail || result.message || "Invalid email/username or password";
        return { success: false, error: errorMsg };
      }

      const tokenData = result.data;
      const accessToken = tokenData.access_token;
      const userProfile: User = tokenData.user;

      setToken(accessToken);
      setUser(userProfile);

      localStorage.setItem(TOKEN_KEY, accessToken);
      localStorage.setItem(USER_KEY, JSON.stringify(userProfile));

      return { success: true };
    } catch (err: any) {
      return { success: false, error: err.message || "Connection failed. Please ensure the backend is running." };
    }
  };

  const register = async (name: string, email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    try {
      const trimmedEmail = email.trim();
      const derivedUsername = trimmedEmail.split("@")[0].replace(/[^a-zA-Z0-9_]/g, "_");
      
      const endpoint = "/api/v1/auth/register";
      const directUrl = "http://127.0.0.1:8000/api/v1/auth/register";

      const payload = {
        email: trimmedEmail,
        username: derivedUsername.length >= 3 ? derivedUsername : `${derivedUsername}_user`,
        full_name: name.trim(),
        password: password,
        role: "ml_engineer",
      };

      let response: Response;
      try {
        response = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      } catch (proxyError) {
        response = await fetch(directUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      }

      const result = await response.json();

      if (!response.ok || !result.success) {
        const errorMsg = result.detail || result.message || "Registration failed. Email might already exist.";
        return { success: false, error: errorMsg };
      }

      return { success: true };
    } catch (err: any) {
      return { success: false, error: err.message || "Registration connection failed." };
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    try {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
    } catch (e) {
      console.error("Error clearing session:", e);
    }
    router.push("/login");
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
