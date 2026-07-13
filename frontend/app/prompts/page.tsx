"use client";

import { useCallback, useEffect, useState } from "react";
import {
  FileText,
  Loader2,
  RotateCcw,
  Save,
} from "lucide-react";
import { getPrompts, resetPrompt, updatePrompt } from "@/lib/api";
import {
  PROMPT_SECTIONS,
  isFormatPrompt,
  type GlobalPrompt,
  type Prompt,
} from "@/lib/prompts";

export default function PromptsPage() {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [activeId, setActiveId] = useState("system");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  // Draft state for the active prompt
  const [content, setContent] = useState("");
  const [formatPrompt, setFormatPrompt] = useState("");
  const [example, setExample] = useState("");

  const active = prompts.find((p) => p.id === activeId);

  const loadPrompts = useCallback(async () => {
    try {
      const data = await getPrompts();
      setPrompts(data.prompts);
      setError("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load prompts");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadPrompts();
  }, [loadPrompts]);

  useEffect(() => {
    if (!active) return;
    if (isFormatPrompt(active)) {
      setFormatPrompt(active.format_prompt);
      setExample(active.example);
      setContent("");
    } else {
      setContent((active as GlobalPrompt).content);
      setFormatPrompt("");
      setExample("");
    }
    setMessage("");
  }, [active]);

  async function handleSave() {
    if (!active) return;
    setSaving(true);
    setMessage("");
    try {
      if (isFormatPrompt(active)) {
        await updatePrompt(active.id, { format_prompt: formatPrompt, example });
      } else {
        await updatePrompt(active.id, { content });
      }
      await loadPrompts();
      setMessage("Prompt saved — changes apply to the next generation.");
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  async function handleReset() {
    if (!active) return;
    setResetting(true);
    setMessage("");
    try {
      await resetPrompt(active.id);
      await loadPrompts();
      setMessage("Reset to default.");
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Reset failed");
    } finally {
      setResetting(false);
    }
  }

  const fileHint = PROMPT_SECTIONS.flatMap((s) => s.items).find(
    (i) => i.id === activeId
  )?.file;

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-brand-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="animate-fade-up max-w-2xl">
        <p className="step-label mb-3">
          <span className="step-num">AI</span>
          Prompt studio
        </p>
        <h1 className="font-display text-3xl font-semibold tracking-tight text-ink sm:text-4xl">
          Prompts
        </h1>
        <p className="mt-2 text-ink-muted">
          Tune the system voice and each platform format. Saves apply on the next run.
        </p>
      </div>

      {error && (
        <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">
          {error}
        </div>
      )}

      <div className="flex flex-col gap-6 lg:flex-row">
        {/* Sidebar */}
        <aside className="w-full shrink-0 lg:w-56">
          <nav className="panel space-y-4 p-3">
            {PROMPT_SECTIONS.map((section) => (
              <div key={section.title}>
                <p className="px-2 text-xs font-semibold uppercase tracking-[0.12em] text-ink-soft">
                  {section.title}
                </p>
                <ul className="mt-1 space-y-0.5">
                  {section.items.map((item) => {
                    const p = prompts.find((pr) => pr.id === item.id);
                    const isActive = activeId === item.id;
                    return (
                      <li key={item.id}>
                        <button
                          onClick={() => setActiveId(item.id)}
                          className={`flex w-full items-center justify-between rounded-lg px-3 py-2 text-left text-sm transition-colors ${
                            isActive
                              ? "bg-brand-50 font-semibold text-brand-800"
                              : "text-ink-muted hover:bg-surface-sunken hover:text-ink"
                          }`}
                        >
                          <span>{item.label}</span>
                          {p?.is_customized && (
                            <span className="h-1.5 w-1.5 rounded-full bg-amber-500" title="Customized" />
                          )}
                        </button>
                      </li>
                    );
                  })}
                </ul>
              </div>
            ))}
          </nav>
        </aside>

        {/* Editor */}
        <div className="min-w-0 flex-1 space-y-4">
          {active && (
            <>
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h2 className="font-display text-xl font-semibold text-ink">{active.label}</h2>
                  {fileHint && (
                    <p className="mt-0.5 flex items-center gap-1 text-xs text-ink-soft">
                      <FileText className="h-3 w-3" />
                      prompts/{fileHint}
                      {active.is_customized && (
                        <span className="ml-2 rounded-md bg-amber-100 px-1.5 py-0.5 text-amber-800">
                          customized
                        </span>
                      )}
                    </p>
                  )}
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={handleReset}
                    disabled={resetting || !active.is_customized}
                    className="inline-flex items-center gap-1.5 rounded-xl border border-brand-900/10 px-3 py-2 text-sm text-ink-muted hover:bg-surface-sunken disabled:opacity-40"
                  >
                    {resetting ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <RotateCcw className="h-4 w-4" />
                    )}
                    Reset
                  </button>
                  <button
                    onClick={handleSave}
                    disabled={saving}
                    className="btn-primary"
                  >
                    {saving ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Save className="h-4 w-4" />
                    )}
                    Save Prompt
                  </button>
                </div>
              </div>

              {active.placeholders.length > 0 && (
                <div className="rounded-xl border border-brand-200 bg-brand-50 px-4 py-3 text-xs text-brand-900">
                  <span className="font-semibold">Placeholders: </span>
                  {active.placeholders.map((ph) => (
                    <code key={ph} className="mx-1 rounded-md bg-white/80 px-1.5 py-0.5">
                      {ph}
                    </code>
                  ))}
                  <span className="ml-1 text-brand-700">— filled automatically at generation.</span>
                </div>
              )}

              {isFormatPrompt(active) ? (
                <div>
                  <label className="mb-1.5 block text-sm font-medium text-ink">
                    Format Prompt
                  </label>
                  <textarea
                    value={formatPrompt}
                    onChange={(e) => setFormatPrompt(e.target.value)}
                    rows={24}
                    className="field font-mono text-[13px] leading-relaxed"
                    spellCheck={false}
                  />
                </div>
              ) : (
                <div>
                  <label className="mb-1.5 block text-sm font-medium text-ink">
                    Prompt Text
                  </label>
                  <textarea
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    rows={22}
                    className="field font-mono text-[13px] leading-relaxed"
                    spellCheck={false}
                  />
                </div>
              )}

              {message && (
                <p
                  className={`text-sm ${
                    message.includes("failed") || message.includes("error")
                      ? "text-red-600"
                      : "text-green-600"
                  }`}
                >
                  {message}
                </p>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
