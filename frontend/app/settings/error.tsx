"use client";

import Link from "next/link";
import { useEffect } from "react";

export default function SettingsError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="rounded-xl border border-red-200 bg-red-50 p-6">
      <h2 className="text-lg font-semibold text-red-800">Settings failed to load</h2>
      <p className="mt-2 text-sm text-red-700">{error.message}</p>
      <p className="mt-2 text-xs text-red-600">
        Make sure the backend is running on port 8000.
      </p>
      <div className="mt-4 flex gap-3">
        <button
          onClick={reset}
          className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
        >
          Retry
        </button>
        <Link
          href="/"
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Back to Repurpose
        </Link>
      </div>
    </div>
  );
}
