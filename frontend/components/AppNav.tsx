"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { BookOpen, CreditCard, LogOut, Settings, Sparkles } from "lucide-react";
import { clearAuth } from "@/lib/auth";
import { useAuth } from "@/components/AuthProvider";
import { useToast } from "@/components/Toast";
import ThemeToggle from "@/components/ThemeToggle";

const NAV_ITEMS = [
  { href: "/", label: "Create", icon: Sparkles, match: (p: string) => p === "/" },
  {
    href: "/plans",
    label: "Plans",
    icon: CreditCard,
    match: (p: string) => p.startsWith("/plans"),
  },
  {
    href: "/settings",
    label: "Settings",
    icon: Settings,
    match: (p: string) => p.startsWith("/settings"),
  },
] as const;

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

  const initial = user ? (user.name || user.email).charAt(0).toUpperCase() : "?";

  return (
    <header className="sticky top-0 z-50 h-16 shrink-0 border-b border-brand-900/8 bg-surface-raised shadow-sm dark:border-brand-200/10">
      <div className="flex h-full items-center justify-between gap-4 px-4 sm:px-6">
        {/* Brand */}
        <Link href="/" className="group flex min-w-0 items-center gap-3">
          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-700 text-sm font-bold text-white shadow-md transition-transform group-hover:scale-[1.03]">
            R
          </span>
          <div className="hidden min-w-0 sm:block">
            <p className="truncate font-display text-[15px] font-semibold leading-tight text-ink">
              Repurposer
            </p>
            <p className="text-[10px] font-medium uppercase tracking-widest text-brand-600 dark:text-brand-400">
              AI Content Studio
            </p>
          </div>
        </Link>

        {/* Center nav pills */}
        <nav
          className="absolute left-1/2 hidden -translate-x-1/2 items-center gap-1 rounded-xl bg-surface-sunken p-1 md:flex"
          aria-label="Main"
        >
          {NAV_ITEMS.map(({ href, label, icon: Icon, match }) => {
            const active = match(pathname);
            return (
              <Link
                key={href}
                href={href}
                className={`inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-all ${
                  active
                    ? "bg-surface-raised text-brand-800 shadow-sm ring-1 ring-brand-900/8 dark:text-brand-300 dark:ring-brand-200/15"
                    : "text-ink-muted hover:text-brand-800 dark:hover:text-brand-300"
                }`}
              >
                <Icon className="h-4 w-4 shrink-0" />
                {label}
              </Link>
            );
          })}
        </nav>

        {/* Mobile nav */}
        <nav className="flex items-center gap-1 md:hidden" aria-label="Main mobile">
          {NAV_ITEMS.map(({ href, label, icon: Icon, match }) => {
            const active = match(pathname);
            return (
              <Link
                key={href}
                href={href}
                className={`inline-flex items-center gap-1.5 rounded-lg px-2.5 py-2 text-xs font-medium ${
                  active
                    ? "bg-brand-50 text-brand-800 dark:bg-brand-900/60 dark:text-brand-200"
                    : "text-ink-muted"
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
                {label}
              </Link>
            );
          })}
        </nav>

        {/* Right */}
        <div className="flex items-center gap-1 sm:gap-2">
          <ThemeToggle />

          <a
            href="https://github.com/vandana-yadav-8686/content-generator"
            target="_blank"
            rel="noopener noreferrer"
            title="Documentation"
            className="hidden rounded-lg p-2 text-ink-muted transition-colors hover:bg-surface-sunken hover:text-ink sm:inline-flex"
          >
            <BookOpen className="h-4 w-4" />
          </a>

          {user && (
            <div className="flex items-center gap-2 rounded-full border border-brand-900/8 bg-surface-raised py-1 pl-1 pr-3 shadow-sm dark:border-brand-200/10">
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-700 text-xs font-bold text-white">
                {initial}
              </span>
              <span className="hidden max-w-[120px] truncate text-xs font-medium text-ink lg:inline">
                {user.name || user.email.split("@")[0]}
              </span>
            </div>
          )}

          <button
            type="button"
            onClick={handleLogout}
            title="Logout"
            className="rounded-lg p-2 text-ink-muted transition-colors hover:bg-rose-50 hover:text-rose-600 dark:hover:bg-rose-950/40 dark:hover:text-rose-400"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </header>
  );
}
