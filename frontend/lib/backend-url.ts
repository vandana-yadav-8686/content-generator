/** Production Render API — used when NODE_ENV/VERCEL_ENV is production. */
export const PRODUCTION_BACKEND_URL =
  "https://content-generator-wv8n.onrender.com";
export const LOCAL_BACKEND_URL = "http://localhost:8000";

export function getBackendUrl(): string {
  const fromEnv = process.env.BACKEND_URL?.replace(/\/$/, "");
  if (fromEnv) return fromEnv;

  const isProduction =
    process.env.NODE_ENV === "production" ||
    process.env.VERCEL_ENV === "production";

  return isProduction ? PRODUCTION_BACKEND_URL : LOCAL_BACKEND_URL;
}

/** Client-safe URL baked at build time via next.config.js */
export function getPublicBackendUrl(): string {
  const fromPublic = process.env.NEXT_PUBLIC_BACKEND_URL?.replace(/\/$/, "");
  if (fromPublic) return fromPublic;
  return LOCAL_BACKEND_URL;
}

/**
 * Stream endpoint — production browser calls Render directly (Vercel times out on long SSE).
 * Local dev uses Next.js proxy route.
 */
export function getStreamEndpoint(): string {
  const isBrowser = typeof window !== "undefined";
  const isProduction =
    process.env.NODE_ENV === "production" ||
    process.env.NEXT_PUBLIC_VERCEL_ENV === "production" ||
    process.env.VERCEL_ENV === "production";

  if (isBrowser && isProduction) {
    return `${getPublicBackendUrl()}/api/repurpose/stream`;
  }
  return "/api/repurpose/stream";
}
