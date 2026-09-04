/**
 * Centralised HTTP client.
 *
 * - Configurable BASE_URL via VITE_API_BASE_URL
 * - Request "interceptor" attaches the JWT bearer token
 * - Response "interceptor" normalises errors, fires a toast, and signs the
 *   user out + redirects to /login on 401
 * - When VITE_USE_MOCK_API is not "false", requests are served by the mock
 *   adapter in ./mock using the SAME endpoint paths as the real backend.
 */
import { toast } from "sonner";

import { clearSession, getToken } from "@/lib/auth-storage";
import { handleMockRequest } from "@/services/mock";

export const API_BASE_URL: string =
  import.meta.env["VITE_API_BASE_URL"] ?? "http://localhost:8000";

export const USE_MOCK_API: boolean =
  import.meta.env["VITE_USE_MOCK_API"] !== "false";

export class ApiError extends Error {
  status: number;
  details?: unknown;

  constructor(message: string, status: number, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

export interface RequestOptions {
  method?: "GET" | "POST" | "PATCH" | "PUT" | "DELETE";
  body?: unknown;
  query?: Record<string, string | number | boolean | undefined>;
  /** Set false for auth endpoints that must not send a stale token. */
  auth?: boolean;
  /** Suppress the automatic error toast (e.g. form-level error display). */
  silent?: boolean;
  signal?: AbortSignal;
  timeoutMs?: number;
}

function buildPath(path: string, query?: RequestOptions["query"]): string {
  if (!query) return path;
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value !== undefined && value !== "") params.set(key, String(value));
  }
  const qs = params.toString();
  return qs ? `${path}?${qs}` : path;
}

/** Response interceptor: normalise + surface failures once, in one place. */
function onError(error: ApiError, silent?: boolean): never {
  if (error.status === 401) {
    clearSession();
    if (typeof window !== "undefined" && !window.location.pathname.startsWith("/login")) {
      toast.error("Session expired", { description: "Please sign in again." });
      window.location.assign("/login");
    }
    throw error;
  }
  if (!silent) {
    toast.error("Request failed", { description: error.message });
  }
  throw error;
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const {
    method = "GET",
    body,
    query,
    auth = true,
    silent,
    signal,
    timeoutMs = 20_000,
  } = options;

  const fullPath = buildPath(path, query);

  try {
    if (USE_MOCK_API) {
      return (await handleMockRequest(method, fullPath, body)) as T;
    }

    // Request interceptor
    const headers: Record<string, string> = { Accept: "application/json" };
    if (body !== undefined) headers["Content-Type"] = "application/json";
    const token = auth ? getToken() : null;
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), timeoutMs);
    signal?.addEventListener("abort", () => controller.abort());

    let response: Response;
    try {
      response = await fetch(`${API_BASE_URL}${fullPath}`, {
        method,
        headers,
        ...(body === undefined ? {} : { body: JSON.stringify(body) }),
        signal: controller.signal,
      });
    } finally {
      clearTimeout(timeout);
    }

    const text = await response.text();
    const payload = text ? safeJson(text) : null;

    if (!response.ok) {
      const message =
        (payload as { message?: string; detail?: string } | null)?.message ??
        (payload as { detail?: string } | null)?.detail ??
        `${response.status} ${response.statusText}`;
      throw new ApiError(message, response.status, payload);
    }

    return payload as T;
  } catch (error) {
    if (error instanceof ApiError) return onError(error, silent);
    const message =
      error instanceof DOMException && error.name === "AbortError"
        ? "The request timed out."
        : error instanceof Error
          ? error.message
          : "Unexpected network error.";
    return onError(new ApiError(message, 0), silent);
  }
}

function safeJson(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export const http = {
  get: <T>(path: string, options?: Omit<RequestOptions, "method" | "body">) =>
    request<T>(path, { ...options, method: "GET" }),
  post: <T>(path: string, body?: unknown, options?: Omit<RequestOptions, "method" | "body">) =>
    request<T>(path, { ...options, method: "POST", body }),
  patch: <T>(path: string, body?: unknown, options?: Omit<RequestOptions, "method" | "body">) =>
    request<T>(path, { ...options, method: "PATCH", body }),
  delete: <T>(path: string, options?: Omit<RequestOptions, "method" | "body">) =>
    request<T>(path, { ...options, method: "DELETE" }),
};
