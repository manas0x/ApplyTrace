import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, type DiscoveredJob } from "../api";
import { Layout } from "../components/ui";

export default function Discover() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("software developer intern");
  const [location, setLocation] = useState("India");
  const [jobs, setJobs] = useState<DiscoveredJob[]>([]);
  const [count, setCount] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [added, setAdded] = useState<Set<string>>(new Set());

  async function search(e?: React.FormEvent) {
    e?.preventDefault();
    setBusy(true);
    setError("");
    try {
      const r = await api.discoverJobs(query, location);
      setJobs(r.jobs);
      setCount(r.count);
    } catch (err) {
      setError(String(err));
    } finally {
      setBusy(false);
    }
  }

  async function track(job: DiscoveredJob) {
    try {
      const app = await api.createApplication({
        company: job.company || "Unknown",
        role: job.title || "Unknown role",
        location: job.location,
        status: "wishlist",
        link: job.url,
        jd_text: job.snippet,
        notes: `Found via job discovery (posted ${job.posted || "n/a"}).`,
      });
      setAdded((prev) => new Set(prev).add(job.url));
      navigate(`/applications/${app.id}`);
    } catch (err) {
      setError(String(err));
    }
  }

  return (
    <Layout>
      <h2 className="text-lg font-semibold mb-1">Discover jobs</h2>
      <p className="text-sm text-slate-500 mb-4">Live listings matched to your search. One click adds them to your board.</p>

      <form onSubmit={search} className="flex gap-2 mb-6 flex-wrap">
        <input
          className="border rounded-lg px-3 py-2 text-sm flex-1 min-w-[200px]"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. frontend developer intern"
        />
        <input
          className="border rounded-lg px-3 py-2 text-sm w-40"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          placeholder="Location"
        />
        <button
          disabled={busy}
          className="bg-indigo-600 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
        >
          {busy ? "Searching…" : "Search"}
        </button>
      </form>

      {error && <p className="text-red-600 text-sm mb-4">{error}</p>}
      {count !== null && !error && (
        <p className="text-xs text-slate-500 mb-3">{count} results</p>
      )}

      <div className="space-y-3">
        {jobs.map((j) => (
          <div key={j.url} className="bg-white rounded-xl border p-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <a href={j.url} target="_blank" rel="noreferrer" className="font-medium hover:text-indigo-600">
                  {j.title}
                </a>
                <div className="text-sm text-slate-500">
                  {j.company}{j.location ? ` · ${j.location}` : ""}{j.posted ? ` · posted ${j.posted}` : ""}
                </div>
                {j.snippet && <p className="text-sm text-slate-600 mt-2 line-clamp-3">{j.snippet}</p>}
              </div>
              <button
                onClick={() => track(j)}
                disabled={added.has(j.url)}
                className="shrink-0 text-sm px-3 py-1.5 rounded-lg border hover:border-indigo-400 disabled:opacity-50"
              >
                {added.has(j.url) ? "Added ✓" : "Track →"}
              </button>
            </div>
          </div>
        ))}
      </div>
    </Layout>
  );
}
