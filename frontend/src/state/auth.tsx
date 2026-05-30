import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { Api } from "@/lib/api";
import type { AuthUser, RegisterPayload } from "@/lib/types";

export const TOKEN_KEY = "sp-token";

type Status = "loading" | "authed" | "guest";

interface AuthContextValue {
  user: AuthUser | null;
  status: Status;
  login: (email: string, password: string) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [status, setStatus] = useState<Status>("loading");

  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) {
      setStatus("guest");
      return;
    }
    Api.auth
      .me()
      .then((u) => {
        setUser(u);
        setStatus("authed");
      })
      .catch(() => {
        localStorage.removeItem(TOKEN_KEY);
        setStatus("guest");
      });
  }, []);

  const apply = (res: { access_token: string; user: AuthUser }) => {
    localStorage.setItem(TOKEN_KEY, res.access_token);
    setUser(res.user);
    setStatus("authed");
  };

  const login = async (email: string, password: string) => {
    apply(await Api.auth.login({ email, password }));
  };
  const register = async (payload: RegisterPayload) => {
    apply(await Api.auth.register(payload));
  };
  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    setUser(null);
    setStatus("guest");
  };

  return (
    <AuthContext.Provider value={{ user, status, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
