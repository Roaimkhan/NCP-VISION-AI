"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

type TrackData = {
  tracking_no: string;
  status: string;
  district: string;
  make: string;
  model: string;
  year: number;
};

export default function TrackPage() {
  const params = useParams<{ trackingNo: string }>();
  const [data, setData] = useState<TrackData | null>(null);

  useEffect(() => {
    fetch(`/api/track/${params.trackingNo}`)
      .then((res) => res.json())
      .then((json) => setData(json));
  }, [params.trackingNo]);

  if (!data) return <p className="p-8">Loading...</p>;

  return (
    <main className="mx-auto max-w-2xl px-6 py-12">
      <div className="rounded border bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-bold">Tracking {data.tracking_no}</h1>
        <p className="mt-3 text-slate-600">Status: {data.status}</p>
        <div className="mt-4 grid gap-2 text-sm">
          <div>District: {data.district}</div>
          <div>Vehicle: {data.make} {data.model}</div>
          <div>Year: {data.year}</div>
        </div>
      </div>
    </main>
  );
}
