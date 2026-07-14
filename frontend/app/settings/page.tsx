"use client";

import { useEffect, useState } from "react";
import { Check, KeyRound, Loader2, Shield, Sparkles } from "lucide-react";
import ProviderCard from "@/components/ProviderCard";
import OpenAITip from "@/components/OpenAITip";
import { useToast } from "@/components/Toast";
import { getProviders } from "@/lib/api";
import type { ProviderConfig, ProviderId } from "@/lib/types";

const PROVIDER_ACCENTS: Record<ProviderId, string> = {
  openai: "bg-emerald-50 text-emerald-700 ring-emerald-200 dark:bg-emerald-950/50 dark:text-emerald-300 dark:ring-emerald-800",
  gemini: "bg-sky-50 text-sky-700 ring-sky-200 dark:bg-sky-950/50 dark:text-sky-300 dark:ring-sky-800",
  anthropic: "bg-orange-50 text-orange-700 ring-orange-200 dark:bg-orange-950/50 dark:text-orange-300 dark:ring-orange-800",
  groq: "bg-violet-50 text-violet-700 ring-violet-200 dark:bg-violet-950/50 dark:text-violet-300 dark:ring-violet-800",
  openrouter: "bg-indigo-50 text-indigo-700 ring-indigo-200 dark:bg-indigo-950/50 dark:text-indigo-300 dark:ring-indigo-800",
  mistral: "bg-amber-50 text-amber-800 ring-amber-200 dark:bg-amber-950/50 dark:text-amber-300 dark:ring-amber-800",
  cohere: "bg-rose-50 text-rose-700 ring-rose-200 dark:bg-rose-950/50 dark:text-rose-300 dark:ring-rose-800",
  deepseek: "bg-teal-50 text-teal-700 ring-teal-200 dark:bg-teal-950/50 dark:text-teal-300 dark:ring-teal-800",
};

