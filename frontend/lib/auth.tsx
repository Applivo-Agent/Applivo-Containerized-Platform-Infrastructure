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
  verifyLoginOtp: (email: string, otp: string) => Promise<void>;
  loginWithGoogle: (idToken: string) => Promise<void>;
  register: (email: string, password: string, full_name: string) => Promise<void>;
  verifyRegisterOtp: (email: string, otp: string, userData: { password: string; full_name: string }) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } catch {}
    localStorage.removeItem("applivo_token");
    localStorage.removeItem("applivo_user");
    setToken(null);
    setUser(null);
  }, []);

  const refreshUser = useCallback(async () => {
    try {
      const res = await authApi.me();
      setUser(res.data);
    } catch {
      logout();
    }
  }, [logout]);

  // eslint-disable-next-line react-hooks/set-state-in-effect
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
    await authApi.loginInitiate({ email, password });
  };

  const verifyLoginOtp = async (email: string, otp: string) => {
    const res = await authApi.loginVerify({ email, otp, purpose: "login" });
    const { access_token } = res.data;
    localStorage.setItem("applivo_token", access_token);
    setToken(access_token);
    const userRes = await authApi.me();
    setUser(userRes.data);
    localStorage.setItem("applivo_user", JSON.stringify(userRes.data));
  };

  const loginWithGoogle = async (idToken: string) => {
    const res = await authApi.googleLogin(idToken);
    const { access_token } = res.data;
    localStorage.setItem("applivo_token", access_token);
    setToken(access_token);
    const userRes = await authApi.me();
    setUser(userRes.data);
    localStorage.setItem("applivo_user", JSON.stringify(userRes.data));
  };

  const register = async (email: string, password: string, full_name: string) => {
    await authApi.registerInitiate({ email, password, full_name });
  };

  const verifyRegisterOtp = async (email: string, otp: string, userData: { password: string; full_name: string }) => {
    const res = await authApi.registerVerify({ email, otp, purpose: "register" }, userData);
    const { access_token } = res.data;
    localStorage.setItem("applivo_token", access_token);
    setToken(access_token);
    const userRes = await authApi.me();
    setUser(userRes.data);
    localStorage.setItem("applivo_user", JSON.stringify(userRes.data));
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        isAuthenticated: !!user,
        login,
        verifyLoginOtp,
        loginWithGoogle,
        register,
        verifyRegisterOtp,
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
