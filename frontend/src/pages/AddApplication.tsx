import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { Layout } from "../components/ui";
import { STATUSES } from "../types";

const inputCls = "w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400";

export default function AddApplication() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    company: "", role: "", location: "", status: "wishlist", link: "", notes: "",
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
    setForm((f) => ({ ...f, [k]: e.target.value }));

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      const app = await api.createApplication(form);
      navigate(`/applications/${app.id}`);
    } catch (err) {
      setError(String(err));
    } finally {
      setSaving(false);
    }
  }

  return (
    <Layout>
      <h2 className="text-lg font-semibold mb-4">Add application</h2>
      <form onSubmit={submit} className="bg-white rounded-xl border shadow-sm p-6 space-y-4 max-w-2xl">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium">Company *</label>
            <input required className={inputCls} value={form.company} onChange={set("company")} placeholder="e.g. Heizen" />
          </div>
          <div>
            <label className="text-sm font-medium">Role *</label>
            <input required className={inputCls} value={form.role} onChange={set("role")} placeholder="e.g. Software Engineer Intern" />
          </div>
          <div>
            <label className="text-sm font-medium">Location</label>
            <input className={inputCls} value={form.location} onChange={set("location")} placeholder="e.g. Bengaluru / Remote" />
          </div>
          <div>
            <label className="text-sm font-medium">Status</label>
            <select className={inputCls} value={form.status} onChange={set("status")}>
              {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
        </div>
        <div>
          <label className="text-sm font-medium">Apply link</label>
          <input className={inputCls} value={form.link} onChange={set("link")} placeholder="https://…" />
        </div>
        <div>
          <label className="text-sm font-medium">Notes</label>
          <textarea rows={3} className={inputCls} value={form.notes} onChange={set("notes")} placeholder="Stipend, batch eligibility, recruiter email…" />
        </div>
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <button
          disabled={saving}
          className="bg-indigo-600 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
        >
          {saving ? "Saving…" : "Save application"}
        </button>
      </form>
    </Layout>
  );
}
