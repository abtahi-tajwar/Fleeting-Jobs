"use client";

import { useEffect, useState } from "react";
import { JobCard } from "@/components/JobCard";
import { useScan } from "@/context/ScanContext";
import { AppConfig, getConfig, getResults } from "@/lib/api";

export default function JobsPage() {
  const { scanning, error, result, progressMessage } = useScan();
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [loadedResult, setLoadedResult] = useState<typeof result>(null);

  useEffect(() => {
    getConfig().then(setConfig).catch(() => undefined);
    getResults().then(setLoadedResult).catch(() => undefined);
  }, []);

  const activeResult = result ?? loadedResult;
  const jobs = activeResult?.jobs ?? [];

  return (
    <div className="page">
      <div className="page-header">
        <h1>Jobs</h1>
        <p className="page-subtitle">
          Matched job postings from configured companies and parsers.
        </p>
      </div>

      {config && (
        <div className="stats">
          <div className="stat">
            <strong>{config.company_count}</strong>
            companies
          </div>
          <div className="stat">
            <strong>{config.parser_count}</strong>
            parsers
          </div>
          <div className="stat">
            <strong>{config.categories.length}</strong>
            categories
          </div>
        </div>
      )}

      {progressMessage && <p className="status">{progressMessage}</p>}
      {scanning && (
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: "100%" }} />
        </div>
      )}
      {error && <div className="error-banner">{error}</div>}

      <section>
        <h2 className="section-title">
          Results {jobs.length > 0 && `(${jobs.length})`}
        </h2>

        {jobs.length === 0 && !scanning && (
          <div className="empty-state panel">
            No results yet. Add companies and parsers, then click Scan jobs in
            the top bar.
          </div>
        )}

        {jobs.map((job) => (
          <JobCard key={job.url} job={job} />
        ))}
      </section>
    </div>
  );
}
