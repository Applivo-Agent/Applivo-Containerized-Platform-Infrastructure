"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { motion, AnimatePresence } from "framer-motion";
import { onboardingApi, resumesApi } from "@/lib/api";
import { UNIVERSAL_SKILLS } from "@/lib/skillRecommendations";
import { toast } from "sonner";
import { ChevronRight, ChevronLeft, Check, Upload, Plus, X , Loader2} from "lucide-react";
import { useDropzone } from "react-dropzone";

const STEPS = [
  "Basic Info", "Resume", "Education", "Experience",
  "Skills", "Contact", "Job Preferences", "Automation",
];

const SKILL_CATEGORIES = [
  "programming",
  "ml_framework",
  "cloud",
  "tool",
  "soft_skill",
];

interface SkillEntry {
  name: string;
  category?: string;
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

interface ParsedSkillObject {
  name?: string;
  skill?: string;
}

interface ParsedEducationItem {
  degree?: string;
  field?: string;
  institution?: string;
  university?: string;
  college?: string;
  grad_year?: string | number;
  graduation_year?: string | number;
  year?: string | number;
  passout_year?: string | number;
  gpa?: string | number;
}

interface ParsedWorkExperienceItem {
  title?: string;
  company?: string;
  start_date?: string;
  start?: string;
  from?: string;
  end_date?: string;
  end?: string;
  to?: string;
  is_current?: boolean;
  description?: string;
}

interface ParsedResumeData {
  success?: boolean;
  error?: string;
  name?: string;
  professional_summary?: string;
  career_goals?: string;
  unique_value_proposition?: string;
  phone?: string;
  email?: string;
  location?: string;
  linkedin_url?: string;
  github_url?: string;
  portfolio_url?: string;
  education?: ParsedEducationItem[];
  work_experience?: ParsedWorkExperienceItem[];
  skills?: Array<string | ParsedSkillObject>;
}

interface BasicForm {
  full_name: string;
  professional_summary: string;
  career_goals: string;
  unique_value_proposition: string;
}

interface ContactForm {
  phone: string;
  location: string;
  linkedin_url: string;
  github_url: string;
  portfolio_url: string;
  notification_email: string;
}

interface JobPreferencesForm {
  desired_roles: string;
  desired_locations: string;
  open_to_remote: boolean;
  open_to_hybrid: boolean;
  min_salary: number;
  preferred_industries: string;
}

interface ErrorWithResponse {
  response?: {
    data?: {
      detail?: unknown;
    };
  };
}

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const getErrorDetail = (err: unknown): unknown => {
    if (typeof err === "object" && err !== null && "response" in err) {
      return (err as ErrorWithResponse).response?.data?.detail;
    }
    return undefined;
  };

  // Parse resume and extract data
  const parseResumeFile = async (file: File) => {
    setIsParsingResume(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const { data: result } = await onboardingApi.parseResume(formData);
      
      if (result.success) {
        setParsedResume(result.data);
        setShowParsedData(true);
        toast.success("Resume parsed successfully! Review and edit the data below.");
      } else {
        toast.error(result.error || "Failed to parse resume");
      }
    } catch (err: unknown) {
      const errorDetail = getErrorDetail(err);
      const message = typeof errorDetail === "string" ? errorDetail : "Error parsing resume";
      toast.error(message);
    } finally {
      setIsParsingResume(false);
    }
  };

