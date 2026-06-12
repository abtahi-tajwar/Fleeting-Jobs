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
  categories: string[];
  company_count: number;
  parser_count: number;
}

export interface Company {
  id: number;
  name: string;
  slug: string;
  listing_url: string;
  single_post_url_format: string;
  has_parser: boolean;
}

export interface CompanyParser {
  id: number;
  company_id: number;
  listing_page: Record<string, unknown>;
  company_page: Record<string, unknown>;
  company_name?: string | null;
}

export interface CreateCompanyPayload {
  name: string;
  listing_url: string;
  single_post_url_format: string;
}

export interface CreateParserPayload {
  company_id: number;
  listing_page: Record<string, unknown>;
  company_page: Record<string, unknown>;
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
    const detail = body.detail;
    const message =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map((item: { msg?: string }) => item.msg).join(", ")
          : `Request failed: ${response.status}`;
    throw new Error(message);
  }

  return response.json();
}

export function getConfig() {
  return fetchJson<AppConfig>("/api/config");
}

export function getCompanies() {
  return fetchJson<Company[]>("/api/companies");
}

export function createCompany(payload: CreateCompanyPayload) {
  return fetchJson<Company>("/api/companies", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getParsers() {
  return fetchJson<CompanyParser[]>("/api/parsers");
}

export function createParser(payload: CreateParserPayload) {
  return fetchJson<CompanyParser>("/api/parsers", {
    method: "POST",
    body: JSON.stringify(payload),
  });
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
