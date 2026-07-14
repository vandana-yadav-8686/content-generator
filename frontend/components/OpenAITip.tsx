"use client";

import { Sparkles } from "lucide-react";
import Link from "next/link";

export default function OpenAITip() {
  return (
    <div className="flex items-center gap-2.5 rounded-xl border border-sky-200/70 bg-sky-50/80 px-3 py-2 text-xs text-sky-950 dark:border-sky-800/50 dark:bg-sky-950/40 dark:text-sky-100">
      <Sparkles className="h-3.5 w-3.5 shrink-0 text-sky-600 dark:text-sky-400" />
      <p>
        <span className="font-semibold">Tip:</span> Use GPT-4.1 or GPT-5 Mini in{" "}
        <Link href="/settings" className="font-medium underline underline-offset-2">
          Settings
        </Link>{" "}
        for best accuracy.
      </p>
    </div>
  );
}
