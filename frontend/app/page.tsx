"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Check,
  Film,
  Instagram,
  Linkedin,
  Loader2,
  Mic,
  Settings,
  Wand2,
  Youtube,
} from "lucide-react";
import OutputCard from "@/components/OutputCard";
import { repurposeArticleStream } from "@/lib/api";
import {
  ALL_FORMATS,
  FORMAT_DESCRIPTIONS,
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

export default function HomePage() {
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
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
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
    if (allSelected) {
      clearSelection();
    } else {
      selectAll();
    }
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
      setError(e instanceof Error ? e.message : "Repurposing failed");
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
    <div className="space-y-8 sm:space-y-10">
      {/* Brand hero — one composition */}
      <header className="animate-fade-up max-w-2xl">
        <p className="step-label mb-3">
          <span className="step-num">AI</span>
          Content studio
        </p>
        <h1 className="font-display text-4xl font-semibold tracking-tight text-ink sm:text-5xl">
          Repurposer
        </h1>
        <p className="mt-3 text-base leading-relaxed text-ink-muted sm:text-lg">
          Pick formats, paste one article, then generate — only for what you need.
        </p>
      </header>

      {error && (
        <div
          role="alert"
          className="animate-fade-up rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800"
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
        <div className="flex items-center gap-3 rounded-2xl border border-brand-200 bg-brand-50/80 px-4 py-3.5 text-sm text-brand-900 shadow-soft">
          <Loader2 className="h-4 w-4 shrink-0 animate-spin text-brand-700" />
          <div className="min-w-0 flex-1">
            <p className="font-medium">
              {activeFormat
                ? `Writing ${FORMAT_LABELS[activeFormat]}…`
                : statusMessage || "Reading your article…"}
            </p>
            <div className="mt-2 h-1 overflow-hidden rounded-full bg-brand-200/80">
              <div className="h-full w-2/5 animate-pulse-line rounded-full bg-brand-600" />
            </div>
          </div>
        </div>
      )}

      {/* Step 1 — Formats */}
      <section className="animate-fade-up-delay">
        <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
          <div>
            <p className="step-label">
              <span className="step-num">1</span>
              Choose formats
            </p>
            <p className="mt-1.5 text-sm text-ink-muted">
              {noneSelected
                ? "Select at least one format to generate"
                : `${selectedList.length} of ${ALL_FORMATS.length} selected — fewer formats means fewer API calls`}
            </p>
          </div>
          <div className="inline-flex items-center rounded-xl border border-brand-900/10 bg-white p-1 shadow-soft">
            <button
              type="button"
              onClick={toggleSelectAll}
              disabled={loading}
              aria-pressed={allSelected}
              className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors disabled:opacity-50 ${
                allSelected
                  ? "bg-brand-700 text-white"
                  : "text-ink-muted hover:bg-brand-50 hover:text-brand-800"
              }`}
            >
              <span
                className={`flex h-4 w-4 items-center justify-center rounded border ${
                  allSelected
                    ? "border-white/40 bg-white/20 text-white"
                    : "border-brand-900/20 bg-white text-transparent"
                }`}
              >
                <Check className="h-2.5 w-2.5" strokeWidth={3} />
              </span>
              {allSelected ? "All selected" : "Select all"}
            </button>
            <button
              type="button"
              onClick={clearSelection}
              disabled={loading || noneSelected}
              className="rounded-lg px-3 py-1.5 text-xs font-medium text-ink-muted transition-colors hover:bg-surface-sunken hover:text-ink disabled:opacity-40"
            >
              Clear
            </button>
          </div>
        </div>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
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
                className={`group relative rounded-2xl border bg-white p-4 text-left transition-all duration-200 disabled:opacity-60 ${
                  selected
                    ? "border-brand-400 shadow-lift ring-2 ring-brand-500/20"
                    : "border-brand-900/10 shadow-soft hover:-translate-y-0.5 hover:border-brand-300 opacity-90"
                } ${activeFormat === id ? "ring-2 ring-brand-400" : ""}`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div
                    className={`inline-flex rounded-xl p-2.5 ring-1 ring-inset ${accent} transition-transform duration-200 group-hover:scale-105`}
                  >
                    <Icon className="h-4 w-4" />
                  </div>
                  <span
                    className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-md border transition-colors ${
                      selected
                        ? "border-brand-600 bg-brand-600 text-white"
                        : "border-brand-900/20 bg-white text-transparent"
                    }`}
                    aria-hidden
                  >
                    <Check className="h-3 w-3" strokeWidth={3} />
                  </span>
                </div>
                <p className="mt-3 font-display text-sm font-semibold text-ink">
                  {FORMAT_LABELS[id]}
                </p>
                <p className="mt-1 text-xs leading-snug text-ink-muted line-clamp-2">
                  {FORMAT_DESCRIPTIONS[id]}
                </p>
                {streaming && (
                  <p className="mt-3 flex items-center gap-1.5 text-xs font-medium text-brand-700">
                    <Loader2 className="h-3 w-3 animate-spin" />
                    Writing…
                  </p>
                )}
                {ready && (
                  <p className="mt-3 flex items-center gap-1 text-xs font-semibold text-brand-700">
                    <Check className="h-3 w-3" /> Ready
                  </p>
                )}
              </button>
            );
          })}
        </div>
      </section>

      {/* Step 2 — Article */}
      <section className="panel animate-fade-up-late overflow-hidden">
        <div className="border-b border-brand-900/5 px-5 py-4 sm:px-6">
          <p className="step-label">
            <span className="step-num">2</span>
            Paste your article
          </p>
        </div>
        <div className="p-5 sm:p-6">
          <textarea
            value={article}
            onChange={(e) => setArticle(e.target.value)}
            rows={11}
            placeholder="Paste a blog post, newsletter, or case study here…"
            className="field min-h-[220px] resize-y font-sans leading-relaxed"
            disabled={loading}
          />
          <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
            <p
              className={`text-xs ${
                article.trim().length >= 50 ? "text-brand-700" : "text-ink-soft"
              }`}
            >
              {article.length.toLocaleString()} characters
              {article.trim().length > 0 && article.trim().length < 50 && (
                <span className="text-amber-700"> · need {50 - article.trim().length} more</span>
              )}
            </p>
            <label className="flex items-center gap-2 text-sm text-ink-muted">
              Tone
              <select
                value={tone}
                onChange={(e) => setTone(e.target.value as ToneId)}
                disabled={loading}
                className="rounded-lg border border-brand-900/10 bg-white px-2.5 py-1.5 text-sm text-ink focus:border-brand-500 focus:outline-none"
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

      {/* Step 3 — Generate bar */}
      <section className="panel sticky bottom-4 z-20 overflow-hidden sm:bottom-6">
        <div className="flex flex-col gap-4 p-4 sm:flex-row sm:items-center sm:justify-between sm:px-6 sm:py-4">
          <div className="min-w-0">
            <p className="step-label mb-1">
              <span className="step-num">3</span>
              Generate
            </p>
            <p className="truncate text-sm text-ink-muted">
              {allSelected
                ? "All five formats · more API usage"
                : `${selectedList.map((f) => FORMAT_LABELS[f]).join(" · ")}`}
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2 sm:gap-3">
            <Link href="/settings" className="btn-ghost">
              <Settings className="h-3.5 w-3.5" />
              LLM
            </Link>
            <button
              onClick={handleRepurpose}
              disabled={!canGenerate}
              className="btn-primary min-w-[160px]"
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
      </section>

      {meta && (
        <p className="text-center text-xs text-ink-soft">
          Generated {outputs.filter((o) => o.content).length}/{selectedList.length} with{" "}
          <span className="font-medium text-ink-muted">{meta.provider}</span> · {meta.model} ·{" "}
          <span className="capitalize">{tone}</span>
        </p>
      )}

      {outputs.length > 0 && (
        <section className="space-y-4 pt-2">
          <div className="flex items-end justify-between gap-3">
            <h2 className="font-display text-2xl font-semibold tracking-tight text-ink">
              Your content
            </h2>
            <p className="text-xs text-ink-soft">Copy any format below</p>
          </div>
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
  );
}
