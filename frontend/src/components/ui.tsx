import { Link } from "react-router-dom";
import { STATUSES } from "./types";

const STATUS_STYLES: Record<string, string> = {
  wishlist: "bg-gray-100 text-gray-700",
  applied: "bg-blue-100 text-blue-700",
  interviewing: "bg-amber-100 text-amber-700",
  offered: "bg-green-100 text-green-700",
  rejected: "bg-red-100 text-red-700",
};

export function StatusBadge({ status }: { status: string }) {
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_STYLES[status] ?? "bg-gray-100"}`}>
      {status}
    </span>
  );
}

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <nav className="bg-white border-b shadow-sm">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center gap-6">
          <Link to="/" className="font-bold text-xl text-indigo-600">ApplyTrace</Link>
          <Link to="/" className="text-sm hover:text-indigo-600">Dashboard</Link>
          <Link to="/add" className="text-sm hover:text-indigo-600">Add application</Link>
          <span className="ml-auto text-xs text-slate-400">2027 batch hunt 🎯</span>
        </div>
      </nav>
      <main className="max-w-5xl mx-auto px-4 py-6">{children}</main>
    </div>
  );
}

export function StatusFilter({
  value,
  onChange,
}: {
  value: string;
  onChange: (s: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      <FilterButton active={value === ""} onClick={() => onChange("")} label="All" />
      {STATUSES.map((s) => (
        <FilterButton key={s} active={value === s} onClick={() => onChange(s)} label={s} />
      ))}
    </div>
  );
}

function FilterButton({ active, onClick, label }: { active: boolean; onClick: () => void; label: string }) {
  return (
    <button
      onClick={onClick}
      className={`px-3 py-1 rounded-full text-sm border ${
        active ? "bg-indigo-600 text-white border-indigo-600" : "bg-white text-slate-600 hover:border-indigo-400"
      }`}
    >
      {label}
    </button>
  );
}
