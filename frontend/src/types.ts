// Shared types mirroring the FastAPI schemas.
export interface Application {
  id: number;
  company: string;
  role: string;
  location: string;
  status: string;
  applied_date: string;
  jd_text: string;
  resume_text: string;
  link: string;
  notes: string;
  match_score: number | null;
}

export interface AnalyzeResult {
  score: number;
  matched_keywords: string[];
  missing_keywords: string[];
  suggested_tweaks: string[];
}

export interface Stats {
  total: number;
  wishlist: number;
  applied: number;
  interviewing: number;
  offered: number;
  rejected: number;
}

export const STATUSES = ["wishlist", "applied", "interviewing", "offered", "rejected"] as const;
