import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["@commonground/ui", "@commonground/types"],
  typedRoutes: false,
};

export default nextConfig;
