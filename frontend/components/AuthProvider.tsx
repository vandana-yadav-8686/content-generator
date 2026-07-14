"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { usePathname, useRouter } from "next/navigation";
import { getStoredUser, getToken } from "@/lib/auth";
import { fetchMe } from "@/lib/api";
import type { User } from "@/lib/types";

const PUBLIC_PATHS = ["/login", "/register"];

interface AuthContextValue {
  user: User | null;
  setUser: (user: User | null) => void;
}

const AuthContext = createContext<AuthContextValue>({
  user: null,
  setUser: () => {},
});

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [ready, setReady] = useState(false);
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function check() {
      const isPublic = PUBLIC_PATHS.some((p) => pathname.startsWith(p));
      const token = getToken();

      if (!token) {
        if (!isPublic) router.replace("/login");
        if (!cancelled) {
          setUser(null);
          setReady(true);
        }
        return;
      }

      if (isPublic) {
        router.replace("/");
        return;
      }

      try {
        const me = await fetchMe();
        if (!cancelled) {
          setUser(me);
          setReady(true);
        }
      } catch {
        if (!cancelled) {
          setUser(null);
          router.replace("/login");
          setReady(true);
        }
      }
    }

    check();
    return () => {
      cancelled = true;
    };
  }, [pathname, router]);

  if (!ready) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-brand-200 border-t-brand-700" />
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ user, setUser }}>{children}</AuthContext.Provider>
  );
}
