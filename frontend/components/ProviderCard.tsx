"use client";

import { useEffect, useState } from "react";
import {
  CheckCircle2,
  Eye,
  EyeOff,
  Loader2,
  Save,
  Wifi,
  XCircle,
  Zap,
} from "lucide-react";
import { updateProvider, testProvider } from "@/lib/api";
import { useToast } from "@/components/Toast";
import type { ProviderConfig } from "@/lib/types";

interface Props {
  provider: ProviderConfig;
  onUpdate: () => void;
}

function resolveModel(provider: ProviderConfig, current?: string): string {
  const ids = provider.available_models.map((m) => m.id);
  const candidate = current ?? provider.model;
  if (ids.includes(candidate)) return candidate;
  return ids[0] || provider.model;
}

export default function ProviderCard({ provider, onUpdate }: Props) {
  const { showToast } = useToast();
  const [enabled, setEnabled] = useState(provider.enabled);
  const [apiKey, setApiKey] = useState("");
  const [showKey, setShowKey] = useState(false);
  const [model, setModel] = useState(() => resolveModel(provider));
  const [baseUrl, setBaseUrl] = useState(provider.base_url || "");
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{
    success: boolean;
    message: string;
    latency_ms?: number;
  } | null>(null);
  const [saveMessage, setSaveMessage] = useState("");
  const [keyError, setKeyError] = useState("");

  useEffect(() => {
    setEnabled(provider.enabled);
    setModel(resolveModel(provider));
    setBaseUrl(provider.base_url || "");
  }, [provider]);

  const initial = provider.name.slice(0, 1).toUpperCase();
  const safeModel = resolveModel(provider, model);

  function canTest(): boolean {
    if (apiKey.trim()) return validateKey(apiKey);
    if (provider.has_api_key) {
      setKeyError("");
      return true;
    }
    setKeyError("Paste your API key, or save one first");
    return false;
  }

  function canSave(): boolean {
    if (!enabled) {
      setKeyError("");
      return true;
    }
    if (apiKey.trim()) return validateKey(apiKey);
    if (provider.has_api_key) {
      setKeyError("");
      return true;
    }
    setKeyError("API key is required to enable this provider");
    return false;
  }

  function validateKey(key: string): boolean {
    if (!key && !provider.has_api_key) {
      setKeyError("API key is required");
      return false;
    }
    if (key && key.length < 8) {
      setKeyError("API key appears too short");
      return false;
    }
    setKeyError("");
    return true;
  }

  async function handleTest() {
    if (!canTest()) return;
    setTesting(true);
    setTestResult(null);
    try {
      const result = await testProvider(provider.provider_id, {
        api_key: apiKey || undefined,
        model: safeModel,
        base_url: baseUrl || undefined,
      });
      setTestResult(result);
      showToast(result.message, result.success ? "success" : "error");
    } catch (e) {
      setTestResult({
        success: false,
        message: e instanceof Error ? e.message : "Test failed",
      });
      showToast(e instanceof Error ? e.message : "Test failed", "error");
    } finally {
      setTesting(false);
    }
  }

  async function handleSave() {
    if (!canSave()) return;
    setSaving(true);
    setSaveMessage("");
    try {
      await updateProvider(provider.provider_id, {
        enabled,
        api_key: apiKey || undefined,
        model: safeModel,
        base_url: baseUrl || undefined,
      });
      setApiKey("");
      setModel(safeModel);
      setSaveMessage("Settings saved successfully");
      showToast("Provider settings saved", "success");
      onUpdate();
      setTimeout(() => setSaveMessage(""), 3000);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Save failed";
      setSaveMessage(msg);
      showToast(msg, "error");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div
      className={`panel transition-all ${
        enabled ? "ring-2 ring-brand-500/15 border-brand-300" : ""
      }`}
    >
      <div className="flex items-center justify-between border-b border-brand-900/5 px-5 py-4 sm:px-6">
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-100 font-display text-sm font-bold text-brand-800">
            {initial}
          </span>
          <div>
            <h3 className="font-display font-semibold text-ink">{provider.name}</h3>
            <p className="text-xs text-ink-muted">{provider.description}</p>
          </div>
        </div>

        <label className="relative inline-flex cursor-pointer items-center gap-2.5">
          <input
            type="checkbox"
            checked={enabled}
            onChange={(e) => setEnabled(e.target.checked)}
            className="peer sr-only"
          />
          <div
            className={`relative h-7 w-12 rounded-full transition-colors duration-200 ${
              enabled
                ? "bg-brand-600 shadow-[inset_0_0_0_1px_rgba(15,122,103,0.3)]"
                : "bg-brand-900/12"
            }`}
          >
            <span
              className={`absolute top-0.5 left-0.5 h-6 w-6 rounded-full bg-white shadow-md transition-transform duration-200 ${
                enabled ? "translate-x-5" : "translate-x-0"
              }`}
            />
          </div>
          <span
            className={`text-xs font-semibold uppercase tracking-wide ${
              enabled ? "text-brand-700" : "text-ink-soft"
            }`}
          >
            {enabled ? "On" : "Off"}
          </span>
        </label>
      </div>

      <div className="space-y-4 px-5 py-5 sm:px-6">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-ink">
            API Key
            {provider.has_api_key && !apiKey && (
              <span className="ml-2 text-xs font-normal text-brand-700">
                (saved: {provider.api_key_masked})
              </span>
            )}
          </label>
          <div className="relative">
            <input
              type={showKey ? "text" : "password"}
              value={apiKey}
              onChange={(e) => {
                setApiKey(e.target.value);
                setKeyError("");
              }}
              placeholder={
                provider.has_api_key ? "Enter new key to replace..." : "Paste your API key"
              }
              className={`field pr-10 ${
                keyError ? "border-rose-300 focus:border-rose-500 focus:ring-rose-500/20" : ""
              }`}
            />
            <button
              type="button"
              onClick={() => setShowKey(!showKey)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-ink-soft hover:text-ink"
            >
              {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
          {keyError && <p className="mt-1 text-xs text-rose-600">{keyError}</p>}
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-ink">Model</label>
          <select
            value={safeModel}
            onChange={(e) => setModel(e.target.value)}
            className="field"
          >
            {provider.available_models.map((m) => (
              <option key={m.id} value={m.id}>
                {m.name}
                {m.modality === "image" ? " (image)" : ""}
              </option>
            ))}
          </select>
        </div>

        {(provider.provider_id === "openrouter" ||
          provider.provider_id === "deepseek") && (
          <div>
            <label className="mb-1.5 block text-sm font-medium text-ink">
              Base URL{" "}
              <span className="text-xs font-normal text-ink-soft">(optional)</span>
            </label>
            <input
              type="text"
              value={baseUrl}
              onChange={(e) => setBaseUrl(e.target.value)}
              placeholder={provider.base_url || "https://..."}
              className="field"
            />
          </div>
        )}

        {testResult && (
          <div
            className={`flex items-start gap-2 rounded-xl px-3 py-2 text-sm ${
              testResult.success
                ? "bg-brand-50 text-brand-800"
                : "bg-rose-50 text-rose-800"
            }`}
          >
            {testResult.success ? (
              <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0" />
            ) : (
              <XCircle className="mt-0.5 h-4 w-4 shrink-0" />
            )}
            <div>
              <p>{testResult.message}</p>
              {testResult.latency_ms != null && (
                <p className="mt-0.5 text-xs opacity-75">Latency: {testResult.latency_ms}ms</p>
              )}
            </div>
          </div>
        )}

        {saveMessage && (
          <p
            className={`text-sm ${
              saveMessage.includes("success") ? "text-brand-700" : "text-rose-600"
            }`}
          >
            {saveMessage}
          </p>
        )}

        <div className="flex flex-wrap items-center gap-3 pt-1">
          <button
            onClick={handleTest}
            disabled={testing}
            className="inline-flex items-center gap-2 rounded-xl border border-brand-900/10 px-4 py-2 text-sm font-medium text-ink hover:bg-surface-sunken disabled:opacity-50"
          >
            {testing ? <Loader2 className="h-4 w-4 animate-spin" /> : <Wifi className="h-4 w-4" />}
            Test
          </button>
          <button onClick={handleSave} disabled={saving} className="btn-primary">
            {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
            Save
          </button>
          {enabled && provider.has_api_key && (
            <span className="ml-auto flex items-center gap-1 text-xs font-medium text-brand-700">
              <Zap className="h-3 w-3" /> Active
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
