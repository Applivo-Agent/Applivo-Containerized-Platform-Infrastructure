"use client";

import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
} from "react";
import { authApi } from "./api";

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  last_login_at: string | null;
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, full_name: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    try {
      const res = await authApi.me();
      setUser(res.data);
    } catch {
      logout();
    }
  }, []);

  useEffect(() => {
    const storedToken = localStorage.getItem("applivo_token");
    const storedUser = localStorage.getItem("applivo_user");
    if (storedToken) {
      setToken(storedToken);
      if (storedUser) {
        try {
          setUser(JSON.parse(storedUser));
        } catch {}
      }
      refreshUser().finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, [refreshUser]);

  const login = async (email: string, password: string) => {
    const res = await authApi.login({ email, password });
    const { access_token } = res.data;
    localStorage.setItem("applivo_token", access_token);
    setToken(access_token);
    const userRes = await authApi.me();
    setUser(userRes.data);
    localStorage.setItem("applivo_user", JSON.stringify(userRes.data));
  };

  const register = async (email: string, password: string, full_name: string) => {
    const res = await authApi.register({ email, password, full_name });
    const { access_token } = res.data;
    localStorage.setItem("applivo_token", access_token);
    setToken(access_token);
    const userRes = await authApi.me();
    setUser(userRes.data);
    localStorage.setItem("applivo_user", JSON.stringify(userRes.data));
  };

  const logout = () => {
    localStorage.removeItem("applivo_token");
    localStorage.removeItem("applivo_user");
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
