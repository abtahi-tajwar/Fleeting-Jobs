"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  Company,
  CompanyParser,
  createParser,
  getCompanies,
  getParsers,
} from "@/lib/api";

const LISTING_PAGE_TEMPLATE = `{
  "job_links": {
    "selector": "a",
    "href_contains": "/job/"
  }
}`;

const COMPANY_PAGE_TEMPLATE = `{
  "fields": {
    "title": ["h1", ".job-title"],
    "description": [".job-description", "main"]
  }
}`;

export default function ParsersPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [parsers, setParsers] = useState<CompanyParser[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [companyId, setCompanyId] = useState("");
  const [listingPageJson, setListingPageJson] = useState(LISTING_PAGE_TEMPLATE);
  const [companyPageJson, setCompanyPageJson] = useState(COMPANY_PAGE_TEMPLATE);

  const loadData = () => {
    setLoading(true);
    Promise.all([getCompanies(), getParsers()])
      .then(([companyRows, parserRows]) => {
        setCompanies(companyRows);
        setParsers(parserRows);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  const filteredCompanies = useMemo(() => {
    const query = search.trim().toLowerCase();
    if (!query) return companies;
    return companies.filter(
      (company) =>
        company.name.toLowerCase().includes(query) ||
        company.slug.toLowerCase().includes(query),
    );
  }, [companies, search]);

  const availableCompanies = filteredCompanies.filter((company) => !company.has_parser);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    setSuccess(null);

    try {
      const listing_page = JSON.parse(listingPageJson);
      const company_page = JSON.parse(companyPageJson);

      await createParser({
        company_id: Number(companyId),
        listing_page,
        company_page,
      });

      setCompanyId("");
      setListingPageJson(LISTING_PAGE_TEMPLATE);
      setCompanyPageJson(COMPANY_PAGE_TEMPLATE);
      setSuccess("Parser added successfully.");
      loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add parser");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Parsers</h1>
        <p className="page-subtitle">
          Attach CSS selector configs to a company for listing and job pages.
        </p>
      </div>

      <section className="panel">
        <h2>Add parser</h2>
        <form className="form" onSubmit={handleSubmit}>
          <label className="form-field">
            <span>Search company</span>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Type to filter companies…"
            />
          </label>

          <label className="form-field">
            <span>Company</span>
            <select
              value={companyId}
              onChange={(e) => setCompanyId(e.target.value)}
              required
            >
              <option value="">Select a company…</option>
              {availableCompanies.map((company) => (
                <option key={company.id} value={company.id}>
                  {company.name}
                </option>
              ))}
            </select>
          </label>

          <label className="form-field">
            <span>Listing page JSON</span>
            <textarea
              value={listingPageJson}
              onChange={(e) => setListingPageJson(e.target.value)}
              rows={8}
              className="code-input"
              required
            />
          </label>

          <label className="form-field">
            <span>Company page JSON</span>
            <textarea
              value={companyPageJson}
              onChange={(e) => setCompanyPageJson(e.target.value)}
              rows={10}
              className="code-input"
              required
            />
          </label>

          <button className="btn" type="submit" disabled={submitting}>
            {submitting ? "Saving…" : "Add parser"}
          </button>
        </form>
        {success && <p className="status success">{success}</p>}
        {error && <p className="status error">{error}</p>}
      </section>

      <section className="panel">
        <h2>Configured parsers</h2>
        {loading ? (
          <p className="status">Loading…</p>
        ) : parsers.length === 0 ? (
          <p className="status">No parsers yet.</p>
        ) : (
          <div className="parser-list">
            {parsers.map((parser) => (
              <div key={parser.id} className="parser-card">
                <h3>{parser.company_name ?? `Company #${parser.company_id}`}</h3>
                <div className="parser-json-block">
                  <div className="section-label">Listing page</div>
                  <pre>{JSON.stringify(parser.listing_page, null, 2)}</pre>
                </div>
                <div className="parser-json-block">
                  <div className="section-label">Company page</div>
                  <pre>{JSON.stringify(parser.company_page, null, 2)}</pre>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
