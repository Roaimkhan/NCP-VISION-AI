"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function CitizenApplyPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    district: "Peshawar",
    make: "Toyota",
    model: "Corolla",
    year: "2014",
    color: "White",
    chassis_no: "NZE141-1234567",
    engine_no: "1NZ-A123456",
    owner_name: "Citizen One",
    owner_cnic: "99999-1234567-1",
    owner_phone: "03001234567",
  });
  const [tracking, setTracking] = useState<string | null>(null);
  const [error, setError] = useState("");

  async function submit() {
    const token = localStorage.getItem("ncp_token");
    const res = await fetch("/api/applications", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(form),
    });
    const data = await res.json();
    if (!res.ok) {
      setError(data.detail || "Submission failed");
      return;
    }
    setTracking(data.tracking_no);
  }

  if (tracking) {
    return (
      <main className="mx-auto max-w-xl px-6 py-12">
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-6 text-center">
          <h1 className="text-2xl font-bold">Application submitted</h1>
          <p className="mt-3">Tracking number: {tracking}</p>
          <button onClick={() => router.push(`/track/${tracking}`)} className="mt-6 rounded bg-emerald-600 px-4 py-2 text-white">View status</button>
        </div>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-3xl px-6 py-10">
      <h1 className="text-2xl font-bold">Citizen application</h1>
      <div className="mt-6 grid gap-4 md:grid-cols-2">
        {Object.entries(form).map(([key, value]) => (
          <label key={key} className="text-sm font-medium text-slate-700">
            {key.replace(/_/g, " ")}
            <input
              value={value}
              onChange={(e) => setForm((prev) => ({ ...prev, [key]: e.target.value }))}
              className="mt-1 w-full rounded border border-slate-300 px-3 py-2"
            />
          </label>
        ))}
      </div>
      {error && <p className="mt-4 text-red-600">{error}</p>}
      <button onClick={submit} className="mt-6 rounded bg-slate-900 px-4 py-3 text-white">Submit</button>
    </main>
  );
}
