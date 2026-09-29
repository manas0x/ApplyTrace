import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { setToken } from "../api";

// Landing page for Google's OAuth redirect: /login/callback?token=<jwt>
export default function LoginCallback() {
  const navigate = useNavigate();
  const [error, setError] = useState("");

  useEffect(() => {
    const token = new URLSearchParams(window.location.search).get("token");
    if (token) {
      setToken(token);
      navigate("/", { replace: true });
    } else {
      setError("Sign-in didn't return a session token. Please try again.");
    }
  }, [navigate]);

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center">
      {error ? (
        <p className="text-red-600 text-sm">{error}</p>
      ) : (
        <p className="text-slate-500 text-sm">Signing you in…</p>
      )}
    </div>
  );
}
