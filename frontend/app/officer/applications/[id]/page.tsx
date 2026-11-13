"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

type AlertItem = {
  id: number;
  type: string;
  severity: string;
  message: string;
};

type AppDetail = {
  application: {
    tracking_no: string;
    status: string;
    district: string;
    make: string;
    model: string;
    risk_level: string;
    chassis_no?: string;
    engine_no?: string;
  };
  alerts: AlertItem[];
};

export default function OfficerApplicationDetailPage() {
  const params = useParams<{ id: string }>();
  const [app, setApp] = useState<AppDetail | null>(null);
  const [error, setError] = useState("");

  async function load() {
    const token = localStorage.getItem("ncp_token");
    const res = await fetch(`/api/officer/applications/${params.id}`, { headers: { Authorization: `Bearer ${token}` } });
    const data = await res.json();
    if (!res.ok) {
      setError(data.detail || "Failed to load");
      return;
    }
    setApp(data);
  }

  useEffect(() => { load(); }, [params.id]);

  async function action(name: string) {
    const token = localStorage.getItem("ncp_token");
    const note = name === "request_info" ? window.prompt("Why is this needed?") : undefined;
    const res = await fetch(`/api/officer/applications/${params.id}/action`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ action: name, note }),
    });
    const data = await res.json();
    if (!res.ok) {
      setError(data.detail || "Action failed");
      return;
    }
    await load();
  }

  if (!app) return <p className="p-8">Loading...</p>;

  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <h1 className="text-2xl font-bold">Application {app.application.tracking_no}</h1>
      {error && <p className="mt-2 text-red-600">{error}</p>}
      <div className="mt-6 grid gap-6 md:grid-cols-2">
        <div className="rounded border bg-white p-4">
          <h2 className="font-semibold">Vehicle</h2>
          <ul className="mt-3 space-y-2 text-sm">
            <li>Status: {app.application.status}</li>
            <li>District: {app.application.district}</li>
            <li>Make/Model: {app.application.make} {app.application.model}</li>
            <li>Risk: {app.application.risk_level}</li>
            <li>Chassis: {app.application.chassis_no}</li>
            <li>Engine: {app.application.engine_no}</li>
          </ul>
        </div>
        <div className="rounded border bg-white p-4">
          <h2 className="font-semibold">Actions</h2>
          <div className="mt-3 flex flex-wrap gap-2">
            <button onClick={() => action("start_review")} className="rounded bg-slate-900 px-3 py-2 text-white">Start Review</button>
            <button onClick={() => action("request_info")} className="rounded bg-amber-600 px-3 py-2 text-white">Request Info</button>
            <button onClick={() => action("verify")} className="rounded bg-emerald-600 px-3 py-2 text-white">Verify</button>
            <button onClick={() => action("close_incomplete")} className="rounded bg-red-600 px-3 py-2 text-white">Close Incomplete</button>
          </div>
        </div>
      </div>
      <div className="mt-8 rounded border bg-white p-4">
        <h2 className="font-semibold">Alerts</h2>
        <ul className="mt-3 space-y-3">
          {app.alerts.map((alert: AlertItem) => (
            <li key={alert.id} className="rounded border p-3 text-sm">
              <div className="font-medium">{alert.type} ({alert.severity})</div>
              <div>{alert.message}</div>
            </li>
          ))}
        </ul>
      </div>
    </main>
  );
}
