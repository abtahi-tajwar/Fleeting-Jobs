export interface JobListing {
  title: string;
  url: string;
  matched_categories: string[];
}

export interface CompanyJobs {
  company_name: string;
  career_page_url: string;
  jobs: JobListing[];
  error?: string | null;
}

export interface JobDetails {
  title: string;
  url: string;
  company_name: string;
  career_page_url: string;
  matched_categories: string[];
  required_tech_skills: string[];
  required_soft_skills: string[];
  location?: string | null;
  experience_required?: string | null;
  error?: string | null;
}

export interface ScanProgress {
  status: string;
  message: string;
  current: number;
  total: number;
}

export interface ScanResult {
  status: string;
  companies: CompanyJobs[];
  jobs: JobDetails[];
  progress?: ScanProgress | null;
  error?: string | null;
}

export interface AppConfig {
  career_pages: { name?: string; url: string }[];
  categories: string[];
  parsers: string[];
}

export interface ScanStatusResponse {
  running: boolean;
  progress: ScanProgress;
  result: ScanResult | null;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${response.status}`);
  }

  return response.json();
}

export function getConfig() {
  return fetchJson<AppConfig>("/api/config");
}

export function getScanStatus() {
  return fetchJson<ScanStatusResponse>("/api/scan/status");
}

export function startScan() {
  return fetchJson<ScanResult>("/api/scan", { method: "POST" });
}

export function getResults() {
  return fetchJson<ScanResult | null>("/api/results");
}
