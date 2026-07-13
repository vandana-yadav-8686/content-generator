"use client";

import { BookOpen, Lightbulb, Target, Users } from "lucide-react";
import type { ContentBrief } from "@/lib/types";

interface Props {
  brief: ContentBrief;
}

export default function ExtractionPanel({ brief }: Props) {
  return (
    <div className="rounded-xl border border-emerald-200 bg-emerald-50/50 p-6 shadow-sm">
      <div className="flex items-center gap-2 mb-4">
        <BookOpen className="h-5 w-5 text-emerald-600" />
        <h2 className="text-lg font-semibold text-gray-900">Content Extraction</h2>
        <span className="ml-auto text-xs font-medium text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded-full">
          Step 1 complete
        </span>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-lg bg-white border border-emerald-100 p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-emerald-600 mb-1">Topic</p>
          <p className="text-sm text-gray-800">{brief.topic || "—"}</p>
        </div>
        <div className="rounded-lg bg-white border border-emerald-100 p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-emerald-600 mb-1 flex items-center gap-1">
            <Users className="h-3 w-3" /> Audience
          </p>
          <p className="text-sm text-gray-800">{brief.audience || "—"}</p>
        </div>
        <div className="rounded-lg bg-white border border-emerald-100 p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-emerald-600 mb-1 flex items-center gap-1">
            <Target className="h-3 w-3" /> Tone
          </p>
          <p className="text-sm text-gray-800 capitalize">{brief.tone || "—"}</p>
        </div>
        {brief.best_hook && (
          <div className="rounded-lg bg-white border border-emerald-100 p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-emerald-600 mb-1 flex items-center gap-1">
              <Lightbulb className="h-3 w-3" /> Best Hook
            </p>
            <p className="text-sm text-gray-800 italic">&ldquo;{brief.best_hook}&rdquo;</p>
          </div>
        )}
      </div>

      {brief.key_points.length > 0 && (
        <div className="mt-4 rounded-lg bg-white border border-emerald-100 p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-emerald-600 mb-2">Key Points</p>
          <ul className="space-y-1">
            {brief.key_points.map((point, i) => (
              <li key={i} className="text-sm text-gray-700 flex gap-2">
                <span className="text-emerald-500 font-bold">•</span>
                {point}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        {brief.facts.length > 0 && (
          <div className="rounded-lg bg-white border border-emerald-100 p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-emerald-600 mb-2">Facts</p>
            <ul className="space-y-1">
              {brief.facts.map((fact, i) => (
                <li key={i} className="text-sm text-gray-700">{fact}</li>
              ))}
            </ul>
          </div>
        )}
        {brief.examples.length > 0 && (
          <div className="rounded-lg bg-white border border-emerald-100 p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-emerald-600 mb-2">Examples</p>
            <ul className="space-y-1">
              {brief.examples.map((ex, i) => (
                <li key={i} className="text-sm text-gray-700">{ex}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
