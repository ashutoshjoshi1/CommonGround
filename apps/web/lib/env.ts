export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export const DEV_BANNER_ENABLED =
  (process.env.NEXT_PUBLIC_DEV_BANNER ?? "true") === "true";
