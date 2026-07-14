"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { CheckCircle2, Info, X, XCircle } from "lucide-react";

type ToastType = "success" | "error" | "info";

interface Toast {
  id: number;
  message: string;
  type: ToastType;
}

interface ToastContextValue {
  showToast: (message: string, type?: ToastType) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

const STYLES: Record<ToastType, string> = {
  success: "border-l-brand-600 bg-white text-ink",
  error: "border-l-rose-500 bg-white text-ink",
  info: "border-l-sky-500 bg-white text-ink",
};

const ICON_STYLES: Record<ToastType, string> = {
  success: "bg-brand-50 text-brand-700",
  error: "bg-rose-50 text-rose-600",
  info: "bg-sky-50 text-sky-600",
};

const ICONS: Record<ToastType, typeof Info> = {
  success: CheckCircle2,
  error: XCircle,
  info: Info,
};

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const dismiss = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const showToast = useCallback((message: string, type: ToastType = "info") => {
    const id = Date.now() + Math.random();
    setToasts((prev) => [...prev.slice(-2), { id, message, type }]);
    window.setTimeout(() => dismiss(id), 4200);
  }, [dismiss]);

  const value = useMemo(() => ({ showToast }), [showToast]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div
        className="pointer-events-none fixed right-4 top-4 z-[200] flex w-[min(100%-2rem,22rem)] flex-col gap-2.5 sm:right-6 sm:top-5"
        aria-live="polite"
      >
        {toasts.map((toast) => {
          const Icon = ICONS[toast.type];
          return (
            <div
              key={toast.id}
              className={`toast-slide-in pointer-events-auto flex items-start gap-3 rounded-xl border border-brand-900/8 border-l-[3px] px-3.5 py-3 shadow-[0_8px_30px_rgba(16,35,31,0.12)] backdrop-blur-sm ${STYLES[toast.type]}`}
            >
              <span
                className={`mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg ${ICON_STYLES[toast.type]}`}
              >
                <Icon className="h-3.5 w-3.5" />
              </span>
              <p className="flex-1 pt-0.5 text-[13px] font-medium leading-snug tracking-tight">
                {toast.message}
              </p>
              <button
                type="button"
                onClick={() => dismiss(toast.id)}
                className="rounded-md p-1 text-ink-soft transition-colors hover:bg-surface-sunken hover:text-ink"
                aria-label="Dismiss"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}
