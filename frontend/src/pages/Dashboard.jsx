import { useEffect, useState } from "react";
import { getHistory } from "../api/client";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function Dashboard() {
  const [reports, setReports] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getHistory()
      .then((res) => setReports(res.data))
      .catch(() => setError("Could not load history"));
  }, []);

  return (
    <div className="max-w-3xl mx-auto px-6 pt-16 pb-20">
      <h1 className="font-display text-3xl mb-8">Your scan history</h1>
      {error && <p className="text-red-600 text-sm">{error}</p>}
      {reports.length === 0 && !error && (
        <p className="text-clinic-ink/50">
          No scans yet — head to New Scan to run your first analysis.
        </p>
      )}
      <div className="space-y-4">
        {reports.map((r) => (
          <div
            key={r.id}
            className="bg-white border border-clinic-line rounded-xl p-4 flex items-center gap-4"
          >
            <img
              src={`${API_BASE_URL}${r.original_image_path}`}
              className="w-16 h-16 rounded-lg object-cover"
            />
            <div className="flex-1">
              <p className="font-medium capitalize">
                {r.predicted_class.replace("_", " ")}
              </p>
              <p className="text-xs text-clinic-ink/50">
                {new Date(r.created_at).toLocaleString()}
              </p>
            </div>
            <p className="text-sm text-clinic-sageDark font-medium">
              {(r.confidence * 100).toFixed(0)}%
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
