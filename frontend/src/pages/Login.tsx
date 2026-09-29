import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, setToken } from "../api";

const inputCls =
  "w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400";

export default function Login() {
  const navigate = useNavigate();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const r =
        mode === "login"
          ? await api.login(email, password)
          : await api.register(email, password, name);
      setToken(r.token);
      navigate("/", { replace: true });
    } catch (err) {
      setError(String(err).replace(/^Error: /, ""));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
      <div className="bg-white rounded-2xl shadow-sm border p-8 max-w-sm w-full">
        <div className="text-3xl font-bold text-indigo-600 mb-1 text-center">ApplyTrace</div>
        <p className="text-sm text-slate-500 mb-6 text-center">
          {mode === "login" ? "Welcome back — sign in to your tracker." : "Create your account to start tracking."}
        </p>
        <form onSubmit={submit} className="space-y-3">
          {mode === "register" && (
            <input
              className={inputCls}
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Your name"
            />
          )}
          <input
            className={inputCls}
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email address"
          />
          <input
            className={inputCls}
            type="password"
            required
            minLength={6}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password (min 6 characters)"
          />
          {error && <p className="text-red-600 text-xs">{error}</p>}
          <button
            disabled={busy}
            className="w-full bg-indigo-600 text-white py-2.5 rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
          >
            {busy ? "Please wait…" : mode === "login" ? "Sign in" : "Create account"}
          </button>
        </form>
        <p className="text-xs text-slate-500 mt-4 text-center">
          {mode === "login" ? (
            <>
              New here?{" "}
              <button className="text-indigo-600 underline" onClick={() => setMode("register")}>
                Create an account
              </button>
            </>
          ) : (
            <>
              Already have an account?{" "}
              <button className="text-indigo-600 underline" onClick={() => setMode("login")}>
                Sign in
              </button>
            </>
          )}
        </p>
      </div>
    </div>
  );
}
