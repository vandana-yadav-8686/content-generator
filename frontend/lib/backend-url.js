/** Production Render API — used when NODE_ENV/VERCEL_ENV is production. */
const PRODUCTION_BACKEND_URL = "https://content-generator-wv8n.onrender.com";
const LOCAL_BACKEND_URL = "http://localhost:8000";

function getBackendUrl() {
  const fromEnv = process.env.BACKEND_URL?.replace(/\/$/, "");
  if (fromEnv) return fromEnv;

  const isProduction =
    process.env.NODE_ENV === "production" ||
    process.env.VERCEL_ENV === "production";

  return isProduction ? PRODUCTION_BACKEND_URL : LOCAL_BACKEND_URL;
}

function getPublicBackendUrl() {
  const fromPublic = process.env.NEXT_PUBLIC_BACKEND_URL?.replace(/\/$/, "");
  if (fromPublic) return fromPublic;

  const isProduction =
    process.env.NODE_ENV === "production" ||
    process.env.NEXT_PUBLIC_VERCEL_ENV === "production" ||
    process.env.VERCEL_ENV === "production";

  return isProduction ? PRODUCTION_BACKEND_URL : LOCAL_BACKEND_URL;
}

/** Browser API base — production calls Render directly (Vercel proxy breaks save/test). */
function getApiBase() {
  const isBrowser = typeof window !== "undefined";
  const isProduction =
    process.env.NODE_ENV === "production" ||
    process.env.NEXT_PUBLIC_VERCEL_ENV === "production" ||
    process.env.VERCEL_ENV === "production";

  if (isBrowser && isProduction) {
    return `${getPublicBackendUrl()}/api`;
  }
  return "/api";
}

/** Production browser streams directly to Render (Vercel proxy times out). */
function getStreamEndpoint() {
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

module.exports = {
  getBackendUrl,
  getPublicBackendUrl,
  getApiBase,
  getStreamEndpoint,
  PRODUCTION_BACKEND_URL,
  LOCAL_BACKEND_URL,
};
