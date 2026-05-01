"use client";
import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { Eye, EyeOff, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
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

export default function LoginPage() {
  const { login, verifyLoginOtp } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [otp, setOtp] = useState("");
  const [step, setStep] = useState<"login" | "verify">("login");
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loading) return;
    setLoading(true);
    setError(false);
    try {
      await login(email, password);
      toast.success("Credentials valid! Please check your email for the OTP.");
      setStep("verify");
    } catch (err: any) {
      setError(true);
      toast.error(getErrorMessage(err, "Authentication failed"));
    } finally {
      setLoading(false);
    }
  };

  const handleVerifySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loading) return;
    setLoading(true);
    try {
      await verifyLoginOtp(email, otp);
      toast.success("Welcome back!");
      router.push("/dashboard");
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
        className="w-full max-w-[380px] p-6 relative z-10"
      >
        <div className="relative group p-[1px] rounded-[2.5rem] bg-gradient-to-b from-white/[0.10] to-transparent shadow-[0_32px_128px_-16px_rgba(0,0,0,0.8)] backdrop-blur-2xl">
          <div className="bg-[#242424]/95 rounded-[2.5rem] p-6 space-y-6 overflow-hidden relative border border-white/[0.07]">
            <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/25 to-transparent pointer-events-none" />
            
            <div className="space-y-4 relative z-10 text-center flex flex-col items-center">
              <Link href="/" className="flex flex-col items-center gap-4 group/logo-link">
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
                <div className="space-y-1">
                  <h1 className="text-2xl font-bold text-white tracking-tight">
                    {step === "login" ? "Welcome Back" : "Security Check"}
                  </h1>
                  <p className="text-[#A1A1AA] text-sm font-medium">
                    {step === "login" ? "AI-powered job automation platform" : "Enter the verification code sent to your email"}
                  </p>
                </div>
              </Link>
            </div>

            <AnimatePresence mode="wait">
              {step === "login" ? (
                <motion.form 
                  key="login-form"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  onSubmit={handleLoginSubmit} 
                  className="space-y-4 relative z-10"
                >
                  <div className="space-y-2">
                    <label className="text-xs font-semibold text-[#A1A1AA] uppercase tracking-widest pl-1">Email</label>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => { setEmail(e.target.value); setError(false); }}
                      required
                      className={cn(
                        "w-full bg-[#1d1d1d] border rounded-xl px-4 py-3 text-white focus:outline-none focus:border-white/35 transition-all placeholder:text-[#6B7280]",
                        error ? "border-red-500" : "border-[#1C1C24]"
                      )}
                      placeholder="you@example.com"
                    />
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between items-center pl-1">
                      <label className="text-xs font-semibold text-[#A1A1AA] uppercase tracking-widest">Password</label>
                      <Link href="/forgot-password" core-link="true" className="text-xs text-[#6B7280] hover:text-white">Forgot password?</Link>
                    </div>
                    <div className="relative">
                      <input
                        type={showPass ? "text" : "password"}
                        value={password}
                        onChange={(e) => { setPassword(e.target.value); setError(false); }}
                        required
                        className={cn(
                          "w-full bg-[#1d1d1d] border rounded-xl px-4 py-3 text-white focus:outline-none focus:border-white/35 transition-all pr-12",
                          error ? "border-red-500" : "border-[#1C1C24]"
                        )}
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

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-white text-black py-3 rounded-xl font-bold transition-all hover:bg-zinc-200 active:scale-[0.98] flex items-center justify-center gap-2 shadow-xl"
                  >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Continue"}
                  </button>
                </motion.form>
              ) : (
                <motion.form 
                  key="verify-form"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  onSubmit={handleVerifySubmit} 
                  className="space-y-4 relative z-10"
                >
                  <div className="space-y-4">
                    <label className="text-xs font-semibold text-[#A1A1AA] uppercase tracking-widest pl-1 text-center block">Verification Code</label>
                    <input
                      type="text"
                      value={otp}
                      onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                      required
                      autoFocus
                      className="w-full bg-[#1d1d1d] border border-[#2c2c30] rounded-xl px-4 py-3 text-white text-center text-2xl font-mono tracking-[0.35em] focus:outline-none focus:border-white/35 transition-all placeholder:text-white/70"
                      placeholder="000000"
                    />
                    <p className="text-xs text-[#6B7280] text-center">
                      We sent a 6-digit code to <span className="text-white font-medium">{email}</span>
                    </p>
                  </div>

                  <button
                    type="submit"
                    disabled={loading || otp.length < 6}
                    className="w-full bg-white text-black py-3 rounded-xl font-bold transition-all hover:bg-zinc-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Verify & Login"}
                  </button>

                  <div className="text-center pt-2">
                    <button 
                      type="button"
                      onClick={() => setStep("login")}
                      className="text-sm text-[#A1A1AA] hover:text-white transition-colors"
                    >
                      Back to login
                    </button>
                  </div>
                </motion.form>
              )}
            </AnimatePresence>

            <div className="text-center pt-2 relative z-10">
              <p className="text-sm text-[#A1A1AA]">
                Don&apos;t have an account?{" "}
                <Link href="/register" className="text-white hover:underline font-medium">Sign up</Link>
              </p>
            </div>
          </div>
        </div>
      </motion.div>
    </main>
  );
}
