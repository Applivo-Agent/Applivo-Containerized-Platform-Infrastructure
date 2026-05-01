"use client";
import React, { useState, Suspense, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { Eye, EyeOff, Loader2 } from "lucide-react";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { cn, getErrorMessage } from "@/lib/utils";

// --- Icons ---
const GoogleIcon = () => (
  <svg viewBox="0 0 24 24" className="w-5 h-5">
    <path fill="#EA4335" d="M12 5.04c1.9 0 3.51.65 4.85 1.91l3.61-3.61C18.25 1.25 15.35 0 12 0 7.33 0 3.32 2.67 1.35 6.57l4.16 3.23C6.51 7.02 9.04 5.04 12 5.04z" />
    <path fill="#FBBC05" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31l3.41 2.64c2-1.84 3.16-4.55 3.16-7.8c0-.06 0-.11-.01-.16z" />
    <path fill="#4285F4" d="M5.51 14.2c-.26-.78-.41-1.61-.41-2.45s.15-1.67.41-2.45L1.35 6.57c-.89 1.77-1.35 3.73-1.35 5.68 0 1.95.46 3.91 1.35 5.68l4.16-3.23z" />
    <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.41-2.64c-1.25.84-2.85 1.33-4.52 1.33-3.23 0-5.98-2.18-6.96-5.11L.89 17.88C2.86 21.33 6.67 24 12 24z" />
  </svg>
);

const AppleIcon = () => (
  <svg viewBox="0 0 384 512" className="w-5 h-5 fill-white">
    <path d="M318.7 268.7c-.2-36.7 16.4-64.4 50-84.8-18.8-26.9-47.2-41.7-84.7-44.6-35.5-2.8-74.3 20.7-88.5 20.7-15 0-49.4-19.7-76.4-19.7C63.3 141.2 4 184.8 4 273.5q0 39.3 14.4 81.2c12.8 36.7 59 126.7 107.2 125.2 25.2-.6 43-17.9 75.8-17.9 31.8 0 48.3 17.9 76.4 17.9 48.6-.7 90.4-82.5 102.6-119.3-65.2-30.7-61.7-90-61.7-91.9zm-56.6-164.2c27.3-32.4 24.8-61.9 24-72.5-24.1 1.4-52 16.4-67.9 34.9-17.5 19.8-27.8 44.3-25.6 71.9 26.1 2 49.9-11.4 69.5-34.3z" />
  </svg>
);

function RegisterPageContent() {
  const { register, verifyRegisterOtp } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const planFromUrl = searchParams.get("plan");

  const [form, setForm] = useState({ full_name: "", email: "", password: "", confirm_password: "" });
  const [otp, setOtp] = useState("");
  const [step, setStep] = useState<"register" | "verify">("register");
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (form.password !== form.confirm_password) {
      toast.error("Passwords do not match");
      return;
    }
    if (form.password.length < 8) {
      toast.error("Password must be at least 8 characters");
      return;
    }
    setLoading(true);
    try {
      await register(form.email, form.password, form.full_name);
      toast.success("Account details saved! Check your email for the verification code.");
      setStep("verify");
    } catch (err: any) {
      toast.error(getErrorMessage(err, "Registration failed"));
    } finally {
      setLoading(false);
    }
  };

  const handleVerifySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await verifyRegisterOtp(form.email, otp, {
        password: form.password,
        full_name: form.full_name
      });
      toast.success("Account verified! Let's set up your profile.");
      
      const interval = searchParams.get("interval") || "monthly";
      const onboardingUrl = planFromUrl 
        ? `/onboarding?plan=${planFromUrl}&interval=${interval}`
        : "/onboarding";
      router.push(onboardingUrl);
    } catch (err: any) {
      toast.error(getErrorMessage(err, "Invalid or expired OTP"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-black relative overflow-hidden">
      
      {/* --- BACKGROUND EFFECTS --- */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute inset-0 bg-black" />
        {mounted && (
          <div className="absolute inset-0">
            {[...Array(40)].map((_, i) => (
              <div 
                key={i}
                className="absolute bg-white rounded-full"
                style={{
                  top: `${Math.random() * 100}%`,
                  left: `${Math.random() * 100}%`,
                  width: `${Math.random() * 2 + 1}px`,
                  height: `${Math.random() * 2 + 1}px`,
                  opacity: Math.random() * 0.4 + 0.1,
                  filter: `blur(${Math.random() * 0.5}px)`
                }}
              />
            ))}
          </div>
        )}
        <div 
          className="absolute inset-0 opacity-[0.015]"
          style={{
            backgroundImage: "linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px)",
            backgroundSize: "80px 80px"
          }}
        />
      </div>

      {/* --- AUTH CARD --- */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="w-full max-w-[400px] p-6 relative z-10"
      >
        <div className="relative group p-[1px] rounded-[2.5rem] bg-gradient-to-b from-white/[0.10] to-transparent shadow-[0_32px_128px_-16px_rgba(0,0,0,0.8)] backdrop-blur-2xl">
          <div className="bg-[#242424]/95 rounded-[2.5rem] p-6 space-y-6 overflow-hidden relative border border-white/[0.07]">
            <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/25 to-transparent pointer-events-none" />
            
            <div className="space-y-4 relative z-10 text-center flex flex-col items-center">
              <Link href="/" className="flex flex-col items-center gap-3 group/logo-link">
                <div className="w-16 h-16 rounded-[1.2rem] border border-white/10 flex items-center justify-center group/logo overflow-hidden relative shadow-2xl">
                  <div 
                    className="absolute inset-0 opacity-100 bg-[#111115]" 
                    style={{ 
                      backgroundImage: "radial-gradient(circle, #000 35%, rgba(255,255,255,0.08) 42%, transparent 50%)",
                      backgroundSize: "10px 10px"
                    }} 
                  />
                  <img src="/logo.png" alt="Logo" className="absolute inset-0 w-full h-full scale-[2.0] object-contain invert brightness-[200%] mix-blend-screen" />
                </div>
                <span className="text-2xl font-extrabold font-display tracking-tight text-white">Applivo</span>
              </Link>
              <div className="space-y-1 text-center">
                <h1 className="text-xl font-semibold text-white tracking-tight">
                  {step === "register" ? "Create your account" : "Verify Email"}
                </h1>
                <p className="text-[#A1A1AA] text-sm font-medium">
                  {step === "register" 
                    ? (planFromUrl ? `You selected the ${planFromUrl} plan` : "Start your automated job search")
                    : "Enter the code sent to " + form.email}
                </p>
              </div>
            </div>

            {step === "register" ? (
              <form onSubmit={handleRegisterSubmit} className="space-y-4 relative z-10 text-left">
                <div className="space-y-2">
                  <label className="text-xs font-semibold text-[#A1A1AA] uppercase tracking-widest pl-1">Full Name</label>
                  <input
                    type="text"
                    value={form.full_name}
                    onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                    required
                    className="w-full bg-[#1d1d1d] border border-[#1C1C24] rounded-xl px-4 py-3 text-white focus:outline-none focus:border-white/35 transition-all placeholder:text-[#6B7280]"
                    placeholder="Your Name"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-semibold text-[#A1A1AA] uppercase tracking-widest pl-1">Email</label>
                  <input
                    type="email"
                    value={form.email}
                    onChange={(e) => setForm({ ...form, email: e.target.value })}
                    required
                    className="w-full bg-[#1d1d1d] border border-[#1C1C24] rounded-xl px-4 py-3 text-white focus:outline-none focus:border-white/35 transition-all placeholder:text-[#6B7280]"
                    placeholder="you@example.com"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-xs font-semibold text-[#A1A1AA] uppercase tracking-widest pl-1">Password</label>
                    <div className="relative">
                      <input
                        type={showPass ? "text" : "password"}
                        value={form.password}
                        onChange={(e) => setForm({ ...form, password: e.target.value })}
                        required
                        className="w-full bg-[#1d1d1d] border border-[#1C1C24] rounded-xl px-4 py-3 text-white focus:outline-none focus:border-white/35 transition-all pr-12"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPass(!showPass)}
                        className="absolute right-4 top-1/2 -translate-y-1/2 text-[#A1A1AA] hover:text-white"
                      >
                        {showPass ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-semibold text-[#A1A1AA] uppercase tracking-widest pl-1">Confirm</label>
                    <input
                      type="password"
                      value={form.confirm_password}
                      onChange={(e) => setForm({ ...form, confirm_password: e.target.value })}
                      required
                      className="w-full bg-[#1d1d1d] border border-[#1C1C24] rounded-xl px-4 py-3 text-white focus:outline-none focus:border-white/35 transition-all pl-4"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-white text-black py-3 rounded-xl font-bold transition-all hover:bg-zinc-200 active:scale-[0.98] flex items-center justify-center gap-2"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Continue"}
                </button>
              </form>
            ) : (
              <form onSubmit={handleVerifySubmit} className="space-y-4 relative z-10 text-left">
                <div className="space-y-4">
                  <label className="text-xs font-semibold text-[#A1A1AA] uppercase tracking-widest pl-1 text-center block">Verification Code</label>
                  <input
                    type="text"
                    value={otp}
                    onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    required
                    autoFocus
                    className="w-full bg-[#1d1d1d] border border-[#1C1C24] rounded-xl px-4 py-3 text-white text-center text-2xl font-mono tracking-[0.35em] focus:outline-none focus:border-white/35 transition-all placeholder:text-white/70"
                    placeholder="000000"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading || otp.length < 6}
                  className="w-full bg-white text-black py-3 rounded-xl font-bold transition-all hover:bg-zinc-200 disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Verify & Create Account"}
                </button>

                <div className="text-center pt-2">
                  <button 
                    type="button"
                    onClick={() => setStep("register")}
                    className="text-sm text-[#A1A1AA] hover:text-white transition-colors"
                  >
                    Back to registration
                  </button>
                </div>
              </form>
            )}

            {/* Footer */}
            <div className="space-y-4 pt-2 relative z-10 text-center">
              <p className="text-sm text-[#A1A1AA]">
                Already have an account?{" "}
                <Link href="/login" className="text-white hover:underline font-medium">Sign in</Link>
              </p>
            </div>
          </div>
        </div>
      </motion.div>
    </main>
  );
}

export default function RegisterPage() {
  return (
    <Suspense fallback={null}>
      <RegisterPageContent />
    </Suspense>
  );
}
