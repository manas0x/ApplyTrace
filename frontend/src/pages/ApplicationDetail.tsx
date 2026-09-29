import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api";
import type { AnalyzeResult, Application } from "../types";
import { Layout, StatusBadge } from "../components/ui";
import { STATUSES } from "../types";

const inputCls = "w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400";

export default function ApplicationDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const appId = Number(id);
  const [app, setApp] = useState<Application | null>(null);
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [jdUrl, setJdUrl] = useState("");
  const [fetchingJd, setFetchingJd] = useState(false);

  async function fetchJdFromLink() {
    const url = (jdUrl || app?.link || "").trim();
    if (!url) { setError("Paste a job posting link first."); return; }
    setFetchingJd(true); setError("");
    try {
      const r = await api.fetchJd(url);
      setApp((prev) => prev ? { ...prev, jd_text: r.text } : prev);
    } catch (e) { setError(String(e)); }
    finally { setFetchingJd(false); }
  }

  useEffect(() => {
    api.getApplication(appId).then(setApp).catch((e) => setError(String(e)));
  }, [appId]);

  async function save() {
    if (!app) return;
    setBusy(true);
    try {
      const updated = await api.updateApplication(appId, {
        jd_text: app.jd_text, resume_text: app.resume_text, status: app.status,
      });
      setApp(updated);
    } catch (e) { setError(String(e)); }
    finally { setBusy(false); }
  }

  async function analyze() {
    setBusy(true); setError("");
    try {
      await save();
      const r = await api.analyzeApplication(appId);
      setResult(r);
      const fresh = await api.getApplication(appId); // pulls saved match_score
      setApp(fresh);
    } catch (e) { setError(String(e)); }
    finally { setBusy(false); }
  }

  if (error) return <Layout><p className="text-red-600">{error}</p></Layout>;
  if (!app) return <Layout><p>Loading…</p></Layout>;

  return (
    <Layout>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-xl font-bold">{app.role}</h2>
          <p className="text-sm text-slate-500">{app.company} · {app.location || "—"}</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            className="border rounded-lg px-2 py-1 text-sm"
            value={app.status}
            onChange={(e) => setApp({ ...app, status: e.target.value })}
          >
            {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
          <StatusBadge status={app.status} />
        </div>
      </div>

      <div className="bg-white rounded-xl border p-4 mb-4">
        <label className="text-sm font-medium">Fetch the JD automatically</label>
        <div className="flex gap-2 mt-1">
          <input
            className={inputCls}
            value={jdUrl}
            onChange={(e) => setJdUrl(e.target.value)}
            placeholder={app.link || "Paste the job posting link…"}
          />
          <button
            onClick={fetchJdFromLink}
            disabled={fetchingJd}
            className="shrink-0 bg-slate-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-slate-700 disabled:opacity-50"
          >
            {fetchingJd ? "Fetching…" : "Auto-fill JD"}
          </button>
        </div>
        <p className="text-xs text-slate-400 mt-1">Downloads the posting and extracts the description — no manual pasting needed.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-4 mb-4">
        <div className="bg-white rounded-xl border p-4">
          <label className="text-sm font-medium">Job description</label>
          <textarea rows={10} className={inputCls + " mt-1 font-mono"}
            value={app.jd_text}
            onChange={(e) => setApp({ ...app, jd_text: e.target.value })}
            placeholder="Paste the job description here…" />
        </div>
        <div className="bg-white rounded-xl border p-4">
          <label className="text-sm font-medium">Resume text (version used for this application)</label>
          <textarea rows={10} className={inputCls + " mt-1 font-mono"}
            value={app.resume_text}
            onChange={(e) => setApp({ ...app, resume_text: e.target.value })}
            placeholder="Paste your resume text here…" />
        </div>
      </div>

      <div className="flex gap-3 mb-6">
        <button onClick={save} disabled={busy} className="bg-white border px-4 py-2 rounded-lg text-sm font-medium hover:border-indigo-400">
          Save changes
        </button>
        <button onClick={analyze} disabled={busy} className="bg-indigo-600 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50">
          {busy ? "Analyzing…" : "Analyze match"}
        </button>
        <button
          onClick={async () => { if (confirm("Delete this application?")) { await api.deleteApplication(appId); navigate("/"); } }}
          className="ml-auto text-red-600 text-sm hover:underline"
        >
          Delete
        </button>
      </div>

      {result && (
        <div className="bg-white rounded-xl border p-5 space-y-4">
          <div className="flex items-center gap-4">
            <div className={`text-4xl font-bold ${result.score >= 70 ? "text-green-600" : result.score >= 40 ? "text-amber-600" : "text-red-600"}`}>
              {result.score}%
            </div>
            <div className="text-sm text-slate-500">resume ↔ JD match</div>
          </div>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <h3 className="text-sm font-semibold text-green-700 mb-2">Matched keywords</h3>
              <div className="flex flex-wrap gap-1.5">
                {result.matched_keywords.map((k) => (
                  <span key={k} className="bg-green-100 text-green-800 text-xs px-2 py-0.5 rounded-full">{k}</span>
                ))}
              </div>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-red-700 mb-2">Missing keywords</h3>
              <div className="flex flex-wrap gap-1.5">
                {result.missing_keywords.map((k) => (
                  <span key={k} className="bg-red-100 text-red-800 text-xs px-2 py-0.5 rounded-full">{k}</span>
                ))}
              </div>
            </div>
          </div>
          <div>
            <h3 className="text-sm font-semibold mb-2">Suggested tweaks</h3>
            <ul className="list-disc pl-5 text-sm text-slate-700 space-y-1">
              {result.suggested_tweaks.map((t, i) => <li key={i}>{t}</li>)}
            </ul>
          </div>
        </div>
      )}
    </Layout>
  );
}
