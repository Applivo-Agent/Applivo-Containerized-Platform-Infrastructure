import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const outfit = Outfit({ subsets: ["latin"], variable: "--font-outfit" });

export const metadata: Metadata = {
  title: {
    default: "Applivo — AI Career Automation Platform",
    template: "%s | Applivo",
  },
  description:
    "Automate your job search with AI. Applivo scrapes job boards, scores opportunities, generates ATS-optimised resumes, and applies automatically — all on autopilot.",
  keywords: [
    "job search automation",
    "AI resume builder",
    "auto apply jobs",
    "ATS optimized",
    "career automation",
    "Internshala automation",
    "job scraper",
  ],
  openGraph: {
    title: "Applivo — AI Career Automation Platform",
    description: "Automate your job search. Apply to 500 jobs a day on autopilot.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${inter.variable} ${outfit.variable} font-sans antialiased bg-background text-foreground`}
      >
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
