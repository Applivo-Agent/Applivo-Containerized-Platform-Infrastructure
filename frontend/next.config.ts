import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  typescript: {
    // Only ignore build errors in production; catch them during local dev
    ignoreBuildErrors: process.env.NODE_ENV === "production",
  },
  // Allow connecting to local backend without HTTPS in dev
  async rewrites() {
    return process.env.NODE_ENV === "development"
      ? [
          {
            source: "/api/:path*",
            destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/:path*`,
          },
        ]
      : [];
  },
} as NextConfig;

export default nextConfig;
