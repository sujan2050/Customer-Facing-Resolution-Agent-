import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Resolve — SkyRoute Multi-Agent Airline Support",
  description: "Policy-grounded multi-agent customer resolution system for airline disruptions",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark h-full">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="h-full bg-background text-slate-100 flex flex-col font-sans antialiased selection:bg-primary-500/30 selection:text-white">
        {children}
      </body>
    </html>
  );
}
