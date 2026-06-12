"use client";

import { FormEvent, useEffect, useState } from "react";
import { Company, createCompany, getCompanies } from "@/lib/api";

export default function CompaniesPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [name, setName] = useState("");
  const [listingUrl, setListingUrl] = useState("");
  const [singlePostUrlFormat, setSinglePostUrlFormat] = useState("");

  const loadCompanies = () => {
    setLoading(true);
    getCompanies()
      .then(setCompanies)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadCompanies();
  }, []);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    setSuccess(null);

    try {
      await createCompany({
        name,
        listing_url: listingUrl,
        single_post_url_format: singlePostUrlFormat,
      });
      setName("");
      setListingUrl("");
      setSinglePostUrlFormat("");
      setSuccess("Company added successfully.");
      loadCompanies();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add company");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Companies</h1>
        <p className="page-subtitle">
          Add companies with their listing URL and single job post URL format.
        </p>
      </div>

      <section className="panel">
        <h2>Add company</h2>
        <form className="form" onSubmit={handleSubmit}>
          <label className="form-field">
            <span>Company name</span>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="RBC"
              required
            />
          </label>
          <label className="form-field">
            <span>Listing URL</span>
            <input
              type="url"
              value={listingUrl}
              onChange={(e) => setListingUrl(e.target.value)}
              placeholder="https://jobs.example.com/careers"
              required
            />
          </label>
          <label className="form-field">
            <span>Single post URL format</span>
            <input
              type="text"
              value={singlePostUrlFormat}
              onChange={(e) => setSinglePostUrlFormat(e.target.value)}
              placeholder="https://jobs.example.com/job/{id}"
              required
            />
          </label>
          <button className="btn" type="submit" disabled={submitting}>
            {submitting ? "Saving…" : "Add company"}
          </button>
        </form>
        {success && <p className="status success">{success}</p>}
        {error && <p className="status error">{error}</p>}
      </section>

      <section className="panel">
        <h2>All companies</h2>
        {loading ? (
          <p className="status">Loading…</p>
        ) : companies.length === 0 ? (
          <p className="status">No companies yet.</p>
        ) : (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Slug</th>
                  <th>Listing URL</th>
                  <th>Parser</th>
                </tr>
              </thead>
              <tbody>
                {companies.map((company) => (
                  <tr key={company.id}>
                    <td>{company.name}</td>
                    <td>{company.slug}</td>
                    <td>
                      <a
                        href={company.listing_url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {company.listing_url}
                      </a>
                    </td>
                    <td>{company.has_parser ? "Yes" : "No"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
