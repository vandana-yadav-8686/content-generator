import type { Metadata } from "next";
import { Figtree, Sora } from "next/font/google";
import Link from "next/link";
import { Settings } from "lucide-react";
import "./globals.css";

const display = Sora({
  subsets: ["latin"],
  variable: "--font-display",
  weight: ["500", "600", "700"],
});

const body = Figtree({
  subsets: ["latin"],
  variable: "--font-body",
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "Repurposer — Turn one article into five formats",
  description: "Transform one article into YouTube, Reel, LinkedIn, carousel, and voice-over scripts",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${display.variable} ${body.variable}`}>
      <body>
        <div className="page-shell">
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
                <Link href="/" className="btn-ghost hidden sm:inline-flex">
                  Create
                </Link>
                <Link href="/prompts" className="btn-ghost">
                  Prompts
                </Link>
                <Link
                  href="/settings"
                  className="ml-1 inline-flex items-center gap-1.5 rounded-xl border border-brand-900/10 bg-white px-3 py-1.5 text-sm font-medium text-ink transition-colors hover:border-brand-300 hover:bg-brand-50"
                >
                  <Settings className="h-3.5 w-3.5 text-brand-700" />
                  Settings
                </Link>
              </div>
            </div>
          </nav>
          <main className="mx-auto max-w-6xl px-5 py-8 sm:px-6 sm:py-10">{children}</main>
        </div>
      </body>
    </html>
  );
}
