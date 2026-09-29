import { useState } from "react";
import { api } from "../api";

export default function Login() {
  const [error, setError] = useState("");

  async function signIn() {
    setError("");
    try {
      const { url } = await api.googleLoginUrl();
      window.location.href = url;
    } catch (e) {
      setError(String(e));
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
      <div className="bg-white rounded-2xl shadow-sm border p-8 max-w-sm w-full text-center">
        <div className="text-3xl font-bold text-indigo-600 mb-2">ApplyTrace</div>
        <p className="text-sm text-slate-500 mb-6">
          Your 2027-batch job hunt, tracked. Applications, resume matching, and Gmail auto-detect.
        </p>
        <button
          onClick={signIn}
          className="w-full bg-indigo-600 text-white py-2.5 rounded-lg text-sm font-medium hover:bg-indigo-700"
        >
          Continue with Google
        </button>
        {error && <p className="text-red-600 text-xs mt-3">{error}</p>}
        <p className="text-xs text-slate-400 mt-4">Sign-in keeps your tracker private to you.</p>
      </div>
    </div>
  );
}
