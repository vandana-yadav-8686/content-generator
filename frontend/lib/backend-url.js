/** Production Render API — used when NODE_ENV/VERCEL_ENV is production. */
const PRODUCTION_BACKEND_URL = "https://content-generator-wv8n.onrender.com";
const LOCAL_BACKEND_URL = "http://localhost:8000";

/**
 * Resolve backend URL:
 * 1. BACKEND_URL env (explicit override)
 * 2. Production URL on Vercel/production builds
 * 3. localhost for local dev
 */
function getBackendUrl() {
  const fromEnv = process.env.BACKEND_URL?.replace(/\/$/, "");
  if (fromEnv) return fromEnv;

  const isProduction =
    process.env.NODE_ENV === "production" ||
    process.env.VERCEL_ENV === "production";

  return isProduction ? PRODUCTION_BACKEND_URL : LOCAL_BACKEND_URL;
}

module.exports = {
  getBackendUrl,
  PRODUCTION_BACKEND_URL,
  LOCAL_BACKEND_URL,
};
