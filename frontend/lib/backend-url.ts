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
