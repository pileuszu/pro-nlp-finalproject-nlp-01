import type { NextConfig } from "next";

const isGha = !!process.env.GITHUB_ACTIONS;

const nextConfig: NextConfig = {
  output: isGha ? 'export' : undefined,
  basePath: isGha ? '/pro-nlp-finalproject-nlp-01' : '',
  images: {
    unoptimized: true,
  },
  trailingSlash: true,
};

export default nextConfig;