  // Apply parsed resume data to form fields
  const applyParsedData = () => {
    if (!parsedResume) return;

    const toYear = (value: unknown) => {
      if (value === null || value === undefined) return "";
      const text = String(value).trim();
      if (!text) return "";
      const m = text.match(/\b(19|20)\d{2}\b/);
      return m ? m[0] : "";
    };

    const normalizeMonthYear = (value: unknown) => {
      if (value === null || value === undefined) return "";
      const text = String(value).trim();
      if (!text) return "";

      const yyyymm = text.match(/\b((19|20)\d{2})[-/]([01]?\d)\b/);
      if (yyyymm) {
        const month = Number(yyyymm[3]);
        if (month >= 1 && month <= 12) return `${yyyymm[1]}-${String(month).padStart(2, "0")}`;
      }

      const mmyyyy = text.match(/\b([01]?\d)[-/]((19|20)\d{2})\b/);
      if (mmyyyy) {
        const month = Number(mmyyyy[1]);
        if (month >= 1 && month <= 12) return `${mmyyyy[2]}-${String(month).padStart(2, "0")}`;
      }

      const year = toYear(text);
      return year ? `${year}-01` : "";
    };

    const splitSkillText = (raw: string) => {
      return raw
        .split(/[\n;|•]+/)
        .flatMap((chunk) => {
          const trimmed = chunk.trim();
          if (!trimmed) return [];
          const withoutPrefix = trimmed.includes(":") ? trimmed.split(":", 2)[1] : trimmed;
          return withoutPrefix.split(",").map((s) => s.trim()).filter(Boolean);
        });
    };

    // Apply basic info
    if (parsedResume.name) {
      setBasic({
        ...basic,
        full_name: parsedResume.name || "",
        professional_summary: parsedResume.professional_summary || "",
        career_goals: parsedResume.career_goals || "",
        unique_value_proposition: parsedResume.unique_value_proposition || "",
      });
    }

    // Apply contact info
    if (parsedResume.phone || parsedResume.location || parsedResume.linkedin_url || parsedResume.github_url || parsedResume.portfolio_url) {
      setContact({
        ...contact,
        phone: parsedResume.phone || "",
        location: parsedResume.location || "",
        linkedin_url: parsedResume.linkedin_url || "",
        github_url: parsedResume.github_url || "",
        portfolio_url: parsedResume.portfolio_url || "",
      });
    }

    // Apply education
    if (parsedResume.education && parsedResume.education.length > 0) {
      const edu = parsedResume.education.map((e: ParsedEducationItem) => ({
        degree: e.degree || "",
        field: e.field || "",
        institution: e.institution || e.university || e.college || "",
        graduation_year: toYear(e.grad_year || e.graduation_year || e.year || e.passout_year),
        gpa: e.gpa ? e.gpa.toString() : "",
      }));
      setEducation(edu);
    }

    // Apply work experience
    if (parsedResume.work_experience && parsedResume.work_experience.length > 0) {
      const exp = parsedResume.work_experience.map((e: ParsedWorkExperienceItem) => ({
        title: e.title || "",
        company: e.company || "",
        start_date: normalizeMonthYear(e.start_date || e.start || e.from),
        end_date: normalizeMonthYear(e.end_date || e.end || e.to),
        is_current: !!e.is_current || /present|current|ongoing|now/i.test(String(e.end_date || e.end || e.to || "")),
        description: e.description || "",
      }));
      setExperience(exp);
    }

    // Apply skills
    if (parsedResume.skills && parsedResume.skills.length > 0) {
      const rawSkills = parsedResume.skills.flatMap((s: string | ParsedSkillObject) => {
        if (typeof s === "string") return splitSkillText(s);
        const name = (s?.name || s?.skill || "").trim();
        if (!name) return [];
        return splitSkillText(name);
      });

      const deduped: string[] = Array.from(new Set(rawSkills.map((s: string) => s.trim()).filter(Boolean)));
      const sk = deduped.map((name) => ({
        name,
        category: "tool",
        is_primary: false,
      }));
      setSkills(sk);
    }

    setShowParsedData(false);
    toast.success("Form filled with resume data! Review each step and make edits as needed.");
    setStep(0); // Go back to step 1 to review filled data
  };

  // Step 1
  const [basic, setBasic] = useState<BasicForm>({ full_name: "", professional_summary: "", career_goals: "", unique_value_proposition: "" });
  // Step 2
  const [contact, setContact] = useState<ContactForm>({ phone: "", location: "", linkedin_url: "", github_url: "", portfolio_url: "", notification_email: "" });
  // Step 3
  const [education, setEducation] = useState<EduEntry[]>([{ degree: "", field: "", institution: "", graduation_year: "", gpa: "" }]);
  // Step 4
  const [experience, setExperience] = useState<ExpEntry[]>([{ title: "", company: "", start_date: "", end_date: "", is_current: false, description: "" }]);
  // Step 5
  const [skills, setSkills] = useState<SkillEntry[]>([]);
  const [skillDraft, setSkillDraft] = useState<SkillEntry>({ name: "", category: "tool", is_primary: false });
  const [skillSearch, setSkillSearch] = useState("");
  const [showAllSelectedSkills, setShowAllSelectedSkills] = useState(false);
  // Step 6
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [parsedResume, setParsedResume] = useState<ParsedResumeData | null>(null);
  const [isParsingResume, setIsParsingResume] = useState(false);
  const [showParsedData, setShowParsedData] = useState(false);
  // Step 7
  const [jobPrefs, setJobPrefs] = useState<JobPreferencesForm>({ desired_roles: "", desired_locations: "", open_to_remote: true, open_to_hybrid: true, min_salary: 0, preferred_industries: "" });

