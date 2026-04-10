"use client";

import { ReactNode, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { getToken } from "@/lib/auth";

interface AuthGateProps {
  children: (token: string) => ReactNode;
}

export function AuthGate({ children }: AuthGateProps) {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const stored = getToken();
    if (!stored) {
      router.replace("/login");
      return;
    }
    setToken(stored);
  }, [router]);

  if (!token) {
    return <div className="p-8 text-sm text-zinc-600">Checking session…</div>;
  }

  return <>{children(token)}</>;
}
