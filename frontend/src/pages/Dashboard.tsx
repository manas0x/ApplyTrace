import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import type { Application, Stats } from "../types";
import { Layout, StatusBadge, StatusFilter } from "../components/ui";

const CARD_LABELS: Array<[keyof Stats, string, string]> = [
  ["applied", "Applied", "bg-blue-500"],
  ["interviewing", "Interviewing", "bg-amber-500"],
  ["offered", "Offers", "bg-green-500"],
  ["rejected", "Rejected", "bg-red-500"],
];

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [apps, setApps] = useState<Application[]>([]);
  const [filter, setFilter] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api.stats().then(setStats).catch((e) => setError(String(e)));
    api.seed().catch(() => {}); // idempotent demo seed on first visit
  }, []);

  useEffect(() => {
    api
      .listApplications(filter || undefined)
      .then(setApps)
      .catch((e) => setError(String(e)));
  }, [filter]);

  if (error) return <Layout><p className="text-red-600">Backend not reachable: {error}</p></Layout>;

  return (
    <Layout>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {CARD_LABELS.map(([key, label, color]) => (
          <div key={key} className="bg-white rounded-xl shadow-sm p-4 border">
            <div className={`w-2 h-2 rounded-full ${color} mb-2`} />
            <div className="text-3xl font-bold">{stats ? stats[key] : "…"}</div>
            <div className="text-sm text-slate-500">{label}</div>
          </div>
        ))}
      </div>

      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Applications</h2>
        <StatusFilter value={filter} onChange={setFilter} />
      </div>

      <div className="space-y-3">
        {apps.map((a) => (
          <Link
            key={a.id}
            to={`/applications/${a.id}`}
            className="block bg-white rounded-xl shadow-sm border p-4 hover:shadow-md transition"
          >
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium">{a.role}</div>
                <div className="text-sm text-slate-500">
                  {a.company} · {a.location || "—"} · applied {a.applied_date}
                </div>
              </div>
              <div className="flex items-center gap-3">
                {a.match_score !== null && (
                  <span className="text-sm font-semibold text-indigo-600">{a.match_score}% match</span>
                )}
                <StatusBadge status={a.status} />
              </div>
            </div>
          </Link>
        ))}
        {apps.length === 0 && (
          <p className="text-slate-500 text-sm">
            No applications here yet. <Link to="/add" className="text-indigo-600 underline">Add one →</Link>
          </p>
        )}
      </div>
    </Layout>
  );
}
