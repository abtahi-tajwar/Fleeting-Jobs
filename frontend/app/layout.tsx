import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Fleeting Jobs",
  description: "Scrape career pages, classify jobs with AI, and extract requirements",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
