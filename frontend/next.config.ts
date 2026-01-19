import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Vercel handles deployments automatically without 'export' mode
  images: {
    unoptimized: true,
  },
  trailingSlash: true,
};

export default nextConfig;
