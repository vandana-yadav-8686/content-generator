import { NextRequest } from "next/server";
import { getBackendUrl } from "@/lib/backend-url.js";

const BACKEND_URL = getBackendUrl();

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

/** Proxy SSE from FastAPI without buffering (next.config rewrites buffer streams). */
export async function POST(request: NextRequest) {
  const body = await request.text();

  const backendRes = await fetch(`${BACKEND_URL}/api/repurpose/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
    cache: "no-store",
  });

  if (!backendRes.ok) {
    const err = await backendRes.json().catch(() => ({
      detail: backendRes.statusText || "Stream request failed",
    }));
    return Response.json(err, { status: backendRes.status });
  }

  if (!backendRes.body) {
    return Response.json({ detail: "No response body" }, { status: 502 });
  }

  return new Response(backendRes.body, {
    status: 200,
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
      "X-Accel-Buffering": "no",
    },
  });
}
