/**
 * Client-side JWT session storage. Kept dependency-free so the HTTP layer can
 * read the token without importing React.
 */
import type { AuthSession, AuthUser } from "@/services/types";

const TOKEN_KEY = "ds.auth.token";
const USER_KEY = "ds.auth.user";

const listeners = new Set<() => void>();

function isBrowser() {
  return typeof window !== "undefined";
}

export function getToken(): string | null {
  if (!isBrowser()) return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

let cachedRaw: string | null = null;
let cachedUser: AuthUser | null = null;

/** Returns a stable reference so React's useSyncExternalStore stays happy. */
export function getUser(): AuthUser | null {
  if (!isBrowser()) return null;
  const raw = window.localStorage.getItem(USER_KEY);
  if (raw === cachedRaw) return cachedUser;
  cachedRaw = raw;
  if (!raw) {
    cachedUser = null;
    return null;
  }
  try {
    cachedUser = JSON.parse(raw) as AuthUser;
  } catch {
    cachedUser = null;
  }
  return cachedUser;
}

export function setSession(session: AuthSession) {
  if (!isBrowser()) return;
  window.localStorage.setItem(TOKEN_KEY, session.token);
  window.localStorage.setItem(USER_KEY, JSON.stringify(session.user));
  emit();
}

export function clearSession() {
  if (!isBrowser()) return;
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(USER_KEY);
  emit();
}

export function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

function emit() {
  listeners.forEach((listener) => listener());
}
