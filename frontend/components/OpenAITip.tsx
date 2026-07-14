"use client";

import { Sparkles } from "lucide-react";
import Link from "next/link";

export default function OpenAITip() {
  return (
    <div className="flex items-start gap-3 rounded-2xl border border-sky-200/80 bg-gradient-to-r from-sky-50 to-white px-4 py-3.5 text-sm text-sky-950 shadow-soft">
      <Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-sky-600" />
      <div>
        <p className="font-semibold">Tip: Use OpenAI for best accuracy</p>
        <p className="mt-0.5 text-sky-800/90">
          GPT-4.1 or GPT-5 Mini in{" "}
          <Link href="/settings" className="font-medium underline underline-offset-2">
            Settings
          </Link>{" "}
          gives the most accurate, grounded repurposed content.
        </p>
      </div>
    </div>
  );
}
