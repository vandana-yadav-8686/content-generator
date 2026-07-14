/** @type {import('next').NextConfig} */
const { getBackendUrl } = require("./lib/backend-url.js");

const backendUrl = getBackendUrl();

const nextConfig = {
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
