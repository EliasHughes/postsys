import { createContext, useContext, useEffect, useState } from "react";
import { api, login as doLogin } from "../services/api";

export type Me = {
  id: number;
  username: string;
  full_name: string;
  company_id: number;
  branch_id: number | null;
  roles: string[];
  permissions: string[];
};

type Ctx = {
  user: Me | null;
  loading: boolean;
  login: (u: string, p: string) => Promise<void>;
  logout: () => void;
  can: (code: string) => boolean;
};

const AuthCtx = createContext<Ctx>(null!);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<Me | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const t = localStorage.getItem("cp_access");
    if (!t) {
      setLoading(false);
      return;
    }
    api<Me>("/auth/me")
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  async function login(u: string, p: string) {
    await doLogin(u, p);
    const me = await api<Me>("/auth/me");
    setUser(me);
  }

  function logout() {
    localStorage.removeItem("cp_access");
    localStorage.removeItem("cp_refresh");
    setUser(null);
  }

  function can(code: string) {
    if (!user) return false;
    return user.permissions.includes("*") || user.permissions.includes(code);
  }

  return (
    <AuthCtx.Provider value={{ user, loading, login, logout, can }}>
      {children}
    </AuthCtx.Provider>
  );
}

export const useAuth = () => useContext(AuthCtx);
