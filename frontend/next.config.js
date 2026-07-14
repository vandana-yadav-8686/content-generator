/** @type {import('next').NextConfig} */
const {
  getBackendUrl,
  PRODUCTION_BACKEND_URL,
  LOCAL_BACKEND_URL,
} = require("./lib/backend-url.js");

const backendUrl = getBackendUrl();
const isProduction =
  process.env.NODE_ENV === "production" ||
  process.env.VERCEL_ENV === "production";

const nextConfig = {
  env: {
    NEXT_PUBLIC_BACKEND_URL: backendUrl,
    NEXT_PUBLIC_VERCEL_ENV: process.env.VERCEL_ENV || "",
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
