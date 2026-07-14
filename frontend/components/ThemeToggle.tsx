"use client";

import { useRef } from "react";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "@/components/ThemeProvider";

export default function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const isDark = theme === "dark";
  const btnRef = useRef<HTMLButtonElement>(null);

  function setTransitionOrigin() {
    const btn = btnRef.current;
    const root = document.documentElement;
    if (btn) {
      const rect = btn.getBoundingClientRect();
      root.style.setProperty("--theme-x", `${rect.left + rect.width / 2}px`);
      root.style.setProperty("--theme-y", `${rect.top + rect.height / 2}px`);
    } else {
      root.style.setProperty("--theme-x", "calc(100% - 2.5rem)");
      root.style.setProperty("--theme-y", "2rem");
    }
  }

  function handleToggle() {
    const next = isDark ? "light" : "dark";
    setTransitionOrigin();

    const apply = () => setTheme(next);

    const doc = document as Document & {
      startViewTransition?: (callback: () => void) => { finished: Promise<void> };
    };

    if (typeof doc.startViewTransition === "function") {
      doc.startViewTransition(apply);
      return;
    }

    // Fallback: smooth circular overlay
    const overlay = document.createElement("div");
    overlay.className = "theme-transition-fallback";
    overlay.setAttribute("aria-hidden", "true");
    document.body.appendChild(overlay);
    requestAnimationFrame(() => overlay.classList.add("theme-transition-fallback-active"));

    window.setTimeout(apply, 150);

    window.setTimeout(() => {
      overlay.remove();
    }, 1700);
  }

  return (
    <button
      ref={btnRef}
      type="button"
      onClick={handleToggle}
      title={isDark ? "Switch to light mode" : "Switch to dark mode"}
      aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
      className="theme-toggle-btn relative rounded-lg p-2 text-ink-muted transition-colors hover:bg-surface-sunken hover:text-ink"
    >
      <span className="theme-toggle-icons" aria-hidden>
        <Sun
          className={`theme-toggle-sun h-4 w-4 ${isDark ? "is-active" : ""}`}
          strokeWidth={2}
        />
        <Moon
          className={`theme-toggle-moon h-4 w-4 ${!isDark ? "is-active" : ""}`}
          strokeWidth={2}
        />
      </span>
    </button>
  );
}
