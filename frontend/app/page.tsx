"use client";

import { useCallback, useEffect, useState } from "react";
import {
  AppConfig,
  JobDetails,
  ScanResult,
  getConfig,
  startScan,
} from "@/lib/api";

function SkillChips({
  label,
  items,
  variant,
}: {
  label: string;
  items: string[];
  variant: "tech" | "soft" | "muted";
}) {
  if (!items.length) return null;
  return (
    <div>
      <div className="section-label">{label}</div>
      <div className="chip-list">
        {items.map((item) => (
          <span key={item} className={`chip ${variant}`}>
            {item}
          </span>
        ))}
      </div>
    </div>
  );
}

function JobCard({ job }: { job: JobDetails }) {
  return (
    <article className="job-card">
      <h3>{job.title}</h3>
      <div className="job-meta">
        <span>{job.company_name}</span>
        {job.location && <span>{job.location}</span>}
        {job.experience_required && <span>{job.experience_required}</span>}
      </div>

      {job.matched_categories.length > 0 && (
        <div>
          <div className="section-label">Matched categories</div>
          <div className="chip-list">
            {job.matched_categories.map((cat) => (
              <span key={cat} className="chip">
                {cat}
              </span>
            ))}
          </div>
        </div>
      )}

      <SkillChips
        label="Tech skills"
        items={job.required_tech_skills}
        variant="tech"
      />
      <SkillChips
        label="Soft skills"
        items={job.required_soft_skills}
        variant="soft"
      />

      <div style={{ marginTop: "1rem" }}>
        <a href={job.url} target="_blank" rel="noopener noreferrer">
          View original posting →
        </a>
      </div>

      {job.error && <p className="status error" style={{ marginTop: "0.5rem" }}>{job.error}</p>}
    </article>
  );
}

export default function HomePage() {
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progressMessage, setProgressMessage] = useState("");

  useEffect(() => {
    getConfig()
      .then(setConfig)
      .catch((err) => setError(err.message));
  }, []);

  const handleScan = useCallback(async () => {
    setLoading(true);
    setError(null);
    setProgressMessage("Starting scan… this may take several minutes.");
    setResult(null);

    try {
      const scanResult = await startScan();
      setResult(scanResult);
      setProgressMessage("Scan completed.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Scan failed");
      setProgressMessage("");
    } finally {
      setLoading(false);
    }
  }, []);

  const jobs = result?.jobs ?? [];

  return (
    <main className="container">
      <header className="header">
        <h1>Fleeting Jobs</h1>
        <p>
          Scrapes career pages with a headless browser, parses job listings with
          company-specific CSS selectors, filters by category with ChatGPT, and
          extracts skills, location, and experience from each job description.
        </p>
      </header>

      <section className="panel">
        <h2>Configuration</h2>
        {config ? (
          <>
            <div className="stats">
              <div className="stat">
                <strong>{config.career_pages.length}</strong>
                career pages
              </div>
              <div className="stat">
                <strong>{config.categories.length}</strong>
                target categories
              </div>
              <div className="stat">
                <strong>{config.parsers?.length ?? 0}</strong>
                company parsers
              </div>
            </div>
            <ul className="config-list">
              {config.career_pages.map((page) => (
                <li key={page.url}>
                  <strong>{page.name || page.url}</strong> —{" "}
                  <a href={page.url} target="_blank" rel="noopener noreferrer">
                    {page.url}
                  </a>
                </li>
              ))}
            </ul>
            <div className="section-label" style={{ marginTop: "1rem" }}>
              Categories
            </div>
            <div className="chip-list">
              {config.categories.map((cat) => (
                <span key={cat} className="chip muted">
                  {cat}
                </span>
              ))}
            </div>
          </>
        ) : (
          <p className="status">Loading configuration…</p>
        )}
      </section>

      <section className="panel">
        <h2>Run scan</h2>
        <div className="actions">
          <button className="btn" onClick={handleScan} disabled={loading}>
            {loading ? "Scanning…" : "Start job scan"}
          </button>
          {progressMessage && <span className="status">{progressMessage}</span>}
        </div>
        {loading && (
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: "100%" }} />
          </div>
        )}
      </section>

      {error && <div className="error-banner">{error}</div>}

      <section>
        <h2 style={{ marginBottom: "1rem" }}>
          Results {jobs.length > 0 && `(${jobs.length} jobs)`}
        </h2>

        {jobs.length === 0 && !loading && (
          <div className="empty-state panel">
            No results yet. Start a scan to discover matching jobs from your
            configured career pages.
          </div>
        )}

        {jobs.map((job) => (
          <JobCard key={job.url} job={job} />
        ))}
      </section>
    </main>
  );
}
