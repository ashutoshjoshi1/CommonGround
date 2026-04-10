import type { NextConfig } from "next";

const internalApiBaseUrl =
  process.env.INTERNAL_API_BASE_URL ?? "http://localhost:8000";

const nextConfig: NextConfig = {
  transpilePackages: ["@commonground/ui", "@commonground/types"],
  typedRoutes: false,
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: `${internalApiBaseUrl}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
