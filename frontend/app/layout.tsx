import type { Metadata } from "next";
import { Figtree, Sora } from "next/font/google";
import { Providers } from "@/components/Providers";
import AppNav from "@/components/AppNav";
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
        <Providers>
          <div className="page-shell">
            <AppNav />
            <main className="mx-auto max-w-6xl px-5 py-8 sm:px-6 sm:py-10">
              {children}
            </main>
          </div>
        </Providers>
      </body>
    </html>
  );
}
