// Thin fetch wrapper for the FastAPI backend.
// In local dev, requests go to the same origin and Vite proxies /api -> :8000.
// In production (Vercel), set VITE_API_URL to the backend deployment URL,
// e.g. VITE_API_URL=https://applytrace-api-xxx.vercel.app
import type { AnalyzeResult, Application, Stats } from "./types";

const API_BASE = (import.meta.env.VITE_API_URL as string | undefined) ?? "";
const TOKEN_KEY = "applytrace_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}
export function setToken(t: string | null) {
  if (t) localStorage.setItem(TOKEN_KEY, t);
  else localStorage.removeItem(TOKEN_KEY);
}

async function req<T>(path: string, init?: RequestInit, raw401 = false): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}${path}`, { headers, ...init });
  if (res.status === 401) {
    if (raw401) {
      // Login/register failures: surface the server's real message.
      const body = (await res.json().catch(() => ({}))) as { detail?: string };
      throw new Error(body.detail ?? "Wrong email or password.");
    }
    setToken(null);
    if (!window.location.pathname.startsWith("/login")) window.location.href = "/login";
    throw new Error("Session expired — please sign in again.");
  }
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export interface DiscoveredJob {
  title: string;
  company: string;
  location: string;
  url: string;
  snippet: string;
  posted: string;
}

export const api = {
  listApplications: (status?: string) =>
    req<Application[]>(`/api/applications${status ? `?status=${status}` : ""}`),
  getApplication: (id: number) => req<Application>(`/api/applications/${id}`),
  createApplication: (payload: Partial<Application>) =>
    req<Application>("/api/applications", { method: "POST", body: JSON.stringify(payload) }),
  updateApplication: (id: number, payload: Partial<Application>) =>
    req<Application>(`/api/applications/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
  deleteApplication: (id: number) =>
    req<void>(`/api/applications/${id}`, { method: "DELETE" }),
  analyzeApplication: (id: number) =>
    req<AnalyzeResult>(`/api/analyze/application/${id}`, { method: "POST" }),
  stats: () => req<Stats>("/api/stats"),
  clearDemo: () => req<{ removed: number }>("/api/demo/clear", { method: "POST" }),
  gmailStatus: () => req<{ connected: boolean; email: string | null }>("/api/gmail/status"),
  gmailAuthUrl: () => req<{ url: string }>("/api/gmail/auth-url"),
  gmailSync: () =>
    req<{ added: number; skipped: number; companies: string[] }>("/api/gmail/sync", {
      method: "POST",
    }),
  login: (email: string, password: string) =>
    req<{ token: string; user: { id: number; email: string; name: string } }>(
      "/api/auth/login",
      { method: "POST", body: JSON.stringify({ email, password }) },
      true
    ),
  register: (email: string, password: string, name: string) =>
    req<{ token: string; user: { id: number; email: string; name: string } }>(
      "/api/auth/register",
      { method: "POST", body: JSON.stringify({ email, password, name }) },
      true
    ),
  fetchJd: (url: string) =>
    req<{ title: string; company: string; text: string }>("/api/jobs/fetch-jd", {
      method: "POST",
      body: JSON.stringify({ url }),
    }),
  discoverJobs: (query: string, location = "India") =>
    req<{ count: number; jobs: DiscoveredJob[] }>(
      `/api/jobs/discover?query=${encodeURIComponent(query)}&location=${encodeURIComponent(location)}`
    ),
};
