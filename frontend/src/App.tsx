import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import AddApplication from "./pages/AddApplication";
import ApplicationDetail from "./pages/ApplicationDetail";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/add" element={<AddApplication />} />
        <Route path="/applications/:id" element={<ApplicationDetail />} />
      </Routes>
    </BrowserRouter>
  );
}
