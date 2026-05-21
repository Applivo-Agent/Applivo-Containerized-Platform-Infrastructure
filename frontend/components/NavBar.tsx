"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { 
  ChevronDown, 
  Activity, 
  ShieldCheck, 
  FileText 
} from "lucide-react";
import { useAuth } from "@/lib/auth";

/* ─── NAV LINKS ──────────────────────────────────────────── */
const navLinks = [
  { label: "Dashboard", href: "/dashboard" },
  { label: "Workflow", href: "/#workflow" },
  { label: "Features", href: "/#features" },
  { label: "Integrations", href: "/#integrations" },
  { label: "Pricing", href: "/#pricing" },
];

const resourceLinks = [
  { label: "Changelog", href: "/resources/changelog", icon: <Activity className="w-4 h-4" /> },
  { label: "Privacy Policy", href: "/resources/privacy-policy", icon: <ShieldCheck className="w-4 h-4" /> },
  { label: "Terms of Use", href: "/resources/terms-of-use", icon: <FileText className="w-4 h-4" /> },
];

type NavBarProps = {
  sidebarOffset?: boolean;
};

export function NavBar({ sidebarOffset = false }: NavBarProps) {
  const router = useRouter();
  const { isAuthenticated, isLoading, logout } = useAuth();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <header
      className={`fixed top-0 ${sidebarOffset ? "left-[17rem]" : "left-0"} right-0 z-50 transition-all duration-300 ${
        scrolled
            ? "bg-[#050505]/95 backdrop-blur-md border-b border-white/[0.06]"
            : "bg-transparent"
      }`}
    >
      <div className="max-w-[1400px] mx-auto flex items-center justify-between px-6 md:px-10 h-[64px]">

        {/* Logo — left */}
        <Link href="/" className="flex items-center gap-3 shrink-0">
          <Image src="/logo.png" alt="Applivo" width={56} height={56} className="rounded-xl object-contain" priority />
          <span className="text-white font-bold text-[22px] tracking-tight">Applivo</span>
        </Link>

        {/* Nav links — center */}
        <nav className="hidden md:flex items-center gap-8 absolute left-1/2 -translate-x-1/2">
          {navLinks.map((l) => (
            <Link
              key={l.label}
              href={l.href}
              className="text-[14px] font-medium text-[#888] hover:text-white transition-colors duration-200"
            >
              {l.label}
            </Link>
          ))}

          {/* Resources Dropdown */}
          <div className="relative group/resources">
            <button className="flex items-center gap-1.5 text-[14px] font-medium text-[#888] group-hover/resources:text-white transition-colors duration-200 py-4">
              Resources
              <ChevronDown className="w-3.5 h-3.5 opacity-50 group-hover/resources:rotate-180 transition-transform duration-300" />
            </button>

            {/* Glassy Dropdown Menu */}
            <div className="absolute top-full left-1/2 -translate-x-1/2 pointer-events-none group-hover/resources:pointer-events-auto group-hover/resources:opacity-100 group-hover/resources:translate-y-0 opacity-0 translate-y-2 transition-all duration-300 z-[100]">
              <div className="w-[220px] mt-1 bg-[#0d0d0d]/95 backdrop-blur-xl border border-white/10 rounded-2xl p-2 shadow-[0_20px_40px_-15px_rgba(0,0,0,0.5)]">
                {resourceLinks.map((item) => (
                  <Link
                    key={item.label}
                    href={item.href}
                    className="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-white/5 text-[13px] text-zinc-400 hover:text-white transition-all group/item"
                  >
                    <div className="w-8 h-8 rounded-lg bg-zinc-900 border border-white/5 flex items-center justify-center text-zinc-500 group-hover/item:text-blue-500 group-hover/item:border-blue-500/20 transition-colors">
                      {item.icon}
                    </div>
                    {item.label}
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </nav>

        {/* CTA — right */}
        <div className="flex items-center gap-3 shrink-0">
          {!isLoading && isAuthenticated ? (
            <>
              <button
                type="button"
                onClick={handleLogout}
                className="hidden sm:block text-[14px] font-medium text-[#666] hover:text-white transition-colors duration-200"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className="hidden sm:block text-[14px] font-medium text-[#666] hover:text-white transition-colors duration-200"
              >
                Log in
              </Link>
              <Link
                href="/register"
                className="px-5 py-2 rounded-lg border border-white/20 text-white text-[14px] font-medium hover:bg-white hover:text-black transition-all duration-200 shadow-xl"
              >
                Sign up
              </Link>
            </>
          )}
        </div>

      </div>
    </header>
  );
}
