import type { Metadata } from "next";

import "./globals.css";
import { DevBanner } from "@/components/dev-banner";

export const metadata: Metadata = {
  title: "CommonGround",
  description:
    "Internal workspace for grounded knowledge, findings, and reviewable insights.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="font-sans text-ink antialiased">
        <DevBanner />
        {children}
      </body>
    </html>
  );
}