  const updateEducationField = (index: number, key: keyof EduEntry, value: string) => {
    setEducation((prev) => {
      const next = [...prev];
      next[index] = { ...next[index], [key]: value };
      return next;
    });
  };

  const updateExperienceField = (index: number, key: keyof ExpEntry, value: string | boolean) => {
    setExperience((prev) => {
      const next = [...prev];
      next[index] = { ...next[index], [key]: value } as ExpEntry;
      return next;
    });
  };
  // Step 8
  const [automation, setAutomation] = useState({ 
    auto_apply_enabled: false, 
    auto_apply_threshold: 75, 
    auto_apply_daily_limit: 10, 
    require_apply_approval: true, 
    notify_via_email: true, 
    notify_via_telegram: true, 
    notify_new_jobs: true,
    notify_applications: true,
    notify_interviews: true,
    telegram_chat_id: "" 
  });

  const addSkill = (skill: SkillEntry) => {
    const name = skill.name.trim();
    if (!name) return;

    const duplicate = skills.some((existing) => existing.name.trim().toLowerCase() === name.toLowerCase());
    if (duplicate) {
      toast.message("That skill is already added");
      return;
    }

    setSkills([
      ...skills,
      {
        name,
        category: skill.category?.trim() || "tool",
        is_primary: skill.is_primary,
      },
    ]);
    setSkillDraft({ name: "", category: "tool", is_primary: false });
  };

  const removeSkill = (index: number) => {
    setSkills(skills.filter((_, currentIndex) => currentIndex !== index));
  };