export default function SettingsPage() {
  const { showToast } = useToast();
  const [providers, setProviders] = useState<ProviderConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedId, setSelectedId] = useState<ProviderId | null>(null);

  async function loadProviders() {
    try {
      const data = await getProviders();
      setProviders(data);
      setError("");
      setSelectedId((prev) => {
        if (prev && data.some((p) => p.provider_id === prev)) return prev;
        const enabled = data.find((p) => p.enabled);
        return enabled?.provider_id ?? data[0]?.provider_id ?? null;
      });
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Failed to load providers";
      setError(msg);
      showToast(msg, "error");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadProviders();
  }, []);

  const selected = providers.find((p) => p.provider_id === selectedId);
  const enabledCount = providers.filter((p) => p.enabled).length;

  return (
    <div className="studio-shell flex-col lg:flex-row">
      {/* Left sidebar — provider list */}
      <aside className="studio-sidebar flex max-h-[38vh] flex-col lg:max-h-none">
        <div className="border-b border-brand-900/6 px-4 py-4 sm:px-5 dark:border-brand-200/10">
          <p className="step-label">
            <span className="step-num">LLM</span>
            Providers
          </p>
          <p className="mt-1.5 text-xs text-ink-muted">
            {loading
              ? "Loading…"
              : `${enabledCount} of ${providers.length} enabled`}
          </p>
        </div>

        <div className="flex-1 overflow-y-auto px-2 py-2 sm:px-3">
          {loading ? (
            <div className="flex flex-col items-center gap-2 py-10">
              <Loader2 className="h-6 w-6 animate-spin text-brand-600" />
              <p className="text-xs text-ink-muted">Loading providers…</p>
            </div>
          ) : (
            <div className="space-y-1">
              {providers.map((provider) => {
                const active = selectedId === provider.provider_id;
                const accent = PROVIDER_ACCENTS[provider.provider_id];
                const initial = provider.name.slice(0, 1).toUpperCase();
                return (
                  <button
                    key={provider.provider_id}
                    type="button"
                    onClick={() => setSelectedId(provider.provider_id)}
                    className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left transition-all ${
                      active
                        ? "bg-brand-50 ring-1 ring-brand-400/40 dark:bg-brand-900/40 dark:ring-brand-500/40"
                        : "hover:bg-surface-sunken"
                    }`}
                  >
                    <div
                      className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ring-1 ring-inset font-display text-xs font-bold ${accent}`}
                    >
                      {initial}
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-semibold text-ink">
                        {provider.name}
                      </p>
                      <p className="truncate text-[11px] text-ink-muted">
                        {provider.enabled
                          ? provider.has_api_key
                            ? "Enabled · key saved"
                            : "Enabled · no key"
                          : "Disabled"}
                      </p>
                    </div>
                    <span
                      className={`flex h-2 w-2 shrink-0 rounded-full ${
                        provider.enabled
                          ? "bg-brand-500 shadow-[0_0_8px_rgba(54,184,154,0.8)]"
                          : "bg-ink-soft/40"
                      }`}
                      aria-hidden
                    />
                  </button>
                );
              })}
            </div>
          )}
        </div>

        <div className="hidden border-t border-brand-900/6 p-4 lg:block dark:border-brand-200/10">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-brand-700 dark:text-brand-400">
            Quick tips
          </p>
          <ul className="space-y-2 text-xs text-ink-muted">
            <li className="flex gap-2">
              <KeyRound className="mt-0.5 h-3.5 w-3.5 shrink-0 text-brand-600" />
              Keys are encrypted in MongoDB
            </li>
            <li className="flex gap-2">
              <Shield className="mt-0.5 h-3.5 w-3.5 shrink-0 text-brand-600" />
              Test connection before generating
            </li>
            <li className="flex gap-2">
              <Sparkles className="mt-0.5 h-3.5 w-3.5 shrink-0 text-brand-600" />
              First enabled provider is used
            </li>
          </ul>
        </div>
      </aside>

      {/* Main workspace */}
      <div className="studio-main min-h-0 flex-1">
        <div className="flex h-full flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto px-4 py-5 sm:px-6 lg:px-8 lg:py-6">
            <header className="mb-4">
              <h1 className="font-display text-xl font-semibold text-ink sm:text-2xl">
                Settings
              </h1>
              <p className="mt-1 text-sm text-ink-muted">
                Connect an API key — encrypted on the server and never shown again.
              </p>
            </header>

            <div className="mb-5">
              <OpenAITip />
            </div>

            {error && (
              <div className="mb-5 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800 dark:border-rose-900 dark:bg-rose-950/40 dark:text-rose-200">
                {error}
                <p className="mt-1 text-xs opacity-80">
                  Ensure MONGODB_URI and ENCRYPTION_KEY are set on the server.
                </p>
              </div>
            )}

            {!loading && selected && (
              <ProviderCard
                key={selected.provider_id}
                provider={selected}
                accent={PROVIDER_ACCENTS[selected.provider_id]}
                onUpdate={loadProviders}
              />
            )}

            {!loading && !selected && providers.length === 0 && (
              <div className="panel flex flex-col items-center gap-2 p-10 text-center">
                <p className="text-sm text-ink-muted">No providers found.</p>
              </div>
            )}
          </div>

          {/* Footer bar — matches Create page */}
          <div className="shrink-0 border-t border-brand-900/8 px-4 py-3 sm:px-6 lg:px-8 dark:border-brand-200/10">
            <div className="flex flex-wrap items-center justify-between gap-2 text-sm">
              <p className="text-ink-muted">
                <span className="font-semibold text-brand-700 dark:text-brand-400">
                  {enabledCount}
                </span>{" "}
                provider{enabledCount !== 1 ? "s" : ""} ready
              </p>
              <p className="flex items-center gap-1.5 text-xs text-ink-soft">
                <Check className="h-3.5 w-3.5 text-brand-600" />
                Select a provider in the sidebar to configure
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
