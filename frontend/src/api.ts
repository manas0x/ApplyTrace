// Thin fetch wrapper for the FastAPI backend (proxied through Vite in dev).
import type { AnalyzeResult, Application, Stats } from "./types";

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
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
  seed: () => req<{ seeded: number; message: string }>("/api/seed", { method: "POST" }),
};
