"use client";
import React from "react";
import { SimplePricing as Pricing } from "@/components/ainest/Pricing";
import { NavBar } from "@/components/NavBar";

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-black text-white selection:bg-white/20">
      <NavBar />
      
      {/* 
          We're using the shared SimplePricing component here to ensure 
          total visual and functional consistency (including the toggle) 
          between the dedicated /pricing page and the landing page section.
      */}
      <div className="pt-24 md:pt-32">
        <Pricing />
      </div>

      <div className="max-w-4xl mx-auto px-6 pb-24 text-center">
        <p className="text-zinc-700 text-[10px] font-black uppercase tracking-[0.3em]">
            Precision Engineering by Applivo © 2026
        </p>
      </div>
    </div>
  );
}
