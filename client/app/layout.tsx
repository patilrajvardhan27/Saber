import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Building Audit Tool",
  description: "Energy Efficiency Evaluation for Buildings",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
