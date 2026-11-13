"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("citizen1");
  const [password, setPassword] = useState("demo123");
  const [error, setError] = useState("");

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok) {
      setError(data.detail || "Login failed");
      return;
    }
    localStorage.setItem("ncp_token", data.token);
    localStorage.setItem("ncp_role", data.role);
    localStorage.setItem("ncp_full_name", data.full_name);
    if (data.role === "officer" || data.role === "admin") router.push("/officer");
    else router.push("/citizen/apply");
  }

  return (
    <main className="mx-auto max-w-md px-6 py-12">
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-bold">Login</h1>
        <form onSubmit={onSubmit} className="mt-6 space-y-4">
          <input value={username} onChange={(e) => setUsername(e.target.value)} className="w-full rounded border border-slate-300 px-3 py-2" placeholder="Username" />
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full rounded border border-slate-300 px-3 py-2" placeholder="Password" />
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button className="w-full rounded bg-slate-900 px-4 py-3 text-white">Continue</button>
        </form>
      </div>
    </main>
  );
}
