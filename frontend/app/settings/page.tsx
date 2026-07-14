"use client";

import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";
import ProviderCard from "@/components/ProviderCard";
import OpenAITip from "@/components/OpenAITip";
import { useToast } from "@/components/Toast";
import { getProviders } from "@/lib/api";
import type { ProviderConfig } from "@/lib/types";

export default function SettingsPage() {
  const { showToast } = useToast();
  const [providers, setProviders] = useState<ProviderConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadProviders() {
    try {
      const data = await getProviders();
      setProviders(data);
      setError("");
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

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-brand-600" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="animate-fade-up max-w-2xl">
        <p className="step-label mb-3">
          <span className="step-num">LLM</span>
          Providers
        </p>
        <h1 className="font-display text-3xl font-semibold tracking-tight text-ink sm:text-4xl">
          Settings
        </h1>
        <p className="mt-2 text-ink-muted">
          Connect an API key. Keys are encrypted on the server and never shown again after saving.
        </p>
      </div>

      <OpenAITip />

      {error && (
        <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">
          {error}
          <p className="mt-1 text-xs text-rose-600">
            Settings are stored in MongoDB Atlas only. Ensure MONGODB_URI and ENCRYPTION_KEY
            are set on the server, then save your API key below.
          </p>
        </div>
      )}

      <div className="grid gap-5">
        {providers.map((provider) => (
          <ProviderCard
            key={provider.provider_id}
            provider={provider}
            onUpdate={loadProviders}
          />
        ))}
      </div>

      <div className="panel p-5 text-sm text-ink-muted">
        <p className="font-display font-semibold text-ink mb-2">How it works</p>
        <ul className="space-y-1.5 list-disc list-inside">
          <li>Enable a provider and save your API key.</li>
          <li>The first enabled provider is used by default.</li>
          <li>Use Test Connection before you generate.</li>
        </ul>
      </div>
    </div>
  );
}
