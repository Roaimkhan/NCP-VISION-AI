import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NCP Vision",
  description: "Citizen and officer portal",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-100 text-slate-900 antialiased">
        <div className="border-b border-amber-300 bg-amber-100 px-4 py-3 text-center text-sm font-medium text-amber-900">
          DEMO — synthetic data. Profiling is not registration, customs clearance, or eligibility for any scheme.
        </div>
        {children}
      </body>
    </html>
  );
}
