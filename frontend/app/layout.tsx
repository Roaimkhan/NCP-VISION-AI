import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NCP Vision",
  description: "NCP Vision MVP scaffold",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