  const normalizedSkillSearch = skillSearch.trim().toLowerCase();
  const selectedSkills = skills.filter((sk) => sk.name.trim());
  const primarySkillsCount = selectedSkills.filter((sk) => sk.is_primary).length;
  const DEFAULT_SUGGESTED_SKILLS_LIMIT = 12;
  const SEARCH_SUGGESTED_SKILLS_LIMIT = 60;
  const suggestedSkills = UNIVERSAL_SKILLS.filter((skill) => {
    const alreadyAdded = skills.some((existing) => existing.name.trim().toLowerCase() === skill.toLowerCase());
    const matchesSearch = !normalizedSkillSearch || skill.toLowerCase().includes(normalizedSkillSearch);
    return !alreadyAdded && matchesSearch;
  }).sort((a, b) => {
    if (!normalizedSkillSearch) return a.localeCompare(b);
    const aStarts = a.toLowerCase().startsWith(normalizedSkillSearch);
    const bStarts = b.toLowerCase().startsWith(normalizedSkillSearch);
    if (aStarts && !bStarts) return -1;
    if (!aStarts && bStarts) return 1;
    return a.localeCompare(b);
  });
  const visibleSelectedSkills = showAllSelectedSkills ? selectedSkills : selectedSkills.slice(0, 10);
  const visibleSuggestedSkills = normalizedSkillSearch
    ? suggestedSkills.slice(0, SEARCH_SUGGESTED_SKILLS_LIMIT)
    : suggestedSkills.slice(0, DEFAULT_SUGGESTED_SKILLS_LIMIT);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { "application/pdf": [".pdf"] },
    maxFiles: 1,
    onDrop: (files) => {
      const file = files[0];
      if (file) {
        setResumeFile(file);
        parseResumeFile(file);
      }
    },
  });

  const next = () => setStep((s) => Math.min(s + 1, STEPS.length - 1));
  const prev = () => setStep((s) => Math.max(s - 1, 0));

  const submit = async () => {
    // Validate step 1 (resume upload)
    if (step === 1) {
      if (!resumeFile) {
        toast.error("Please upload a resume to continue");
        return;
      }
      if (showParsedData) {
        toast.error("Please review and apply the parsed data before continuing");
        return;
      }
      // Resume upload happens at the end after all steps
      setLoading(false);
      next();
      return;
    }

    setLoading(true);
    try {
      const stepEndpoints: Record<number, [string, unknown]> = {
        0: ["basic-info", basic],
        2: ["education", { 
          education: education.map(edu => ({
            degree: edu.degree,
            field: edu.field,
            institution: edu.institution,
            year: parseInt(edu.graduation_year) || null,
            gpa: parseFloat(edu.gpa) || null
          }))
        }],
        3: ["work-experience", { 
          experience: experience.map(exp => ({
            title: exp.title,
            company: exp.company,
            start_date: exp.start_date,
            end_date: exp.end_date || null,
            is_current: exp.is_current,
            description: exp.description
          }))
        }],
        4: ["skills", { 
          skills: skills
            .filter((sk) => sk.name.trim())
            .map(sk => ({
            name: sk.name,
            category: sk.category || "tool"
          }))
        }],
        5: ["contact-info", contact],
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
      if (endpoint && typeof endpoint[1] === "object" && endpoint[1] !== null) {
        await onboardingApi.complete(endpoint[0], endpoint[1] as Record<string, unknown>);
      }

      if (step === STEPS.length - 1) {
        // Upload resume at the end
        if (resumeFile) {
          const fd = new FormData();
          fd.append("file", resumeFile);
          fd.append("name", resumeFile.name.replace(".pdf", ""));
          await resumesApi.upload(fd);
        }
        
        toast.success("Profile complete! Welcome to Applivo 🚀");
        router.push("/dashboard");
      } else {
        next();
      }
    } catch (err: unknown) {
      const errorDetail = getErrorDetail(err);
      const errorMessage = Array.isArray(errorDetail) 
        ? errorDetail[0]?.msg || "Invalid input"
        : typeof errorDetail === "string"
          ? errorDetail
          : "Error saving this step";
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (!mounted) return null;

  return (
    <div className="min-h-screen bg-background animated-gradient grid-pattern flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-4">
            <div className="w-10 h-10 rounded-lg bg-[#0E0F14] border border-[#1C1C24] overflow-hidden flex items-center justify-center shadow-lg relative">
              <Image src="/logo.png" alt="Applivo" fill sizes="40px" priority className="absolute inset-0 scale-[1.5] object-contain" />
            </div>
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
                i <= step ? "bg-white text-black" : "bg-muted"
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
                        value={basic[f.key as keyof BasicForm]}
                        onChange={(e) => setBasic({ ...basic, [f.key]: e.target.value })}
                        className="w-full px-4 py-3 bg-muted border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/50 resize-none"
                        placeholder={f.ph}
                      />
                    ) : (
                      <input
                        type="text"
                        value={basic[f.key as keyof BasicForm]}
                        onChange={(e) => setBasic({ ...basic, [f.key]: e.target.value })}
                        className="w-full px-4 py-3 bg-muted border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/50"
                        placeholder={f.ph}
                      />
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* STEP 5 — Contact */}
            {step === 5 && (
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
                        value={contact[f.key as keyof ContactForm]}
                        onChange={(e) => setContact({ ...contact, [f.key]: e.target.value })}
                        className="w-full px-4 py-3 bg-muted border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/50"
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
                    className="flex items-center gap-1 text-sm text-white-light hover:text-white transition-colors">
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
                          <input type="text" value={edu[key as keyof EduEntry]} onChange={(e) => updateEducationField(i, key as keyof EduEntry, e.target.value)}
                            className="w-full px-3 py-2 bg-muted border border-border rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-brand-primary/50"
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
                    className="flex items-center gap-1 text-sm text-white-light hover:text-white transition-colors">
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
                          <input type="text" value={exp[key as keyof Pick<ExpEntry, "title" | "company">]} onChange={(e) => updateExperienceField(i, key as keyof Pick<ExpEntry, "title" | "company">, e.target.value)}
                            className="w-full px-3 py-2 bg-muted border border-border rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-brand-primary/50" placeholder={ph} />
                        </div>
                      ))}
                      <div>
                        <label className="block text-xs font-medium mb-1 text-muted-foreground">Start Date</label>
                        <input type="month" value={exp.start_date} onChange={(e) => updateExperienceField(i, "start_date", e.target.value)}
                          className="w-full px-3 py-2 bg-muted border border-border rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-brand-primary/50" />
                      </div>
                      <div>
                        <label className="block text-xs font-medium mb-1 text-muted-foreground">End Date</label>
                        <input type="month" value={exp.end_date} disabled={exp.is_current} onChange={(e) => updateExperienceField(i, "end_date", e.target.value)}
                          className="w-full px-3 py-2 bg-muted border border-border rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-brand-primary/50 disabled:opacity-80 disabled:cursor-not-allowed" />
                        <label className="flex items-center gap-2 mt-1 text-xs text-muted-foreground cursor-pointer">
                          <input type="checkbox" checked={exp.is_current} onChange={(e) => updateExperienceField(i, "is_current", e.target.checked)} />
                          Current role
                        </label>
                      </div>
                    </div>
                    <div>
                      <label className="block text-xs font-medium mb-1 text-muted-foreground">Description</label>
                      <textarea rows={3} value={exp.description} onChange={(e) => updateExperienceField(i, "description", e.target.value)}
                        className="w-full px-3 py-2 bg-muted border border-border rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-brand-primary/50 resize-none"
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
                  <p className="text-xs text-muted-foreground">Add the skills you actually want Applivo to optimize for.</p>
                </div>
                <div className="rounded-2xl border border-white/10 bg-[#232327] p-5 shadow-lg shadow-black/20">
                  <div className="mb-4 flex flex-wrap items-center gap-2">
                    <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-white">
                      {selectedSkills.length} selected
                    </span>
                    <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-white">
                      {primarySkillsCount} primary
                    </span>
                    <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-white capitalize">
                      {skillDraft.category?.replace(/_/g, " ") || "tool"} mode
                    </span>
                  </div>

                  <div className="grid gap-3 md:grid-cols-[minmax(0,1.2fr)_170px_auto_auto] items-end">
                    <div className="space-y-2">
                      <label className="text-xs font-medium uppercase tracking-[0.18em] text-[#A1A1AA]">Skill name</label>
                      <input
                        type="text"
                        value={skillDraft.name}
                        onChange={(e) => setSkillDraft({ ...skillDraft, name: e.target.value })}
                        placeholder="Type one skill and press Add"
                        className="w-full bg-[#0E0E13] border border-[#1C1C24] rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-white transition-all"
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-medium uppercase tracking-[0.18em] text-[#A1A1AA]">Category</label>
                      <select
                        value={skillDraft.category || "tool"}
                        onChange={(e) => setSkillDraft({ ...skillDraft, category: e.target.value })}
                        className="w-full bg-[#0E0E13] border border-[#1C1C24] rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-white transition-all capitalize"
                      >
                        {SKILL_CATEGORIES.map((category) => (
                          <option key={category} value={category}>
                            {category.replace(/_/g, " ")}
                          </option>
                        ))}
                      </select>
                    </div>
                    <label className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-[#0E0E13] px-4 py-3 text-sm text-white">
                      <input
                        type="checkbox"
                        checked={skillDraft.is_primary}
                        onChange={(e) => setSkillDraft({ ...skillDraft, is_primary: e.target.checked })}
                        className="h-4 w-4 rounded border-white/20 bg-transparent text-white focus:ring-white"
                      />
                      Primary
                    </label>
                    <button
                      type="button"
                      onClick={() => addSkill(skillDraft)}
                      className="inline-flex items-center justify-center gap-2 rounded-xl bg-white px-4 py-3 text-sm font-semibold text-black transition-all hover:bg-gray-200"
                    >
                      <Plus className="w-4 h-4" /> Add
                    </button>
                  </div>

                  <div className="mt-4 grid gap-4 lg:grid-cols-[minmax(0,1.05fr)_minmax(0,0.95fr)]">
                    <div className="rounded-xl border border-white/10 bg-[#0E0E13]">
                      <div className="border-b border-white/10 px-4 py-3">
                        <p className="text-sm font-medium text-white">Selected skills</p>
                        <p className="text-xs text-[#A1A1AA]">Keep only relevant skills to improve matching quality.</p>
                      </div>
                      {selectedSkills.length ? (
                        <div className="max-h-64 overflow-y-auto px-2 py-2">
                          {visibleSelectedSkills.map((sk, i) => {
                            const realIndex = skills.findIndex(
                              (existing) =>
                                existing.name.trim().toLowerCase() === sk.name.trim().toLowerCase() &&
                                existing.category === sk.category &&
                                existing.is_primary === sk.is_primary
                            );
                            return (
                              <div key={`${sk.name}-${i}`} className="flex items-center justify-between gap-2 rounded-lg px-3 py-2 hover:bg-white/5">
                                <div className="min-w-0">
                                  <p className="truncate text-sm font-medium text-white">{sk.name}</p>
                                  <div className="mt-1 flex items-center gap-2 text-[10px] uppercase tracking-[0.14em] text-[#A1A1AA]">
                                    <span>{(sk.category || "tool").replace(/_/g, " ")}</span>
                                    {sk.is_primary && <span className="rounded-full border border-white/15 bg-white/10 px-1.5 py-0.5 text-[9px]">Primary</span>}
                                  </div>
                                </div>
                                <button
                                  type="button"
                                  onClick={() => removeSkill(realIndex)}
                                  className="rounded-md p-1.5 text-[#A1A1AA] transition-colors hover:bg-red-500/15 hover:text-red-300"
                                  aria-label={`Remove ${sk.name}`}
                                >
                                  <X className="w-3.5 h-3.5" />
                                </button>
                              </div>
                            );
                          })}
                        </div>
                      ) : (
                        <div className="flex min-h-[160px] items-center justify-center px-4 text-center">
                          <p className="text-sm text-[#A1A1AA]">No skills yet. Add a few core skills to continue.</p>
                        </div>
                      )}
                      {selectedSkills.length > 10 && (
                        <div className="border-t border-white/10 px-4 py-2">
                          <button
                            type="button"
                            onClick={() => setShowAllSelectedSkills((v) => !v)}
                            className="text-xs font-medium text-white/80 transition-colors hover:text-white"
                          >
                            {showAllSelectedSkills ? "Show fewer" : `Show all (${selectedSkills.length})`}
                          </button>
                        </div>
                      )}
                    </div>

                    <div className="rounded-xl border border-white/10 bg-[#0E0E13] p-4">
                      <div className="mb-3 flex items-center justify-between gap-3">
                        <p className="text-sm font-medium text-white">Suggested skills</p>
                        <input
                          type="text"
                          value={skillSearch}
                          onChange={(e) => setSkillSearch(e.target.value)}
                          placeholder="Search"
                          className="w-40 bg-[#101017] border border-[#1C1C24] rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-white transition-all"
                        />
                      </div>

                      <div className="flex max-h-44 flex-wrap gap-2 overflow-y-auto pr-1">
                        {visibleSuggestedSkills.length ? visibleSuggestedSkills.map((skill) => (
                          <button
                            key={skill}
                            type="button"
                            onClick={() => addSkill({ name: skill, category: "tool", is_primary: false })}
                            className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-medium text-white transition-all hover:border-white/30 hover:bg-white/10"
                          >
                            + {skill}
                          </button>
                        )) : (
                          <p className="text-sm text-[#A1A1AA]">No suggestions match your search.</p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* STEP 1 — Resume Upload & Parse */}
            {step === 1 && (
              <div className="space-y-5">
                <h2 className="text-lg font-semibold">Upload your resume</h2>
                
                {!showParsedData ? (
                  <>
                    <div {...getRootProps()} className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all ${isDragActive ? "border-brand-primary bg-white text-black/10" : "border-border hover:border-brand-primary/50 hover:bg-white/3"}`}>
                      <input {...getInputProps()} />
                      {isParsingResume ? (
                        <>
                          <Loader2 className="w-10 h-10 text-brand-primary mx-auto mb-3 animate-spin" />
                          <p className="text-sm font-medium">Parsing your resume...</p>
                        </>
                      ) : resumeFile ? (
                        <p className="text-brand-green font-medium">{resumeFile.name}</p>
                      ) : (
                        <>
                          <Upload className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
                          <p className="text-sm font-medium mb-1">Drag & drop your PDF resume</p>
                          <p className="text-xs text-muted-foreground">or click to browse files</p>
                        </>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground text-center">PDF only · Max 10MB · We&apos;ll automatically extract your data and fill the form</p>
                  </>
                ) : (
                  <div className="space-y-5">
                    <div className="p-4 bg-brand-green/10 border border-brand-green/30 rounded-lg">
                      <p className="text-sm text-brand-green font-medium">✓ Resume parsed successfully!</p>
                      <p className="text-xs text-muted-foreground mt-1">Review the extracted data below. You can edit any field.</p>
                    </div>

                    <div className="space-y-4 max-h-96 overflow-y-auto">
                      {/* Basic Info */}
                      {parsedResume?.name && (
                        <div className="p-4 bg-muted/50 rounded-lg space-y-2">
                          <h3 className="text-sm font-semibold">Basic Information</h3>
                          <div>
                            <label className="block text-xs text-muted-foreground mb-1">Name</label>
                            <input type="text" defaultValue={parsedResume.name} 
                              className="w-full px-3 py-2 bg-muted border border-border rounded-md text-sm" disabled />
                          </div>
                          {parsedResume.professional_summary && (
                            <div>
                              <label className="block text-xs text-muted-foreground mb-1">Professional Summary</label>
                              <textarea rows={2} defaultValue={parsedResume.professional_summary}
                                className="w-full px-3 py-2 bg-muted border border-border rounded-md text-sm resize-none" disabled />
                            </div>
                          )}
                        </div>
                      )}

                      {/* Contact Info */}
                      {(parsedResume?.phone || parsedResume?.email || parsedResume?.location) && (
                        <div className="p-4 bg-muted/50 rounded-lg space-y-2">
                          <h3 className="text-sm font-semibold">Contact Information</h3>
                          {parsedResume.phone && <div>
                            <label className="block text-xs text-muted-foreground mb-1">Phone</label>
                            <input type="text" defaultValue={parsedResume.phone}
                              className="w-full px-3 py-2 bg-muted border border-border rounded-md text-sm" disabled />
                          </div>}
                          {parsedResume.location && <div>
                            <label className="block text-xs text-muted-foreground mb-1">Location</label>
                            <input type="text" defaultValue={parsedResume.location}
                              className="w-full px-3 py-2 bg-muted border border-border rounded-md text-sm" disabled />
                          </div>}
                          {parsedResume.linkedin_url && <div>
                            <label className="block text-xs text-muted-foreground mb-1">LinkedIn</label>
                            <input type="text" defaultValue={parsedResume.linkedin_url}
                              className="w-full px-3 py-2 bg-muted border border-border rounded-md text-sm" disabled />
                          </div>}
                          {parsedResume.github_url && <div>
                            <label className="block text-xs text-muted-foreground mb-1">GitHub</label>
                            <input type="text" defaultValue={parsedResume.github_url}
                              className="w-full px-3 py-2 bg-muted border border-border rounded-md text-sm" disabled />
                          </div>}
                        </div>
                      )}

                      {/* Education */}
                      {parsedResume?.education && parsedResume.education.length > 0 && (
                        <div className="p-4 bg-muted/50 rounded-lg space-y-2">
                          <h3 className="text-sm font-semibold">Education ({parsedResume.education.length})</h3>
                          {parsedResume.education.map((edu: ParsedEducationItem, i: number) => (
                            <div key={i} className="text-sm">
                              <p className="font-medium">{edu.degree} in {edu.field}</p>
                              <p className="text-xs text-muted-foreground">{edu.institution} • {edu.grad_year}</p>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Experience */}
                      {parsedResume?.work_experience && parsedResume.work_experience.length > 0 && (
                        <div className="p-4 bg-muted/50 rounded-lg space-y-2">
                          <h3 className="text-sm font-semibold">Work Experience ({parsedResume.work_experience.length})</h3>
                          {parsedResume.work_experience.map((exp: ParsedWorkExperienceItem, i: number) => (
                            <div key={i} className="text-sm">
                              <p className="font-medium">{exp.title} at {exp.company}</p>
                              <p className="text-xs text-muted-foreground">{exp.start_date} to {exp.end_date || 'Present'}</p>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Skills */}
                      {parsedResume?.skills && parsedResume.skills.length > 0 && (
                        <div className="p-4 bg-muted/50 rounded-lg space-y-2">
                          <h3 className="text-sm font-semibold">Skills parsed</h3>
                          <p className="text-xs text-muted-foreground">
                            We found {parsedResume.skills.length} skills in your resume. Use the Skills step to search and add the ones you want to keep.
                          </p>
                        </div>
                      )}
                    </div>

                    <div className="flex gap-3">
                      <button
                        onClick={() => setShowParsedData(false)}
                        className="flex-1 px-4 py-2 bg-muted border border-border rounded-lg text-sm font-medium hover:bg-muted/80"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={applyParsedData}
                        className="flex-1 px-4 py-2 bg-brand-primary text-black rounded-lg text-sm font-medium hover:bg-white"
                      >
                        Apply to Form ✓
                      </button>
                    </div>
                  </div>
                )}
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
                    <input type="text" value={jobPrefs[f.key as keyof Pick<JobPreferencesForm, "desired_roles" | "desired_locations" | "preferred_industries">]} onChange={(e) => setJobPrefs({ ...jobPrefs, [f.key]: e.target.value })}
                      className="w-full px-4 py-3 bg-muted border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/50"
                      placeholder={f.ph} />
                  </div>
                ))}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Min Salary (₹/year)</label>
                    <input type="number" value={jobPrefs.min_salary} onChange={(e) => setJobPrefs({ ...jobPrefs, min_salary: +e.target.value })}
                      className="w-full px-4 py-3 bg-muted border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/50" />
                  </div>
                  <div className="space-y-3 flex flex-col justify-end pb-1">
                    {[["open_to_remote", "Open to Remote"], ["open_to_hybrid", "Open to Hybrid"]].map(([key, label]) => (
                      <label key={key} className="flex items-center gap-3 cursor-pointer">
                        <input type="checkbox" checked={jobPrefs[key as keyof Pick<JobPreferencesForm, "open_to_remote" | "open_to_hybrid">]} onChange={(e) => setJobPrefs({ ...jobPrefs, [key]: e.target.checked })}
                          className="w-4 h-4 accent-brand-primary" />
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
                  <div className={`w-12 h-6 rounded-full transition-colors ${automation.auto_apply_enabled ? "bg-white text-black" : "bg-muted"} relative cursor-pointer`}
                    onClick={() => setAutomation({ ...automation, auto_apply_enabled: !automation.auto_apply_enabled })}>
                    <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${automation.auto_apply_enabled ? "left-7" : "left-1"}`} />
                  </div>
                </label>

                <div>
                  <div className="flex justify-between mb-2">
                    <label className="text-sm font-medium">Match Threshold</label>
                    <span className="text-sm text-white-light font-semibold">{automation.auto_apply_threshold}%</span>
                  </div>
                  <input type="range" min={0} max={100} value={automation.auto_apply_threshold}
                    onChange={(e) => setAutomation({ ...automation, auto_apply_threshold: +e.target.value })}
                    className="w-full accent-brand-primary" />
                  <p className="text-xs text-muted-foreground mt-1">Only apply to jobs scoring above this threshold</p>
                </div>

                <label className="flex items-center gap-3 cursor-pointer">
                  <input type="checkbox" checked={automation.require_apply_approval}
                    onChange={(e) => setAutomation({ ...automation, require_apply_approval: e.target.checked })}
                    className="w-4 h-4 accent-brand-primary" />
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
                      className="w-full px-4 py-3 bg-muted border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/50"
                      placeholder="Get from @userinfobot on Telegram" />
                  </div>
                )}

                <div className="p-4 bg-brand-primary/10 border border-brand-primary/30 rounded-lg text-sm text-brand-primary-light">
                  <span className="mr-2">🎉</span>
                  Almost done! Click &quot;Complete Setup&quot; to finish and access your dashboard.
                </div>
              </div>
            )}
          </motion.div>
        </AnimatePresence>

        {/* Navigation */}
        <div className="flex justify-between mt-6">
          <button onClick={prev} disabled={step === 0}
            className="flex items-center gap-2 px-5 py-2.5 rounded-lg border border-border text-sm hover:bg-white/5 transition-colors disabled:opacity-80 disabled:cursor-not-allowed">
            <ChevronLeft className="w-4 h-4" /> Back
          </button>
          <button onClick={submit} disabled={loading}
            className="flex items-center gap-2 px-6 py-2.5 bg-white text-zinc-950 rounded-lg font-semibold text-sm hover:bg-white/90 transition-all hover:shadow-lg hover:shadow-white/10 disabled:opacity-80 disabled:cursor-not-allowed">
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
