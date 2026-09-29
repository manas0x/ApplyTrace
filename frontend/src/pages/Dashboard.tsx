import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import type { Application, Stats } from "../types";
import { Layout, StatusBadge } from "../components/ui";
import { STATUSES } from "../types";

const COLUMN_STYLES: Record<string, string> = {
  wishlist: "border-slate-300",
  applied: "border-blue-300",
  interviewing: "border-amber-300",
  offered: "border-green-300",
  rejected: "border-red-300",
};

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [apps, setApps] = useState<Application[]>([]);
  const [error, setError] = useState("");
  const [gmail, setGmail] = useState<{ connected: boolean; email: string | null } | null>(null);
  const [syncing, setSyncing] = useState(false);
  const [syncMsg, setSyncMsg] = useState("");

  const refreshData = async () => {
    const [s, a] = await Promise.all([api.stats(), api.listApplications()]);
    setStats(s);
    setApps(a);
  };

  const runGmailSync = async () => {
    setSyncing(true);
    setSyncMsg("");
    try {
      const r = await api.gmailSync();
      const names = r.companies.slice(0, 3).join(", ");
      setSyncMsg(
        `Gmail sync: ${r.added} new application${r.added === 1 ? "" : "s"}` +
          (names ? ` (${names}${r.companies.length > 3 ? ", …" : ""})` : "") +
          `, ${r.skipped} already tracked.`
      );
      await refreshData();
    } catch (e) {
      setSyncMsg(`Sync failed: ${e}`);
    }
    setSyncing(false);
  };

  const handleGmail = async () => {
    if (gmail?.connected) {
      await runGmailSync();
      return;
    }
    try {
      const { url } = await api.gmailAuthUrl();
      window.location.href = url;
    } catch (e) {
      setSyncMsg(`Could not start Gmail connect: ${e}`);
    }
  };

  const moveStatus = async (app: Application, status: string) => {
    try {
      const updated = await api.updateApplication(app.id, { status });
      setApps((prev) => prev.map((a) => (a.id === app.id ? updated : a)));
      const s = await api.stats();
      setStats(s);
    } catch (e) {
      setSyncMsg(`Could not move: ${e}`);
    }
  };

  const clearDemo = async () => {
    if (!confirm("Remove the demo applications? Your real entries stay untouched.")) return;
    try {
      const r = await api.clearDemo();
      setSyncMsg(`Removed ${r.removed} demo application${r.removed === 1 ? "" : "s"}.`);
      await refreshData();
    } catch (e) {
      setSyncMsg(`Cleanup failed: ${e}`);
    }
  };

  useEffect(() => {
    refreshData().catch((e) => setError(String(e)));
    api.gmailStatus().then(setGmail).catch(() => setGmail({ connected: false, email: null }));
    if (new URLSearchParams(window.location.search).get("gmail") === "connected") {
      window.history.replaceState({}, "", "/");
      setGmail({ connected: true, email: null });
      runGmailSync();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (error) return <Layout><p className="text-red-600">Backend not reachable: {error}</p></Layout>;

  return (
    <Layout>
      <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
        <h2 className="text-lg font-semibold">
          Pipeline {stats && <span className="text-sm font-normal text-slate-500">· {stats.total} total</span>}
        </h2>
        <div className="flex items-center gap-3 flex-wrap">
          {syncMsg && <span className="text-xs text-slate-500 max-w-[260px]">{syncMsg}</span>}
          <button
            onClick={handleGmail}
            disabled={syncing}
            className="text-sm px-3 py-1.5 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50"
            title={gmail?.email ? `Connected as ${gmail.email}` : "Detect applications from your Gmail"}
          >
            {syncing ? "Syncing…" : gmail?.connected ? "Sync from Gmail" : "Connect Gmail"}
          </button>
          <button onClick={clearDemo} className="text-xs text-slate-400 hover:text-red-600 underline">
            Clear demo data
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {STATUSES.map((status) => {
          const col = apps.filter((a) => a.status === status);
          return (
            <div key={status} className={`bg-white rounded-xl border-t-4 ${COLUMN_STYLES[status]} border shadow-sm p-3`}>
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-semibold capitalize">{status}</span>
                <span className="text-xs text-slate-400 bg-slate-100 rounded-full px-2 py-0.5">{col.length}</span>
              </div>
              <div className="space-y-2">
                {col.map((a) => (
                  <div key={a.id} className="bg-slate-50 rounded-lg border p-3 hover:shadow-sm transition">
                    <Link to={`/applications/${a.id}`} className="block">
                      <div className="font-medium text-sm leading-tight">{a.role}</div>
                      <div className="text-xs text-slate-500 mt-0.5">
                        {a.company}{a.location ? ` · ${a.location}` : ""}
                      </div>
                      <div className="flex items-center gap-2 mt-1.5">
                        <StatusBadge status={a.status} />
                        {a.match_score !== null && (
                          <span className="text-xs font-semibold text-indigo-600">{a.match_score}%</span>
                        )}
                      </div>
                    </Link>
                    <select
                      value={a.status}
                      onChange={(e) => moveStatus(a, e.target.value)}
                      className="mt-2 w-full text-xs border rounded-md px-1.5 py-1 bg-white"
                    >
                      {STATUSES.map((s) => (
                        <option key={s} value={s}>Move to {s}</option>
                      ))}
                    </select>
                  </div>
                ))}
                {col.length === 0 && (
                  <p className="text-xs text-slate-300 italic">Nothing here</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </Layout>
  );
}
