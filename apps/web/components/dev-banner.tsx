"use client";

import { DEV_BANNER_ENABLED } from "@/lib/env";

export function DevBanner() {
  if (!DEV_BANNER_ENABLED) return null;

  return (
    <div className="border-b border-amber-300 bg-amber-50 px-4 py-2 text-center text-xs text-amber-800">
      Development environment. Data and outputs are for non-production use.
    </div>
  );
}
