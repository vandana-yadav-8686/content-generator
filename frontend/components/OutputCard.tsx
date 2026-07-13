"use client";

import { useState } from "react";
import { Check, Copy } from "lucide-react";
import { FORMAT_LABELS } from "@/lib/types";

interface Props {
  format: string;
  content: string;
  streaming?: boolean;
}

export default function OutputCard({ format, content, streaming }: Props) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    await navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <article className="panel overflow-hidden transition-shadow duration-200 hover:shadow-lift">
      <div className="flex items-center justify-between gap-3 border-b border-brand-900/5 bg-surface-sunken/50 px-5 py-3.5 sm:px-6">
        <h3 className="font-display text-sm font-semibold text-brand-800">
          {FORMAT_LABELS[format] || format}
          {streaming && (
            <span className="ml-2 inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-brand-500 align-middle" />
          )}
        </h3>
        <button
          onClick={handleCopy}
          disabled={streaming || !content}
          className="inline-flex items-center gap-1.5 rounded-lg border border-brand-900/10 bg-white px-2.5 py-1.5 text-xs font-medium text-ink-muted transition-colors hover:border-brand-300 hover:text-ink disabled:opacity-40"
        >
          {copied ? (
            <>
              <Check className="h-3.5 w-3.5 text-brand-600" />
              Copied
            </>
          ) : (
            <>
              <Copy className="h-3.5 w-3.5" />
              Copy
            </>
          )}
        </button>
      </div>
      <div className="p-5 sm:p-6">
        <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed text-ink/90">
          {content}
          {streaming && (
            <span className="ml-0.5 inline-block h-4 w-0.5 animate-pulse bg-brand-600 align-middle" />
          )}
        </pre>
      </div>
    </article>
  );
}
