"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { onboardingApi, resumesApi } from "@/lib/api";
import { toast } from "sonner";
import { Zap, ChevronRight, ChevronLeft, Check, Upload, Plus, X } from "lucide-react";
import { useDropzone } from "react-dropzone";

const STEPS = [
  "Basic Info", "Contact", "Education", "Experience",
  "Skills", "Resume", "Job Preferences", "Automation",
];

interface SkillEntry {
  name: string;
  category: string;
  proficiency: string;
  years_experience: number;
  is_primary: boolean;
}

interface EduEntry {
  degree: string;
  field: string;
  institution: string;
  graduation_year: string;
  gpa: string;
}

interface ExpEntry {
  title: string;
  company: string;
  start_date: string;
  end_date: string;
  is_current: boolean;
  description: string;
}

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);

  // Step 1
  const [basic, setBasic] = useState({ full_name: "", professional_summary: "", career_goals: "", unique_value_proposition: "" });
  // Step 2
  const [contact, setContact] = useState({ phone: "", location: "", linkedin_url: "", github_url: "", portfolio_url: "", notification_email: "" });
  // Step 3
  const [education, setEducation] = useState<EduEntry[]>([{ degree: "", field: "", institution: "", graduation_year: "", gpa: "" }]);
  // Step 4
  const [experience, setExperience] = useState<ExpEntry[]>([{ title: "", company: "", start_date: "", end_date: "", is_current: false, description: "" }]);
  // Step 5
  const [skills, setSkills] = useState<SkillEntry[]>([{ name: "", category: "programming", proficiency: "intermediate", years_experience: 1, is_primary: false }]);
  // Step 6
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  // Step 7
  const [jobPrefs, setJobPrefs] = useState({ desired_roles: "", desired_locations: "", open_to_remote: true, open_to_hybrid: true, min_salary: 0, preferred_industries: "" });
  // Step 8
  const [automation, setAutomation] = useState({ auto_apply_enabled: false, auto_apply_threshold: 75, auto_apply_daily_limit: 10, require_apply_approval: true, notify_via_email: true, notify_via_telegram: false, telegram_chat_id: "" });

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { "application/pdf": [".pdf"] },
    maxFiles: 1,
    onDrop: (files) => setResumeFile(files[0] || null),
  });

  const next = () => setStep((s) => Math.min(s + 1, STEPS.length - 1));
  const prev = () => setStep((s) => Math.max(s - 1, 0));

  const submit = async () => {
    setLoading(true);
    try {
      const stepEndpoints: Record<number, [string, Record<string, unknown>]> = {
        0: ["basic-info", basic],
        1: ["contact-info", contact],
        2: ["education", { education }],
        3: ["work-experience", { work_experience: experience }],
        4: ["skills", { skills }],
        6: ["job-preferences", {
          desired_roles: jobPrefs.desired_roles.split(",").map((r) => r.trim()).filter(Boolean),
          desired_locations: jobPrefs.desired_locations.split(",").map((l) => l.trim()).filter(Boolean),
          open_to_remote: jobPrefs.open_to_remote,
          open_to_hybrid: jobPrefs.open_to_hybrid,
          min_salary: jobPrefs.min_salary,
          preferred_industries: jobPrefs.preferred_industries.split(",").map((i) => i.trim()).filter(Boolean),
        }],
        7: ["platform-setup", automation],
      };

      const endpoint = stepEndpoints[step];
      if (endpoint) {
        await onboardingApi.complete(endpoint[0], endpoint[1]);
      }

      // Step 5 is resume upload
      if (step === 5 && resumeFile) {
        const fd = new FormData();
        fd.append("file", resumeFile);
        fd.append("name", resumeFile.name.replace(".pdf", ""));
        await resumesApi.upload(fd);
      }

      if (step === STEPS.length - 1) {
        toast.success("Profile complete! Welcome to Applivo 🚀");
        router.push("/dashboard");
      } else {
        next();
      }
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? "Error saving this step");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background animated-gradient grid-pattern flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-4">
            <img src="/logo.JPG" alt="Applivo" className="w-8 h-8 rounded-lg" />
            <span className="text-xl font-bold font-display gradient-text">Applivo</span>
          </div>
          <h1 className="text-2xl font-bold mb-1">Set up your profile</h1>
          <p className="text-muted-foreground text-sm">Step {step + 1} of {STEPS.length} — {STEPS[step]}</p>
        </div>

        {/* Progress */}
        <div className="flex gap-1.5 mb-8">
          {STEPS.map((_, i) => (
            <div
              key={i}
              className={`flex-1 h-1.5 rounded-full transition-all duration-300 ${
                i <= step ? "bg-brand-purple" : "bg-muted"
              }`}
            />
          ))}
        </div>

        {/* Step content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.25 }}
            className="glass-card p-8"
          >
            {/* STEP 0 — Basic Info */}
            {step === 0 && (
              <div className="space-y-5">
                <h2 className="text-lg font-semibold">Tell us about yourself</h2>
                {[
                  { key: "full_name", label: "Full Name", ph: "Your full name" },
                  { key: "professional_summary", label: "Professional Summary", ph: "2-3 sentences about your expertise…", type: "textarea" },
                  { key: "career_goals", label: "Career Goals", ph: "What are you aiming for?", type: "textarea" },
                  { key: "unique_value_proposition", label: "Unique Value Proposition", ph: "What makes you stand out?", type: "textarea" },
                ].map((f) => (
                  <div key={f.key}>
                    <label className="block text-sm font-medium mb-2">{f.label}</label>
                    {f.type === "textarea" ? (
                      <textarea
                        rows={3}
                        value={(basic as any)[f.key]}
                        onChange={(e) => setBasic({ ...basic, [f.key]: e.target.value })}
                        className="w-full px-4 py-3 bg-muted border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-purple/50 resize-none"
                        placeholder={f.ph}
                      />
                    ) : (
                      <input
                        type="text"
                        value={(basic as any)[f.key]}
                        onChange={(e) => setBasic({ ...basic, [f.key]: e.target.value })}
                        className="w-full px-4 py-3 bg-muted border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-purple/50"
                        placeholder={f.ph}
                      />
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* STEP 1 — Contact */}
            {step === 1 && (
              <div className="space-y-5">
                <h2 className="text-lg font-semibold">Contact information</h2>
                <div className="grid grid-cols-2 gap-4">
                  {[
                    { key: "phone", label: "Phone", ph: "+91 xxxxxxxxxx" },
                    { key: "location", label: "Location", ph: "Chennai, India" },
                    { key: "linkedin_url", label: "LinkedIn URL", ph: "https://linkedin.com/in/…" },
                    { key: "github_url", label: "GitHub URL", ph: "https://github.com/…" },
                    { key: "portfolio_url", label: "Portfolio URL", ph: "https://yoursite.com" },
                    { key: "notification_email", label: "Notification Email", ph: "your@email.com" },
                  ].map((f) => (
                    <div key={f.key} className="col-span-2 sm:col-span-1">
                      <label className="block text-sm font-medium mb-2">{f.label}</label>
                      <input
                        type="text"
                        value={(contact as any)[f.key]}
                        onChange={(e) => setContact({ ...contact, [f.key]: e.target.value })}
                        className="w-full px-4 py-3 bg-muted border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-purple/50"
                        placeholder={f.ph}
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* STEP 2 — Education */}
            {step === 2 && (
              <div className="space-y-5">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold">Education</h2>
                  <button onClick={() => setEducation([...education, { degree: "", field: "", institution: "", graduation_year: "", gpa: "" }])}
                    className="flex items-center gap-1 text-sm text-brand-purple-light hover:text-brand-purple transition-colors">
                    <Plus className="w-4 h-4" /> Add
                  </button>
                </div>
                {education.map((edu, i) => (
                  <div key={i} className="p-4 bg-muted/50 rounded-lg space-y-3 relative">
                    {education.length > 1 && (
                      <button onClick={() => setEducation(education.filter((_, idx) => idx !== i))}
                        className="absolute top-3 right-3 text-muted-foreground hover:text-red-400">
                        <X className="w-4 h-4" />
                      </button>
                    )}
                    <div className="grid grid-cols-2 gap-3">
                      {[["degree", "Degree", "B.Tech", 1], ["field", "Field", "Computer Science", 1], ["institution", "Institution", "IIT Madras", 2], ["graduation_year", "Grad Year", "2025", 1], ["gpa", "GPA", "8.5", 1]].map(([key, label, ph, cols]) => (
                        <div key={key as string} className={`col-span-${cols}`}>
                          <label className="block text-xs font-medium mb-1 text-muted-foreground">{label as string}</label>
                          <input type="text" value={(edu as any)[key as string]} onChange={(e) => { const ne = [...education]; (ne[i] as any)[key as string] = e.target.value; setEducation(ne); }}
                            className="w-full px-3 py-2 bg-muted border border-border rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-brand-purple/50"
                            placeholder={ph as string} />
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* STEP 3 — Experience */}
            {step === 3 && (
              <div className="space-y-5">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold">Work Experience</h2>
                  <button onClick={() => setExperience([...experience, { title: "", company: "", start_date: "", end_date: "", is_current: false, description: "" }])}
                    className="flex items-center gap-1 text-sm text-brand-purple-light hover:text-brand-purple transition-colors">
                    <Plus className="w-4 h-4" /> Add
                  </button>
                </div>
                {experience.map((exp, i) => (
                  <div key={i} className="p-4 bg-muted/50 rounded-lg space-y-3 relative">
                    {experience.length > 1 && (
                      <button onClick={() => setExperience(experience.filter((_, idx) => idx !== i))}
                        className="absolute top-3 right-3 text-muted-foreground hover:text-red-400">
                        <X className="w-4 h-4" />
                      </button>
                    )}
                    <div className="grid grid-cols-2 gap-3">
                      {[["title", "Job Title", "ML Engineer"], ["company", "Company", "Google"]].map(([key, label, ph]) => (
                        <div key={key}>
                          <label className="block text-xs font-medium mb-1 text-muted-foreground">{label}</label>
                          <input type="text" value={(exp as any)[key]} onChange={(e) => { const ne = [...experience]; (ne[i] as any)[key] = e.target.value; setExperience(ne); }}
                            className="w-full px-3 py-2 bg-muted border border-border rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-brand-purple/50" placeholder={ph} />
                        </div>
                      ))}
                      <div>
                        <label className="block text-xs font-medium mb-1 text-muted-foreground">Start Date</label>
                        <input type="month" value={exp.start_date} onChange={(e) => { const ne = [...experience]; ne[i].start_date = e.target.value; setExperience(ne); }}
                          className="w-full px-3 py-2 bg-muted border border-border rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-brand-purple/50" />
                      </div>
                      <div>
                        <label className="block text-xs font-medium mb-1 text-muted-foreground">End Date</label>
                        <input type="month" value={exp.end_date} disabled={exp.is_current} onChange={(e) => { const ne = [...experience]; ne[i].end_date = e.target.value; setExperience(ne); }}
                          className="w-full px-3 py-2 bg-muted border border-border rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-brand-purple/50 disabled:opacity-40" />
                        <label className="flex items-center gap-2 mt-1 text-xs text-muted-foreground cursor-pointer">
                          <input type="checkbox" checked={exp.is_current} onChange={(e) => { const ne = [...experience]; ne[i].is_current = e.target.checked; setExperience(ne); }} />
                          Current role
                        </label>
                      </div>
                    </div>
                    <div>
                      <label className="block text-xs font-medium mb-1 text-muted-foreground">Description</label>
                      <textarea rows={3} value={exp.description} onChange={(e) => { const ne = [...experience]; ne[i].description = e.target.value; setExperience(ne); }}
                        className="w-full px-3 py-2 bg-muted border border-border rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-brand-purple/50 resize-none"
                        placeholder="Key achievements and responsibilities…" />
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* STEP 4 — Skills */}
            {step === 4 && (
              <div className="space-y-5">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold">Skills</h2>
                  <button onClick={() => setSkills([...skills, { name: "", category: "programming", proficiency: "intermediate", years_experience: 1, is_primary: false }])}
                    className="flex items-center gap-1 text-sm text-brand-purple-light hover:text-brand-purple transition-colors">
                    <Plus className="w-4 h-4" /> Add skill
                  </button>
                </div>
                <div className="space-y-3">
                  {skills.map((sk, i) => (
                    <div key={i} className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg">
                      <input type="text" value={sk.name} onChange={(e) => { const ns = [...skills]; ns[i].name = e.target.value; setSkills(ns); }}
                        placeholder="Python" className="flex-1 px-3 py-2 bg-muted border border-border rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-brand-purple/50" />
                      <select value={sk.category} onChange={(e) => { const ns = [...skills]; ns[i].category = e.target.value; setSkills(ns); }}
                        className="px-3 py-2 bg-muted border border-border rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-brand-purple/50">
                        {["programming", "ml_framework", "cloud", "tool", "soft_skill"].map((c) => <option key={c} value={c}>{c}</option>)}
                      </select>
                      <select value={sk.proficiency} onChange={(e) => { const ns = [...skills]; ns[i].proficiency = e.target.value; setSkills(ns); }}
                        className="px-3 py-2 bg-muted border border-border rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-brand-purple/50">
                        {["beginner", "intermediate", "advanced", "expert"].map((p) => <option key={p} value={p}>{p}</option>)}
                      </select>
                      <input type="number" min={0} max={20} value={sk.years_experience} onChange={(e) => { const ns = [...skills]; ns[i].years_experience = +e.target.value; setSkills(ns); }}
                        className="w-16 px-3 py-2 bg-muted border border-border rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-brand-purple/50" />
                      {skills.length > 1 && (
                        <button onClick={() => setSkills(skills.filter((_, idx) => idx !== i))} className="text-muted-foreground hover:text-red-400">
                          <X className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* STEP 5 — Resume Upload */}
            {step === 5 && (
              <div className="space-y-5">
                <h2 className="text-lg font-semibold">Upload your resume</h2>
                <div {...getRootProps()} className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all ${isDragActive ? "border-brand-purple bg-brand-purple/10" : "border-border hover:border-brand-purple/50 hover:bg-white/3"}`}>
                  <input {...getInputProps()} />
                  <Upload className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
                  {resumeFile ? (
                    <p className="text-brand-green font-medium">{resumeFile.name}</p>
                  ) : (
                    <>
                      <p className="text-sm font-medium mb-1">Drag & drop your PDF resume</p>
                      <p className="text-xs text-muted-foreground">or click to browse files</p>
                    </>
                  )}
                </div>
                <p className="text-xs text-muted-foreground text-center">PDF only · Max 10MB · This will be used as your base resume for AI tailoring</p>
              </div>
            )}

            {/* STEP 6 — Job Preferences */}
            {step === 6 && (
              <div className="space-y-5">
                <h2 className="text-lg font-semibold">Job preferences</h2>
                {[
                  { key: "desired_roles", label: "Desired Roles", ph: "ML Engineer, Data Scientist, AI Researcher (comma separated)" },
                  { key: "desired_locations", label: "Desired Locations", ph: "Remote, Bangalore, Chennai (comma separated)" },
                  { key: "preferred_industries", label: "Preferred Industries", ph: "Tech, AI, Finance (comma separated)" },
                ].map((f) => (
                  <div key={f.key}>
                    <label className="block text-sm font-medium mb-2">{f.label}</label>
                    <input type="text" value={(jobPrefs as any)[f.key]} onChange={(e) => setJobPrefs({ ...jobPrefs, [f.key]: e.target.value })}
                      className="w-full px-4 py-3 bg-muted border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-purple/50"
                      placeholder={f.ph} />
                  </div>
                ))}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Min Salary (₹/year)</label>
                    <input type="number" value={jobPrefs.min_salary} onChange={(e) => setJobPrefs({ ...jobPrefs, min_salary: +e.target.value })}
                      className="w-full px-4 py-3 bg-muted border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-purple/50" />
                  </div>
                  <div className="space-y-3 flex flex-col justify-end pb-1">
                    {[["open_to_remote", "Open to Remote"], ["open_to_hybrid", "Open to Hybrid"]].map(([key, label]) => (
                      <label key={key} className="flex items-center gap-3 cursor-pointer">
                        <input type="checkbox" checked={(jobPrefs as any)[key]} onChange={(e) => setJobPrefs({ ...jobPrefs, [key]: e.target.checked })}
                          className="w-4 h-4 accent-brand-purple" />
                        <span className="text-sm">{label}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* STEP 7 — Automation */}
            {step === 7 && (
              <div className="space-y-6">
                <h2 className="text-lg font-semibold">Automation settings</h2>

                <label className="flex items-center justify-between p-4 bg-muted/50 rounded-lg cursor-pointer">
                  <div>
                    <p className="font-medium text-sm">Enable Auto-Apply</p>
                    <p className="text-xs text-muted-foreground mt-0.5">Let the bot apply on your behalf automatically</p>
                  </div>
                  <div className={`w-12 h-6 rounded-full transition-colors ${automation.auto_apply_enabled ? "bg-brand-purple" : "bg-muted"} relative cursor-pointer`}
                    onClick={() => setAutomation({ ...automation, auto_apply_enabled: !automation.auto_apply_enabled })}>
                    <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${automation.auto_apply_enabled ? "left-7" : "left-1"}`} />
                  </div>
                </label>

                <div>
                  <div className="flex justify-between mb-2">
                    <label className="text-sm font-medium">Match Threshold</label>
                    <span className="text-sm text-brand-purple-light font-semibold">{automation.auto_apply_threshold}%</span>
                  </div>
                  <input type="range" min={0} max={100} value={automation.auto_apply_threshold}
                    onChange={(e) => setAutomation({ ...automation, auto_apply_threshold: +e.target.value })}
                    className="w-full accent-brand-purple" />
                  <p className="text-xs text-muted-foreground mt-1">Only apply to jobs scoring above this threshold</p>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Daily Application Limit</label>
                  <input type="number" min={1} max={50} value={automation.auto_apply_daily_limit}
                    onChange={(e) => setAutomation({ ...automation, auto_apply_daily_limit: +e.target.value })}
                    className="w-full px-4 py-3 bg-muted border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-purple/50" />
                </div>

                <label className="flex items-center gap-3 cursor-pointer">
                  <input type="checkbox" checked={automation.require_apply_approval}
                    onChange={(e) => setAutomation({ ...automation, require_apply_approval: e.target.checked })}
                    className="w-4 h-4 accent-brand-purple" />
                  <div>
                    <p className="text-sm font-medium">Require Telegram approval before applying</p>
                    <p className="text-xs text-muted-foreground">Recommended — you approve each application via Telegram</p>
                  </div>
                </label>

                {automation.require_apply_approval && (
                  <div>
                    <label className="block text-sm font-medium mb-2">Telegram Chat ID</label>
                    <input type="text" value={automation.telegram_chat_id}
                      onChange={(e) => setAutomation({ ...automation, telegram_chat_id: e.target.value })}
                      className="w-full px-4 py-3 bg-muted border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-purple/50"
                      placeholder="Get from @userinfobot on Telegram" />
                  </div>
                )}

                <div className="p-4 bg-brand-purple/10 border border-brand-purple/30 rounded-lg text-sm text-brand-purple-light">
                  🎉 Almost done! Click "Complete Setup" to finish and access your dashboard.
                </div>
              </div>
            )}
          </motion.div>
        </AnimatePresence>

        {/* Navigation */}
        <div className="flex justify-between mt-6">
          <button onClick={prev} disabled={step === 0}
            className="flex items-center gap-2 px-5 py-2.5 rounded-lg border border-border text-sm hover:bg-white/5 transition-colors disabled:opacity-30 disabled:cursor-not-allowed">
            <ChevronLeft className="w-4 h-4" /> Back
          </button>
          <button onClick={submit} disabled={loading}
            className="flex items-center gap-2 px-6 py-2.5 bg-brand-purple text-white rounded-lg font-semibold text-sm hover:bg-brand-purple/90 transition-all hover:shadow-lg hover:shadow-brand-purple/30 disabled:opacity-50 disabled:cursor-not-allowed">
            {loading ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : step === STEPS.length - 1 ? (
              <><Check className="w-4 h-4" /> Complete Setup</>
            ) : (
              <>Next <ChevronRight className="w-4 h-4" /></>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
