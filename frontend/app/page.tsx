"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Check,
  FileUp,
  Film,
  Instagram,
  Link2,
  Linkedin,
  Loader2,
  Mic,
  Settings,
  Type,
  Wand2,
  Youtube,
} from "lucide-react";
import OutputCard from "@/components/OutputCard";
import OpenAITip from "@/components/OpenAITip";
import { useToast } from "@/components/Toast";
import { repurposeArticleStream } from "@/lib/api";
import {
  ALL_FORMATS,
  FORMAT_LABELS,
  TONE_OPTIONS,
  type RepurposeOutput,
  type ToneId,
} from "@/lib/types";

const DELIVERABLES = [
  { id: "youtube_script", icon: Youtube, accent: "bg-rose-50 text-rose-700 ring-rose-200" },
  { id: "reel_script", icon: Film, accent: "bg-teal-50 text-teal-700 ring-teal-200" },
  { id: "linkedin_post", icon: Linkedin, accent: "bg-sky-50 text-sky-700 ring-sky-200" },
  { id: "instagram_carousel", icon: Instagram, accent: "bg-fuchsia-50 text-fuchsia-700 ring-fuchsia-200" },
  { id: "voiceover_script", icon: Mic, accent: "bg-amber-50 text-amber-800 ring-amber-200" },
] as const;

function ComingSoonInputOption({
  icon: Icon,
  label,
}: {
  icon: typeof Type;
  label: string;
}) {
  return (
    <div
      className="group relative cursor-not-allowed"
      tabIndex={0}
      aria-label={`${label} — coming soon`}
    >
      <span className="inline-flex items-center gap-1.5 rounded-lg border border-dashed border-brand-900/15 bg-surface-raised px-2.5 py-1.5 text-xs font-medium text-ink-muted opacity-80 dark:border-brand-200/20">
        <Icon className="h-4 w-4 shrink-0" aria-hidden />
        {label}
      </span>
      <span
        role="tooltip"
        className="pointer-events-none absolute bottom-full left-1/2 z-10 mb-2 -translate-x-1/2 whitespace-nowrap rounded-lg bg-ink px-2.5 py-1 text-xs font-medium text-white opacity-0 shadow-lg transition-opacity duration-150 group-hover:opacity-100 group-focus-within:opacity-100"
      >
        Coming soon
        <span className="absolute left-1/2 top-full -translate-x-1/2 border-4 border-transparent border-t-ink" />
      </span>
    </div>
  );
}

