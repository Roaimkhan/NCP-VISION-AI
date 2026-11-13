"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function HomePage() {
  const router = useRouter();
  const [tracking, setTracking] = useState("");

  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <div className="grid gap-8 md:grid-cols-2">
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h1 className="text-3xl font-bold">NCP-VISION AI</h1>
          <p className="mt-3 text-slate-600">Citizen and officer workflows for synthetic import checks.</p>
          <div className="mt-6 space-y-3">
            <a href="/login" className="block rounded bg-slate-900 px-4 py-3 text-center text-white">Citizen Login</a>
            <a href="/officer" className="block rounded border border-slate-300 bg-white px-4 py-3 text-center text-slate-900">Officer Portal</a>
          </div>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold">Track application</h2>
          <div className="mt-4 flex gap-2">
            <input
              value={tracking}
              onChange={(e) => setTracking(e.target.value)}
              className="w-full rounded border border-slate-300 px-3 py-2"
              placeholder="NCP-KP-2026-000123"
            />
            <button
              onClick={() => router.push(`/track/${tracking}`)}
              className="rounded bg-amber-600 px-4 py-2 text-white"
            >
              Go
            </button>
          </div>
        </section>
      </div>
    </main>
  );
}
