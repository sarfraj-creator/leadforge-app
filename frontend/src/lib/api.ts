/**
 * Universal API fetcher for LeadForge frontend.
 *
 * Resolves the backend base URL automatically:
 * - If NEXT_PUBLIC_API_URL is set, requests go to that absolute URL + /api.
 * - Otherwise, requests use a relative "/api" path, which works out of the box
 *   on Vercel because vercel.json routes /api/* to the FastAPI backend on the
 *   same domain, and works locally when the Next.js dev server proxies to
 *   http://localhost:8000 (see next.config.js rewrites, if configured) or when
 *   both servers are reachable via relative paths behind a shared origin.
 */

const RAW_BASE = process.env.NEXT_PUBLIC_API_URL?.trim();

// Normalize: strip any trailing slash so we don't end up with "//api"
const API_ROOT = RAW_BASE ? RAW_BASE.replace(/\/+$/, "") : "";

function buildUrl(path: string): string {
  const cleanPath = path.startsWith("/") ? path : `/${path}`;
  // Avoid double-prefixing if a caller already included /api
  const withApiPrefix = cleanPath.startsWith("/api")
    ? cleanPath
    : `/api${cleanPath}`;
  return `${API_ROOT}${withApiPrefix}`;
}

export class ApiError extends Error {
  status: number;
  body: unknown;

  constructor(message: string, status: number, body: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

export async function apiFetch<T = any>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = buildUrl(path);

  const headers: HeadersInit = {
    ...(options.body ? { "Content-Type": "application/json" } : {}),
    ...(options.headers || {}),
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  // Try to parse JSON regardless of status, since FastAPI error responses
  // are also JSON (e.g. { "detail": "..." })
  let data: unknown = null;
  const text = await response.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }

  if (!response.ok) {
    const message =
      (data as { detail?: string })?.detail ||
      (data as { message?: string })?.message ||
      `Request failed with status ${response.status}`;
    throw new ApiError(message, response.status, data);
  }

  return data as T;
}