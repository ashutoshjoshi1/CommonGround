import { API_BASE_URL } from "@/lib/env";

export class ApiError extends Error {
  status: number;
  payload: unknown;

  constructor(message: string, status: number, payload: unknown) {
    super(message);
    this.status = status;
    this.payload = payload;
  }
}

export async function apiFetch<T>(
  path: string,
  options?: RequestInit,
  token?: string | null,
): Promise<T> {
  const headers = new Headers(options?.headers);
  headers.set("Content-Type", "application/json");
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers,
    });
  } catch (error) {
    throw new ApiError(
      `Unable to reach the API (${API_BASE_URL}). Make sure the API service is running.`,
      0,
      error,
    );
  }

  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const message =
      (typeof payload === "object" && payload && "detail" in payload
        ? String((payload as { detail: unknown }).detail)
        : response.statusText) || "Request failed";
    throw new ApiError(message, response.status, payload);
  }

  return payload as T;
}

export async function uploadFile<T>(
  workspaceId: string,
  file: File,
  token: string,
): Promise<T> {
  const form = new FormData();
  form.append("file", file);

  let response: Response;
  try {
    response = await fetch(
      `${API_BASE_URL}/sources/upload?workspace_id=${encodeURIComponent(workspaceId)}`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: form,
      },
    );
  } catch (error) {
    throw new ApiError(
      `Unable to reach the API (${API_BASE_URL}). Make sure the API service is running.`,
      0,
      error,
    );
  }

  const payload = await response.json();
  if (!response.ok) {
    throw new ApiError(
      String(payload?.detail ?? "Upload failed"),
      response.status,
      payload,
    );
  }
  return payload as T;
}
