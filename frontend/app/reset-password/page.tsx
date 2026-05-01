"use client";
import React, { useState, Suspense, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { authApi } from "@/lib/api";
import { Eye, EyeOff, Loader2, ArrowLeft, ShieldCheck } from "lucide-react";
import { motion } from "framer-motion";
import { toast } from "sonner";

function ResetPasswordPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (!token) {
      toast.error("Invalid reset link. No token found.");
    }
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }
    if (password.length < 8) {
      toast.error("Password must be at least 8 characters");
      return;
    }
    if (!token) {
      toast.error("Missing reset token. Please request a new link.");
      return;
    }

    setLoading(true);
    try {
      await authApi.resetPassword({ token, new_password: password });
      setSuccess(true);
      toast.success("Password reset successfully!");
      setTimeout(() => router.push("/login"), 3000);
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      toast.error(typeof detail === "string" ? detail : "Failed to reset password. Link may be expired.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-[#07080D] relative overflow-hidden">
      
      {/* --- BACKGROUND EFFECTS --- */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute inset-0 bg-[#07080D]" />
        <div 
          className="absolute -top-[20%] -left-[10%] w-[70%] h-[70%] rounded-full opacity-20 blur-[120px]"
          style={{ background: "radial-gradient(circle, rgba(79, 70, 229, 0.4) 0%, transparent 70%)" }}
        />
        <div 
          className="absolute -bottom-[20%] left-1/2 -translate-x-1/2 w-[80%] h-[60%] rounded-full opacity-[0.07] blur-[120px]"
          style={{ background: "radial-gradient(circle, rgba(99, 102, 241, 0.3) 0%, transparent 70%)" }}
        />
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
        <div className="relative group p-[1px] rounded-[2.5rem] bg-gradient-to-b from-white/[0.12] to-transparent shadow-[0_32px_128px_-16px_rgba(0,0,0,0.8)] backdrop-blur-2xl">
          <div className="bg-[#0B0C10]/95 rounded-[2.5rem] p-6 space-y-6 overflow-hidden relative border border-white/[0.02]">
            <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-indigo-500/40 to-transparent pointer-events-none" />
            
            <div className="space-y-4 relative z-10 text-center flex flex-col items-center">
              <Link href="/login" className="flex flex-col items-center gap-3 group/logo-link">
                <div className="w-16 h-16 rounded-[1.2rem] border border-white/10 flex items-center justify-center group/logo overflow-hidden relative shadow-2xl">
                  <div 
                    className="absolute inset-0 opacity-100 bg-[#111115]" 
                    style={{ 
                      backgroundImage: "radial-gradient(circle, #000 35%, rgba(255,255,255,0.08) 42%, transparent 50%)",
                      backgroundSize: "10px 10px"
                    }} 
                  />
                  <div className="absolute inset-0 shadow-[inset_0_4px_12px_rgba(0,0,0,0.6)] pointer-events-none" />
                  <img 
                    src="/logo.png" 
                    alt="Logo" 
                    className="absolute inset-0 w-full h-full scale-[2.0] object-contain group-hover/logo:scale-[2.1] transition-transform relative z-10 invert brightness-[200%] contrast-[150%] mix-blend-screen" 
                  />
                </div>
              </Link>
              
              {!success ? (
                <div className="space-y-1">
                  <h1 className="text-xl font-semibold text-white tracking-tight text-center">Reset Password</h1>
                  <p className="text-[#A1A1AA] text-sm font-medium text-center">Please enter your new password below.</p>
                </div>
              ) : (
                <div className="space-y-1">
                  <div className="w-12 h-12 rounded-full bg-emerald-500/10 flex items-center justify-center mx-auto mb-4 border border-emerald-500/20 text-emerald-400">
                    <ShieldCheck className="w-6 h-6" />
                  </div>
                  <h1 className="text-xl font-semibold text-white tracking-tight text-center">Success!</h1>
                  <p className="text-[#A1A1AA] text-sm font-medium text-center">Your password has been reset. Redirecting to login...</p>
                </div>
              )}
            </div>

            {!success && (
              <form onSubmit={handleSubmit} className="space-y-4 relative z-10">
                <div className="space-y-2">
                  <label className="text-xs font-semibold text-[#A1A1AA] uppercase tracking-widest pl-1">New Password</label>
                  <div className="relative">
                    <input
                      type={showPass ? "text" : "password"}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      className="w-full bg-[#16171D] border border-[#1C1C24] rounded-xl px-4 py-3 text-white focus:outline-none focus:border-white transition-all placeholder:text-[#6B7280]"
                      placeholder=""
                    />
                    <button
                      type="button"
                      onClick={() => setShowPass(!showPass)}
                      className="absolute right-4 top-1/2 -translate-y-1/2 text-[#6B7280] hover:text-white transition-colors"
                    >
                      {showPass ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-semibold text-[#A1A1AA] uppercase tracking-widest pl-1">Confirm New Password</label>
                  <input
                    type={showPass ? "text" : "password"}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    className="w-full bg-[#16171D] border border-[#1C1C24] rounded-xl px-4 py-3 text-white focus:outline-none focus:border-white transition-all placeholder:text-[#6B7280]"
                    placeholder=""
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading || !token}
                  className="w-full bg-gradient-to-r from-[#1F2937] to-[#111827] border border-[#1F2937] text-white py-3 rounded-xl font-medium transition-all hover:brightness-110 active:scale-[0.98] flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Reset Password"}
                </button>
              </form>
            )}

            <div className="pt-2 relative z-10 text-center">
              <Link 
                href="/login" 
                className="inline-flex items-center gap-2 text-sm text-[#A1A1AA] hover:text-white transition-all font-medium"
              >
                <ArrowLeft className="w-4 h-4" />
                Back to sign in
              </Link>
            </div>
          </div>
        </div>
      </motion.div>
    </main>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={
        <div className="min-h-screen flex items-center justify-center bg-[#07080D]">
            <Loader2 className="w-8 h-8 animate-spin text-white/20" />
        </div>
    }>
      <ResetPasswordPageContent />
    </Suspense>
  );
}