export default function HomePage() {
  const { showToast } = useToast();
  const [article, setArticle] = useState("");
  const [tone, setTone] = useState<ToneId>("professional");
  const [selectedFormats, setSelectedFormats] = useState<Set<string>>(() => new Set());
  const [loading, setLoading] = useState(false);
  const [activeFormat, setActiveFormat] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [outputs, setOutputs] = useState<RepurposeOutput[]>([]);
  const [streamingFormats, setStreamingFormats] = useState<Set<string>>(new Set());
  const [meta, setMeta] = useState<{ provider: string; model: string } | null>(null);
  const [statusMessage, setStatusMessage] = useState("");

  const selectedList = ALL_FORMATS.filter((f) => selectedFormats.has(f));
  const allSelected = selectedList.length === ALL_FORMATS.length;
  const noneSelected = selectedList.length === 0;
  const canGenerate = article.trim().length >= 50 && selectedList.length > 0 && !loading;

  function toggleFormat(id: string) {
    if (loading) return;
    setSelectedFormats((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function selectAll() {
    if (loading) return;
    setSelectedFormats(new Set(ALL_FORMATS));
  }

  function clearSelection() {
    if (loading) return;
    setSelectedFormats(new Set());
  }

  function toggleSelectAll() {
    if (loading) return;
    if (allSelected) clearSelection();
    else selectAll();
  }

  async function handleRepurpose() {
    if (article.trim().length < 50) {
      setError("Article must be at least 50 characters.");
      return;
    }
    if (selectedList.length === 0) {
      setError("Select at least one format to generate.");
      return;
    }
    setError("");
    setLoading(true);
    setOutputs([]);
    setMeta(null);
    setStatusMessage("Starting…");
    setActiveFormat(null);
    setStreamingFormats(new Set());

    const liveContent: Record<string, string> = {};
    let receivedContent = false;
    let streamError = "";

    try {
      await repurposeArticleStream(
        article,
        (event) => {
          switch (event.type) {
            case "status":
              setStatusMessage(event.message);
              break;
            case "format_start":
              setActiveFormat(event.format);
              setStreamingFormats((prev) => new Set(prev).add(event.format));
              liveContent[event.format] = "";
              setOutputs((prev) => {
                const exists = prev.find((o) => o.format === event.format);
                if (exists) return prev;
                return [...prev, { format: event.format, content: "" }];
              });
              break;
            case "chunk":
              receivedContent = true;
              if (streamError) {
                streamError = "";
                setError("");
              }
              liveContent[event.format] =
                (liveContent[event.format] || "") + event.content;
              setOutputs((prev) =>
                prev.map((o) =>
                  o.format === event.format
                    ? { ...o, content: liveContent[event.format] }
                    : o
                )
              );
              break;
            case "format_done":
              receivedContent = true;
              if (streamError) {
                streamError = "";
                setError("");
              }
              liveContent[event.format] = event.content;
              setOutputs((prev) =>
                prev.map((o) =>
                  o.format === event.format ? { ...o, content: event.content } : o
                )
              );
              setStreamingFormats((prev) => {
                const next = new Set(prev);
                next.delete(event.format);
                return next;
              });
              break;
            case "done":
              setMeta({ provider: event.provider_id, model: event.model });
              setActiveFormat(null);
              setStatusMessage("");
              break;
            case "error":
              streamError = event.message;
              setError(event.message);
              showToast(event.message, "error");
              setStatusMessage("");
              break;
          }
        },
        { tone, formats: selectedList }
      );
      if (!receivedContent && !streamError) {
        setError(
          "No content was generated. Click Test Connection in Settings, try fewer formats, or pick a free model like openrouter/free."
        );
      }
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Repurposing failed";
      setError(msg);
      showToast(msg, "error");
    } finally {
      setLoading(false);
      setStreamingFormats(new Set());
      setActiveFormat(null);
    }
  }

  const outputMap = Object.fromEntries(outputs.map((o) => [o.format, o.content]));
  const buttonLabel = allSelected
    ? "Generate all 5"
    : `Generate ${selectedList.length} selected`;

  return (
    <div className="studio-shell flex-col lg:flex-row">
      {/* ── Left sidebar: formats ── */}
      <aside className="studio-sidebar flex max-h-[42vh] flex-col lg:max-h-none">
        <div className="border-b border-brand-900/6 px-4 py-4 sm:px-5">
          <p className="step-label">
            <span className="step-num">1</span>
            Choose formats
          </p>
          <p className="mt-1.5 text-xs text-ink-muted">
            {noneSelected
              ? "Pick at least one output"
              : `${selectedList.length} of ${ALL_FORMATS.length} selected`}
          </p>
          <div className="mt-3 flex gap-2">
            <button
              type="button"
              onClick={toggleSelectAll}
              disabled={loading}
              aria-pressed={allSelected}
              className={`flex-1 rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors disabled:opacity-50 ${
                allSelected
                  ? "bg-brand-700 text-white"
                  : "border border-brand-900/10 bg-surface-raised text-ink-muted hover:border-brand-300 dark:border-brand-200/15"
              }`}
            >
              {allSelected ? "All ✓" : "Select all"}
            </button>
            <button
              type="button"
              onClick={clearSelection}
              disabled={loading || noneSelected}
              className="rounded-lg border border-brand-900/10 px-3 py-1.5 text-xs font-medium text-ink-muted hover:bg-surface-raised disabled:opacity-40 dark:border-brand-200/15"
            >
              Clear
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-3 py-3 sm:px-4">
          <div className="space-y-1.5">
            {DELIVERABLES.map(({ id, icon: Icon, accent }) => {
              const selected = selectedFormats.has(id);
              const ready = Boolean(outputMap[id]) && !streamingFormats.has(id);
              const streaming = streamingFormats.has(id);
              return (
                <button
                  key={id}
                  type="button"
                  onClick={() => toggleFormat(id)}
                  disabled={loading}
                  aria-pressed={selected}
                  className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left transition-all disabled:opacity-60 ${
                    selected
                      ? "bg-brand-50 ring-1 ring-brand-400/40 dark:bg-brand-900/40 dark:ring-brand-500/40"
                      : "hover:bg-surface-sunken"
                  } ${activeFormat === id ? "ring-2 ring-brand-500" : ""}`}
                >
                  <div className={`rounded-lg p-2 ring-1 ring-inset ${accent}`}>
                    <Icon className="h-3.5 w-3.5" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-semibold text-ink">
                      {FORMAT_LABELS[id]}
                    </p>
                    {streaming && (
                      <p className="flex items-center gap-1 text-[11px] font-medium text-brand-700">
                        <Loader2 className="h-3 w-3 animate-spin" />
                        Writing…
                      </p>
                    )}
                    {ready && !streaming && (
                      <p className="flex items-center gap-1 text-[11px] font-medium text-brand-700">
                        <Check className="h-3 w-3" /> Ready
                      </p>
                    )}
                  </div>
                  <span
                    className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-md border transition-colors ${
                      selected
                        ? "border-brand-600 bg-brand-600 text-white"
                        : "border-brand-900/15 bg-surface-raised dark:border-brand-200/20"
                    }`}
                  >
                    {selected && <Check className="h-3 w-3" strokeWidth={3} />}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      </aside>

      {/* ── Main workspace ── */}
      <div className="studio-main min-h-0 flex-1">
        <div className="flex h-full flex-col overflow-hidden">
          {/* Scrollable content */}
          <div className="flex-1 overflow-y-auto">
            <div className="mx-auto w-full max-w-none px-4 py-5 sm:px-6 lg:px-8 lg:py-6">
              <div className="mb-4 space-y-3">
                <div>
                  <h1 className="font-display text-xl font-semibold text-ink sm:text-2xl">
                    Create content
                  </h1>
                  <p className="mt-0.5 text-sm text-ink-muted">
                    Paste your article and generate platform-ready copy.
                  </p>
                </div>
                <OpenAITip />
              </div>

              {error && (
                <div
                  role="alert"
                  className="mb-4 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800"
                >
                  {error}
                  {error.includes("configured") && (
                    <Link href="/settings" className="ml-1 font-semibold underline">
                      Open Settings
                    </Link>
                  )}
                </div>
              )}

              {loading && (
                <div className="mb-4 flex items-center gap-3 rounded-xl border border-brand-200 bg-surface-raised px-4 py-3 text-sm text-brand-900 shadow-soft dark:border-brand-700 dark:text-brand-100">
                  <Loader2 className="h-4 w-4 shrink-0 animate-spin text-brand-700" />
                  <div className="min-w-0 flex-1">
                    <p className="font-medium">
                      {activeFormat
                        ? `Writing ${FORMAT_LABELS[activeFormat]}…`
                        : statusMessage || "Reading your article…"}
                    </p>
                    <div className="mt-2 h-1 overflow-hidden rounded-full bg-brand-100">
                      <div className="h-full w-2/5 animate-pulse-line rounded-full bg-brand-600" />
                    </div>
                  </div>
                </div>
              )}

              {/* Article panel */}
              <section className="panel flex flex-col overflow-hidden">
                <div className="border-b border-brand-900/5 px-5 py-4">
                  <p className="step-label">
                    <span className="step-num">2</span>
                    Paste your article
                  </p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <span className="inline-flex items-center gap-1.5 rounded-lg bg-brand-700 px-3 py-1.5 text-xs font-semibold text-white">
                      <Type className="h-3.5 w-3.5" />
                      Paste text
                    </span>
                    <ComingSoonInputOption icon={Link2} label="Article URL" />
                    <ComingSoonInputOption icon={FileUp} label="Upload PDF" />
                  </div>
                </div>

                <div className="flex flex-col p-4 sm:p-5">
                  <textarea
                    value={article}
                    onChange={(e) => setArticle(e.target.value)}
                    placeholder="Paste a blog post, newsletter, or case study here…"
                    className="field min-h-[200px] flex-1 resize-none font-sans leading-relaxed sm:min-h-[260px] lg:min-h-[300px]"
                    disabled={loading}
                  />
                  <div className="mt-3 flex flex-wrap items-center justify-between gap-3 border-t border-brand-900/5 pt-3">
                    <p
                      className={`text-xs ${
                        article.trim().length >= 50 ? "text-brand-700" : "text-ink-soft"
                      }`}
                    >
                      {article.length.toLocaleString()} chars
                      {article.trim().length > 0 && article.trim().length < 50 && (
                        <span className="text-amber-700">
                          {" "}
                          · need {50 - article.trim().length} more
                        </span>
                      )}
                    </p>
                    <label className="flex items-center gap-2 text-sm text-ink-muted">
                      Tone
                      <select
                        value={tone}
                        onChange={(e) => setTone(e.target.value as ToneId)}
                        disabled={loading}
                        className="rounded-lg border border-brand-900/10 bg-surface-raised px-2.5 py-1.5 text-sm text-ink focus:border-brand-500 focus:outline-none dark:border-brand-200/15"
                      >
                        {TONE_OPTIONS.map((t) => (
                          <option key={t.id} value={t.id}>
                            {t.label}
                          </option>
                        ))}
                      </select>
                    </label>
                  </div>
                </div>
              </section>

              {meta && (
                <p className="mt-4 text-xs text-ink-soft">
                  Generated {outputs.filter((o) => o.content).length}/{selectedList.length}{" "}
                  with{" "}
                  <span className="font-medium text-ink-muted">{meta.provider}</span> ·{" "}
                  {meta.model}
                </p>
              )}

              {outputs.length > 0 && (
                <section className="mt-6 space-y-4 pb-4">
                  <h2 className="font-display text-lg font-semibold text-ink">Your content</h2>
                  {ALL_FORMATS.map((format) => {
                    const output = outputs.find((o) => o.format === format);
                    if (!output) return null;
                    return (
                      <OutputCard
                        key={format}
                        format={format}
                        content={output.content}
                        streaming={streamingFormats.has(format)}
                      />
                    );
                  })}
                </section>
              )}
            </div>
          </div>

          {/* Generate bar — fixed at bottom of main panel */}
          <div className="shrink-0 border-t border-brand-900/8 bg-surface-raised px-4 py-3 sm:px-6 lg:px-8 dark:border-brand-200/10">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="min-w-0">
                <p className="text-xs font-semibold uppercase tracking-wider text-brand-700">
                  Step 3 · Generate
                </p>
                <p className="truncate text-sm text-ink-muted">
                  {noneSelected
                    ? "Select formats in the sidebar"
                    : allSelected
                      ? "All 5 formats selected"
                      : selectedList.map((f) => FORMAT_LABELS[f]).join(", ")}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Link
                  href="/settings"
                  className="btn-ghost hidden text-xs sm:inline-flex"
                >
                  <Settings className="h-3.5 w-3.5" />
                  LLM
                </Link>
                <button
                  onClick={handleRepurpose}
                  disabled={!canGenerate}
                  className="btn-primary w-full sm:w-auto sm:min-w-[200px]"
                >
                  {loading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Wand2 className="h-4 w-4" />
                  )}
                  {loading ? "Generating…" : buttonLabel}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
