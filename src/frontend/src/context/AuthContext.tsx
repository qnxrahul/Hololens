import { createContext, useContext, useEffect, useMemo, useState } from "react";

const tokenStorageKey = import.meta.env.VITE_AUTH_TOKEN_KEY ?? "viv_auth_token";

interface AuthContextValue {
  token?: string;
  setToken: (token?: string) => void;
  clearToken: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setTokenState] = useState<string | undefined>(undefined);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    const stored = window.localStorage.getItem(tokenStorageKey);
    if (stored) {
      setTokenState(stored);
    }
  }, []);

  const writeToken = (value?: string) => {
    setTokenState(value);
    if (typeof window === "undefined") {
      return;
    }
    if (value && value.trim().length > 0) {
      window.localStorage.setItem(tokenStorageKey, value);
    } else {
      window.localStorage.removeItem(tokenStorageKey);
    }
  };

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      setToken: writeToken,
      clearToken: () => writeToken(undefined),
    }),
    [token],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}

