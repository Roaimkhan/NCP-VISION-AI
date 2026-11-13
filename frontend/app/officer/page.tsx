"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

type AppRow = {
  id: number;
  tracking_no: string;
  status: string;
  district: string;
  make: string;
  model: string;
  risk_level: string;
};

export default function OfficerPage() {
  const router = useRouter();
  const [apps, setApps] = useState<AppRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("ncp_token");
    if (!token) {
      router.push("/login");
      return;
    }
    fetch("/api/officer/applications", { headers: { Authorization: `Bearer ${token}` } })
      .then(async (res) => {
        if (!res.ok) throw new Error("Unauthorized");
        const data = await res.json();
        setApps(data.items || []);
      })
      .catch(() => router.push("/login"))
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) return <p className="p-8">Loading...</p>;

  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <h1 className="text-2xl font-bold">Officer dashboard</h1>
      <div className="mt-6 grid gap-4 md:grid-cols-3">
        <div className="rounded border bg-white p-4"><b>Total</b><div>{apps.length}</div></div>
        <div className="rounded border bg-white p-4"><b>Submitted</b><div>{apps.filter((a) => a.status === "SUBMITTED").length}</div></div>
        <div className="rounded border bg-white p-4"><b>Under review</b><div>{apps.filter((a) => a.status === "UNDER_REVIEW").length}</div></div>
      </div>
      <div className="mt-8 overflow-hidden rounded border bg-white shadow-sm">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-slate-100">
            <tr>
              <th className="px-4 py-3">Tracking</th>
              <th className="px-4 py-3">District</th>
              <th className="px-4 py-3">Vehicle</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Risk</th>
            </tr>
          </thead>
          <tbody>
            {apps.map((app) => (
              <tr key={app.id} className="border-t cursor-pointer hover:bg-slate-50" onClick={() => router.push(`/officer/applications/${app.id}`)}>
                <td className="px-4 py-3">{app.tracking_no}</td>
                <td className="px-4 py-3">{app.district}</td>
                <td className="px-4 py-3">{app.make} {app.model}</td>
                <td className="px-4 py-3">{app.status}</td>
                <td className="px-4 py-3">{app.risk_level}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}
