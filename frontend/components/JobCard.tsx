import { JobDetails } from "@/lib/api";

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

export function JobCard({ job }: { job: JobDetails }) {
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

      {job.error && (
        <p className="status error" style={{ marginTop: "0.5rem" }}>
          {job.error}
        </p>
      )}
    </article>
  );
}
