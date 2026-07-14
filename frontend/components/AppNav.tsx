"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { LogOut, Settings, Sparkles, User } from "lucide-react";
import { clearAuth } from "@/lib/auth";
import { useAuth } from "@/components/AuthProvider";
import { useToast } from "@/components/Toast";

export default function AppNav() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, setUser } = useAuth();
  const { showToast } = useToast();
  const isAuthPage = pathname.startsWith("/login") || pathname.startsWith("/register");

  if (isAuthPage) return null;

  function handleLogout() {
    clearAuth();
    setUser(null);
    showToast("Signed out successfully", "success");
    router.push("/login");
  }

  return (
    <nav className="glass-nav sticky top-0 z-40">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-3.5 sm:px-6">
        <Link href="/" className="group flex items-center gap-3">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-700 text-sm font-bold text-white shadow-lift transition-transform duration-200 group-hover:scale-105">
            R
          </span>
          <span className="font-display text-lg font-semibold tracking-tight text-ink">
            Repurposer
          </span>
        </Link>

        <div className="flex items-center gap-1 sm:gap-2">
          <Link
            href="/"
            className={`btn-ghost hidden sm:inline-flex ${pathname === "/" ? "text-ink" : ""}`}
          >
            <Sparkles className="h-3.5 w-3.5" />
            Create
          </Link>
          <Link
            href="/settings"
            className="ml-1 inline-flex items-center gap-1.5 rounded-xl border border-brand-900/10 bg-white px-3 py-1.5 text-sm font-medium text-ink transition-colors hover:border-brand-300 hover:bg-brand-50"
          >
            <Settings className="h-3.5 w-3.5 text-brand-700" />
            <span className="hidden sm:inline">Settings</span>
          </Link>
          {user && (
            <span className="hidden items-center gap-1.5 rounded-xl bg-brand-50 px-2.5 py-1.5 text-xs font-medium text-brand-800 md:inline-flex">
              <User className="h-3.5 w-3.5" />
              {user.name || user.email}
            </span>
          )}
          <button
            type="button"
            onClick={handleLogout}
            className="inline-flex items-center gap-1.5 rounded-xl border border-brand-900/10 px-3 py-1.5 text-sm text-ink-muted transition-colors hover:bg-rose-50 hover:text-rose-700"
          >
            <LogOut className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">Logout</span>
          </button>
        </div>
      </div>
    </nav>
  );
}
