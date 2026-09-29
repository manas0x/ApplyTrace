import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import AddApplication from "./pages/AddApplication";
import ApplicationDetail from "./pages/ApplicationDetail";
import Discover from "./pages/Discover";
import Login from "./pages/Login";
import { getToken } from "./api";

function RequireAuth({ children }: { children: React.ReactNode }) {
  return getToken() ? <>{children}</> : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<RequireAuth><Dashboard /></RequireAuth>} />
        <Route path="/add" element={<RequireAuth><AddApplication /></RequireAuth>} />
        <Route path="/discover" element={<RequireAuth><Discover /></RequireAuth>} />
        <Route path="/applications/:id" element={<RequireAuth><ApplicationDetail /></RequireAuth>} />
      </Routes>
    </BrowserRouter>
  );
}
