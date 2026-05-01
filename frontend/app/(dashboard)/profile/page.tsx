"use client";
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { profileApi, api, applicationsApi, onboardingApi } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import { 
  User as UserIcon, 
  Briefcase, 
  GraduationCap, 
  Code, 
  Edit3, 
  Plus, 
  X, 
  Download, 
  Phone, 
  CheckCircle2,
  Send,
  Target,
  BarChart3,
  Smartphone,
  Monitor,
  Laptop,
  Trash2,
  LogOut,
  AlertTriangle,
  Loader2,
  Save,
  Calendar,
  Zap
} from "lucide-react";
import { cn } from "@/lib/utils";
import { UNIVERSAL_SKILLS } from "@/lib/skillRecommendations";

// --- Types ---
interface Session {
  id: string;
  device_name: string | null;
  device_type: string | null;
  browser: string | null;
  os: string | null;
  ip_address: string | null;
  location: string | null;
  is_current: boolean;
  is_active: boolean;
  created_at: string;
  last_used_at: string | null;
}

// --- Main Page ---
export default function ProfilePage() {
  const { user } = useAuth();
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState("basic");
  
  const { data: profile, isLoading } = useQuery({
    queryKey: ["profile"],
    queryFn: () => profileApi.get().then(r => r.data),
    staleTime: 60000,
  });

  const { data: profileSkills = [] } = useQuery({
    queryKey: ["profile-skills"],
    queryFn: () => profileApi.listSkills().then(r => r.data),
    staleTime: 60000,
  });

  const { data: stats } = useQuery({
    queryKey: ["app-stats"],
    queryFn: () => applicationsApi.stats().then(r => r.data),
  });

  // Edit Basic Info State
  const [editBasic, setEditBasic] = useState(false);
  const [basicForm, setBasicForm] = useState({ 
    full_name: "", 
    professional_summary: "", 
    unique_value_proposition: "",
    career_goals: "",
    desired_roles: [] as string[],
    experience_level: "",
    location: "",
    phone: "",
    linkedin_url: "",
    github_url: "",
    portfolio_url: "",
  });

  const [automationForm, setAutomationForm] = useState({ 
    auto_apply_enabled: false,
    auto_apply_threshold: 75,
    auto_apply_daily_limit: 10,
    require_apply_approval: true,
    telegram_chat_id: "",
  });

  const [prefsForm, setPrefsForm] = useState({
    desired_roles: "",
    desired_locations: "",
    min_salary: 0,
    preferred_industries: "",
  });

  // Modal States
  const [modalType, setModalType] = useState<"experience" | "education" | "skill" | null>(null);
  
  // Experience Form
  const [expForm, setExpForm] = useState({
    title: "", company: "", 
    start_month: "01", start_year: "", 
    end_month: "01", end_year: "", 
    is_current: false, description: ""
  });

  // Education Form
  const [eduForm, setEduForm] = useState({
    degree: "", field: "", institution: "", graduation_year: "", gpa: ""
  });

  // Skill Form
  const [skillForm, setSkillForm] = useState({
    name: ""
  });
  const [sessionAddedSkills, setSessionAddedSkills] = useState<string[]>([]);
  const [parseFile, setParseFile] = useState<File | null>(null);
  const [editIndex, setEditIndex] = useState<number | null>(null);

  const formatExperienceLevel = (value?: string | null) => {
    if (!value) return "—";
    return value.toLowerCase().replace(/\b\w/g, (char) => char.toUpperCase());
  };

  const handleDownloadInfo = () => {
    const lines = [
      "Applivo Profile Information",
      "",
      `Name: ${profile?.full_name || user?.full_name || "New Candidate"}`,
      `Email: ${user?.email || "—"}`,
      `App ID: ${user?.id || "—"}`,
      `Experience Level: ${profile?.experience_level || "—"}`,
      `Phone: ${profile?.phone || "+1 (555) 000-0000"}`,
      `Location: ${profile?.location || "Remote"}`,
      `LinkedIn: ${profile?.linkedin_url || "—"}`,
      `GitHub: ${profile?.github_url || "—"}`,
      `Portfolio: ${profile?.portfolio_url || "—"}`,
      "",
      "Generated from the Applivo profile page.",
    ];

    const blob = new Blob([lines.join("\n")], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${(profile?.full_name || user?.full_name || "applivo-profile").replace(/\s+/g, "-").toLowerCase()}.txt`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    toast.success("Profile info downloaded");
  };

  // Mutations
  const mutUpdate = useMutation({
    mutationFn: (data: any) => profileApi.update(data),
    onSuccess: () => {
      toast.success("Profile updated!");
      setModalType(null);
      setEditIndex(null);
      setEditBasic(false);
      qc.invalidateQueries({ queryKey: ["profile"] });
      qc.invalidateQueries({ queryKey: ["profile-skills"] });
    },
    onError: () => toast.error("Update failed")
  });

  const mutAddSkill = useMutation({
    mutationFn: (data: any) => profileApi.addSkill(data),
    onSuccess: (_data, variables) => {
      toast.success("Skill added!");
      const addedName = String(variables?.name || "").trim();
      if (addedName) {
        setSessionAddedSkills((prev) => Array.from(new Set([...prev, addedName])));
      }
      setSkillForm({ name: "" });
      qc.invalidateQueries({ queryKey: ["profile"] });
      qc.invalidateQueries({ queryKey: ["profile-skills"] });
    },
    onError: () => toast.error("Failed to add skill")
  });

  const mutParseAndFill = useMutation({
    mutationFn: async (file: File) => {
      const fd = new FormData();
      fd.append("file", file);
      return onboardingApi.parseResumeAndFill(fd);
    },
    onSuccess: () => {
      toast.success("Profile updated from resume");
      setParseFile(null);
      qc.invalidateQueries({ queryKey: ["profile"] });
      qc.invalidateQueries({ queryKey: ["profile-skills"] });
    },
    onError: (err: any) => {
      const errorDetail = err?.response?.data?.detail;
      toast.error(typeof errorDetail === "string" ? errorDetail : "Failed to parse resume");
    },
  });

  const handleAddExperience = (e: React.FormEvent) => {
    e.preventDefault();
    const data = {
        ...expForm,
        start_date: expForm.start_year ? `${expForm.start_year}-${expForm.start_month}` : "",
        end_date: expForm.end_year ? `${expForm.end_year}-${expForm.end_month}` : ""
    };
    const updatedExp = [...(profile?.work_experience || [])];
    if (editIndex !== null) {
      updatedExp[editIndex] = data;
    } else {
      updatedExp.push(data);
    }
    mutUpdate.mutate({ work_experience: updatedExp });
  };

  const handleEditExperienceOpen = (index: number) => {
    const item = profile?.work_experience[index];
    const sDate = item.start_date || item.start || "";
    const sParts = sDate.split("-");
    const eDate = item.end_date || item.end || "";
    const eParts = eDate.split("-");

    setExpForm({
      title: item.title || "",
      company: item.company || "",
      start_year: sParts[0] || "",
      start_month: sParts[1] || "01",
      end_year: eParts[0] || "",
      end_month: eParts[1] || "01",
      is_current: item.is_current || false,
      description: item.description || ""
    });
    setEditIndex(index);
    setModalType("experience");
  };

  const handleDeleteExperience = (index: number) => {
    if (!window.confirm("Are you sure you want to delete this experience?")) return;
    const updatedExp = profile?.work_experience.filter((_: any, i: number) => i !== index);
    mutUpdate.mutate({ work_experience: updatedExp });
  };

  const handleAddEducation = (e: React.FormEvent) => {
    e.preventDefault();
    const updatedEdu = [...(profile?.education || [])];
    if (editIndex !== null) {
      updatedEdu[editIndex] = eduForm;
    } else {
      updatedEdu.push(eduForm);
    }
    mutUpdate.mutate({ education: updatedEdu });
  };

  const handleEditEducationOpen = (index: number) => {
    const item = profile?.education[index];
    setEduForm({
      degree: item.degree || "",
      field: item.field || "",
      institution: item.institution || "",
      graduation_year: toYearOnly(item.year || item.graduation_year),
      gpa: item.gpa || ""
    });
    setEditIndex(index);
    setModalType("education");
  };

  const handleDeleteEducation = (index: number) => {
    if (!window.confirm("Are you sure you want to delete this education?")) return;
    const updatedEdu = profile?.education.filter((_: any, i: number) => i !== index);
    mutUpdate.mutate({ education: updatedEdu });
  };

  const handleAddSkill = (e: React.FormEvent) => {
    e.preventDefault();
    const skillName = skillForm.name.trim();
    if (!skillName) return;

    const alreadyExists = profileSkills.some((s: any) => (s.name || "").toLowerCase() === skillName.toLowerCase())
      || sessionAddedSkills.some((s) => s.toLowerCase() === skillName.toLowerCase());

    if (alreadyExists) {
      toast.info("Skill already added");
      setSkillForm({ name: "" });
      return;
    }

    mutAddSkill.mutate({
      name: skillName,
      proficiency: "intermediate",
      category: "tool",
    });
  };

  const handleDeleteSkill = async (skillId: string) => {
    if (!window.confirm("Remove this skill?")) return;
    try {
      await profileApi.deleteSkill(skillId);
      toast.success("Skill removed");
      qc.invalidateQueries({ queryKey: ["profile-skills"] });
    } catch (err) {
      toast.error("Failed to remove skill");
    }
  };


  const handleEditBasicOpen = () => {
    setBasicForm({
      full_name: profile?.full_name || user?.full_name || "",
      professional_summary: profile?.professional_summary || "",
      unique_value_proposition: profile?.unique_value_proposition || "",
      career_goals: profile?.career_goals || "",
      desired_roles: profile?.desired_roles || [],
      experience_level: (profile?.experience_level || "ENTRY").toLowerCase(),
      location: profile?.location || "",
      phone: profile?.phone || "",
      linkedin_url: profile?.linkedin_url || "",
      github_url: profile?.github_url || "",
      portfolio_url: profile?.portfolio_url || "",
    });
    setEditBasic(true);
  };

  const handleEditPrefsOpen = () => {
    setPrefsForm({
      desired_roles: (profile?.desired_roles || []).join(", "),
      desired_locations: (profile?.desired_locations || []).join(", "),
      min_salary: profile?.min_salary || 0,
      preferred_industries: (profile?.preferred_industries || []).join(", "),
    });
  };

  const handleEditAutomationOpen = () => {
    setAutomationForm({
      auto_apply_enabled: profile?.auto_apply_enabled ?? false,
      auto_apply_threshold: profile?.auto_apply_threshold ?? 75,
      auto_apply_daily_limit: profile?.auto_apply_daily_limit ?? 10,
      require_apply_approval: profile?.require_apply_approval ?? true,
      telegram_chat_id: profile?.telegram_chat_id || "",
    });
  };

  React.useEffect(() => {
    if (profile) {
      if (activeTab === "preferences") handleEditPrefsOpen();
      if (activeTab === "automation") handleEditAutomationOpen();
    }
  }, [profile, activeTab]);

  const completion = profile ? Math.round(([profile.full_name, profile.professional_summary, profile.location, profile.work_experience?.length, profileSkills?.length].filter(Boolean).length / 5) * 100) : 0;

  const clampDailyLimit = (value: number) => {
    if (!Number.isFinite(value)) return 10;
    return Math.min(100, Math.max(1, Math.trunc(value)));
  };

  const formatMonthYear = (value?: string | null) => {
    if (!value) return "Not specified";
    const raw = String(value).trim();
    if (!raw) return "Not specified";
    const yyyymm = raw.match(/^(\d{4})-(\d{2})$/);
    if (yyyymm) {
      const [_, year, month] = yyyymm;
      const dt = new Date(Number(year), Number(month) - 1, 1);
      if (!Number.isNaN(dt.getTime())) {
        return dt.toLocaleDateString("en-US", { month: "short", year: "numeric" });
      }
    }
    const yearMatch = raw.match(/\b(19|20)\d{2}\b/);
    if (yearMatch) return yearMatch[0];
    return raw;
  };

  const toYYYYMM = (value?: string | null) => {
    if (!value) return "";
    const raw = String(value).trim();
    const match = raw.match(/^(\d{4})-(\d{2})$/);
    if (match) return raw;
    const yearMatch = raw.match(/\b(19|20)\d{2}\b/);
    if (yearMatch) return `${yearMatch[0]}-01`;
    return "";
  };

  const toYearOnly = (value?: string | number | null) => {
    if (!value) return "";
    const raw = String(value).trim();
    const match = raw.match(/\b(19|20)\d{2}\b/);
    return match ? match[0] : "";
  };

  if (isLoading) return (
    <div className="max-w-7xl mx-auto px-6 py-6 space-y-6">
      <div className="h-64 bg-[#232327] border border-[#1C1C24] rounded-2xl animate-pulse" />
      <div className="grid grid-cols-4 gap-6">
        {[1,2,3,4].map(i => <div key={i} className="h-24 bg-[#232327] border border-[#1C1C24] rounded-2xl animate-pulse" />)}
      </div>
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto px-6 py-6 space-y-6 bg-transparent">
      
      {/* Page Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 bg-[#242424] border border-white/[0.08] rounded-lg">
          <UserIcon className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">Profile</h1>
          <p className="text-sm text-zinc-400 mt-1">Manage your personal information and credentials</p>
        </div>
      </div>

      {/* 1. Profile Header Card */}
      <section className="bg-[#1c1c1e] border border-[#262626] rounded-2xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div className="flex items-center gap-5">
            <div>
              <h1 className="text-xl font-semibold text-white mb-0.5">{profile?.full_name || user?.full_name || "New Candidate"}</h1>
              <div className="flex flex-wrap items-center gap-3">
                <span className="text-xs text-[#A1A1AA]">{profile?.experience_level || "No level set"}</span>
                <span className="text-xs text-[#A1A1AA]">App ID: {user?.id.slice(0, 8)}</span>
                <div className="flex items-center gap-1.5 px-2 py-0.5 bg-white/5 border border-white/10 rounded-full">
                  <div className="w-1.5 h-1.5 rounded-full bg-green-500" />
                  <span className="text-[10px] text-white font-bold uppercase tracking-wider">{completion}% Complete</span>
                </div>
              </div>
            </div>
          </div>
          
          <button 
            onClick={handleDownloadInfo}
            className="bg-white text-black rounded-xl px-4 py-2 font-medium hover:bg-gray-200 transition-all flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            Download Info
          </button>
        </div>

        {/* Meta Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mt-8 pt-6 border-t border-white/10">
          <div className="space-y-1">
            <p className="text-xs text-[#A1A1AA]">Role</p>
            <p className="text-sm text-white font-medium">{formatExperienceLevel(profile?.experience_level)}</p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-[#A1A1AA]">Phone Number</p>
            <p className="text-sm text-white font-medium">{profile?.phone || "+1 (555) 000-0000"}</p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-[#A1A1AA]">Email Address</p>
            <p className="text-sm text-white font-medium truncate">{user?.email || "—"}</p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-[#A1A1AA]">Location</p>
            <p className="text-sm text-white font-medium">{profile?.location || "Remote"}</p>
          </div>
        </div>
      </section>

      {/* 2. Resume Parse Quick Action (Top) */}
      <section className="bg-[#1c1c1e] border border-[#262626] rounded-2xl p-6 shadow-sm">
        <p className="text-sm font-semibold text-white mb-3">Update Profile From Resume</p>
        <div className="flex flex-col md:flex-row gap-3 md:items-center">
          <input
            type="file"
            accept=".pdf,application/pdf"
            onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) {
                    mutParseAndFill.mutate(file);
                }
            }}
            disabled={mutParseAndFill.isPending}
            className="text-xs text-[#A1A1AA] file:mr-3 file:rounded-lg file:border-0 file:bg-white file:px-3 file:py-2 file:text-xs file:font-semibold file:text-black hover:file:bg-zinc-200 disabled:opacity-50"
          />
          {mutParseAndFill.isPending && (
            <div className="flex items-center gap-2 text-xs text-white">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Reading resume...</span>
            </div>
          )}
        </div>
        <p className="text-xs text-[#A1A1AA] mt-2">Uploads are not required here. This will parse the PDF and fill your profile fields, which you can edit anytime.</p>
      </section>


      {/* 4. Tabbed Content Section */}
      <section className="space-y-6">
        <div className="bg-[#232327] border border-white/10 rounded-full p-1 flex gap-1 w-fit overflow-x-auto no-scrollbar">
          {[
            { id: "basic", label: "Basic Info", icon: UserIcon },
            { id: "experience", label: "Experience", icon: Briefcase },
            { id: "education", label: "Education", icon: GraduationCap },
            { id: "skills", label: "Skills", icon: Code },
            { id: "preferences", label: "Preferences", icon: Target },
            { id: "automation", label: "Automation", icon: Zap },
          ].map(t => (
            <button 
              key={t.id} 
              onClick={() => setActiveTab(t.id)}
              className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-full text-xs font-medium transition-all whitespace-nowrap", 
                activeTab === t.id ? "bg-white text-black" : "text-[#A1A1AA] hover:text-white"
              )}
            >
              <t.icon className="w-3.5 h-3.5" /> 
              <span>{t.label}</span>
            </button>
          ))}
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="bg-[#1c1c1e] border border-[#262626] rounded-2xl p-6 shadow-sm min-h-[400px]"
          >
            {activeTab === "basic" && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-white">Basic Information</h2>
                  {!editBasic && (
                    <button onClick={handleEditBasicOpen} className="p-2 bg-[#232327] border border-white/10 rounded-xl text-white hover:bg-[#1C1C24] transition-all">
                      <Edit3 className="w-4 h-4" />
                    </button>
                  )}
                </div>

                {editBasic ? (
                  <form onSubmit={e => { e.preventDefault(); mutUpdate.mutate(basicForm); }} className="grid grid-cols-2 gap-4">
                    <div className="col-span-1 space-y-2">
                      <label className="text-xs text-[#A1A1AA]">Full Name</label>
                      <input type="text" value={basicForm.full_name} onChange={e => setBasicForm({ ...basicForm, full_name: e.target.value })} className="w-full bg-[#232327] border border-[#1C1C24] rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-white transition-all" />
                    </div>
                    <div className="col-span-1 space-y-2">
                        <label className="text-xs text-[#A1A1AA]">Experience Level</label>
                        <select value={basicForm.experience_level} onChange={e => setBasicForm({ ...basicForm, experience_level: e.target.value })} className="w-full bg-[#232327] border border-[#1C1C24] rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-white transition-all capitalize">
                            {["entry", "mid", "senior", "lead", "executive"].map(l => <option key={l} value={l}>{l}</option>)}
                        </select>
                    </div>
                    <div className="col-span-1 space-y-2">
                      <label className="text-xs text-[#A1A1AA]">Location</label>
                      <input type="text" value={basicForm.location} onChange={e => setBasicForm({ ...basicForm, location: e.target.value })} className="w-full bg-[#232327] border border-[#1C1C24] rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-white transition-all" />
                    </div>
                    <div className="col-span-1 space-y-2">
                      <label className="text-xs text-[#A1A1AA]">Phone Number</label>
                      <input type="text" value={basicForm.phone} onChange={e => setBasicForm({ ...basicForm, phone: e.target.value })} className="w-full bg-[#232327] border border-[#1C1C24] rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-white transition-all" />
                    </div>
                    <div className="col-span-2 space-y-2">
                        <label className="text-xs text-[#A1A1AA]">LinkedIn URL</label>
                        <input type="text" value={basicForm.linkedin_url} onChange={e => setBasicForm({ ...basicForm, linkedin_url: e.target.value })} className="w-full bg-[#232327] border border-[#1C1C24] rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-white transition-all" />
                    </div>
                    <div className="col-span-2 space-y-2">
                      <label className="text-xs text-[#A1A1AA]">Professional Summary</label>
                      <textarea rows={3} value={basicForm.professional_summary} onChange={e => setBasicForm({ ...basicForm, professional_summary: e.target.value })} className="w-full bg-[#232327] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-white transition-all resize-none" />
                    </div>
                    <div className="col-span-2 space-y-2">
                        <label className="text-xs text-[#A1A1AA]">Career Goals</label>
                        <textarea rows={2} value={basicForm.career_goals} onChange={e => setBasicForm({ ...basicForm, career_goals: e.target.value })} className="w-full bg-[#232327] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-white transition-all resize-none" />
                    </div>
                    <div className="col-span-2 flex justify-end gap-2 pt-2">
                      <button type="button" onClick={() => setEditBasic(false)} className="px-4 py-2 text-sm text-[#A1A1AA]">Cancel</button>
                      <button type="submit" disabled={mutUpdate.isPending} className="bg-white text-black px-6 py-2 rounded-xl text-sm font-medium hover:bg-gray-200 shadow-lg">
                        Save Changes
                      </button>
                    </div>
                  </form>
                ) : (
                  <div className="grid grid-cols-2 gap-8">
                    <div className="space-y-4 col-span-2 md:col-span-1">
                      <div>
                        <p className="text-xs text-[#A1A1AA] mb-1">Full Name</p>
                        <p className="text-sm text-white font-medium">{profile?.full_name || "—"}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#A1A1AA] mb-1">Experience Level</p>
                        <p className="text-sm text-white font-medium capitalize">{profile?.experience_level || "—"}</p>
                      </div>
                    </div>
                    <div className="space-y-4 col-span-2 md:col-span-1">
                      <div>
                        <p className="text-xs text-[#A1A1AA] mb-1">Location</p>
                        <p className="text-sm text-white font-medium">{profile?.location || "—"}</p>
                      </div>
                    </div>
                    <div className="col-span-2">
                      <p className="text-xs text-[#A1A1AA] mb-1">Professional Summary</p>
                      <p className="text-sm text-white/80 leading-relaxed font-medium bg-[#232327] p-4 rounded-xl border border-white/10">
                        {profile?.professional_summary || "No summary provided."}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === "experience" && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-white">Work Experience</h2>
                  <button onClick={() => {
                    setExpForm({ title: "", company: "", start_month: "01", start_year: "", end_month: "01", end_year: "", is_current: false, description: "" });
                    setEditIndex(null);
                    setModalType("experience");
                  }} className="bg-white text-black rounded-xl px-4 py-2 text-sm font-medium hover:bg-gray-200 transition-all flex items-center gap-2">
                    <Plus className="w-4 h-4" /> Add
                  </button>
                </div>
                <div className="space-y-4">
                  {profile?.work_experience?.map((exp: any, i: number) => (
                    <div key={i} className="p-4 bg-[#232327] border border-white/10 rounded-xl flex justify-between items-start group">
                      <div className="flex gap-4">
                        <div className="w-10 h-10 rounded-lg bg-[#232327] border border-[#1C1C24] flex items-center justify-center shrink-0">
                          <Briefcase className="w-5 h-5 text-white" />
                        </div>
                        <div>
                          <p className="text-sm text-white font-semibold">{exp.title}</p>
                          <p className="text-xs text-[#A1A1AA] font-medium">{exp.company}</p>
                          <p className="text-xs text-[#A1A1AA] flex items-center gap-1 mt-1">
                            <Calendar className="w-3 h-3" /> {formatMonthYear(exp.start_date || exp.start)} - {(exp.is_current ? "Present" : formatMonthYear(exp.end_date || exp.end))}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 transition-all">
                        <button onClick={() => handleEditExperienceOpen(i)} className="p-2 bg-white/5 border border-white/10 rounded-lg text-[#A1A1AA] hover:text-white hover:bg-white/10 transition-all">
                          <Edit3 className="w-3.5 h-3.5" />
                        </button>
                        <button onClick={() => handleDeleteExperience(i)} className="p-2 bg-white/5 border border-white/10 rounded-lg text-red-400/70 hover:text-red-400 hover:bg-red-400/10 transition-all">
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  ))}
                  {!profile?.work_experience?.length && <p className="text-center text-[#A1A1AA] py-10">No experience listed.</p>}
                </div>
              </div>
            )}

            {activeTab === "education" && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-white">Education</h2>
                  <button onClick={() => {
                    setEduForm({ degree: "", field: "", institution: "", graduation_year: "", gpa: "" });
                    setEditIndex(null);
                    setModalType("education");
                  }} className="bg-white text-black rounded-xl px-4 py-2 text-sm font-medium hover:bg-gray-200 transition-all flex items-center gap-2">
                    <Plus className="w-4 h-4" /> Add
                  </button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {profile?.education?.map((edu: any, i: number) => (
                    <div key={i} className="p-4 bg-[#232327] border border-white/10 rounded-xl group relative">
                      <p className="text-sm text-white font-semibold">{edu.field ? `${edu.degree} in ${edu.field}` : edu.degree}</p>
                      <p className="text-xs text-[#A1A1AA] mt-0.5">{edu.institution}</p>
                      <div className="flex justify-between mt-3 text-[10px] text-[#A1A1AA] uppercase font-bold tracking-tight">
                        <span>{(edu.year || edu.graduation_year) ? `Graduated ${edu.year || edu.graduation_year}` : "Graduation year not set"}</span>
                        <span>{edu.gpa ? `GPA ${edu.gpa}` : "GPA not set"}</span>
                      </div>
                      
                      <div className="absolute top-4 right-4 flex items-center gap-2 transition-all">
                        <button onClick={() => handleEditEducationOpen(i)} className="p-2 bg-white/5 border border-white/10 rounded-lg text-[#A1A1AA] hover:text-white hover:bg-white/10 transition-all">
                          <Edit3 className="w-3.5 h-3.5" />
                        </button>
                        <button onClick={() => handleDeleteEducation(i)} className="p-2 bg-white/5 border border-white/10 rounded-lg text-red-400/70 hover:text-red-400 hover:bg-red-400/10 transition-all">
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  ))}
                  {!profile?.education?.length && <p className="text-center text-[#A1A1AA] py-10 w-full col-span-full">No education listed.</p>}
                </div>
              </div>
            )}

            {activeTab === "preferences" && (
                <div className="space-y-6">
                    <div className="flex items-center justify-between">
                        <h2 className="text-lg font-semibold text-white">Job Preferences</h2>
                    </div>
                    <form onSubmit={e => {
                        e.preventDefault();
                        mutUpdate.mutate({
                            desired_roles: prefsForm.desired_roles.split(",").map(r => r.trim()).filter(Boolean),
                            desired_locations: prefsForm.desired_locations.split(",").map(l => l.trim()).filter(Boolean),
                            min_salary: Number(prefsForm.min_salary),
                            preferred_industries: prefsForm.preferred_industries.split(",").map(i => i.trim()).filter(Boolean),
                        });
                    }} className="grid grid-cols-2 gap-6">
                        <div className="col-span-2 space-y-2">
                            <label className="text-xs text-[#A1A1AA]">Desired Roles (comma separated)</label>
                            <input type="text" value={prefsForm.desired_roles} onChange={e => setPrefsForm({ ...prefsForm, desired_roles: e.target.value })} className="w-full bg-[#232327] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-white transition-all" placeholder="Software Engineer, product Manager" />
                        </div>
                        <div className="col-span-2 space-y-2">
                            <label className="text-xs text-[#A1A1AA]">Desired Locations (comma separated)</label>
                            <input type="text" value={prefsForm.desired_locations} onChange={e => setPrefsForm({ ...prefsForm, desired_locations: e.target.value })} className="w-full bg-[#232327] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-white transition-all" placeholder="Remote, Hyderabad, Bangalore" />
                        </div>
                        <div className="col-span-1 space-y-2">
                            <label className="text-xs text-[#A1A1AA]">Minimum Salary (₹/year)</label>
                            <input type="number" value={prefsForm.min_salary} onChange={e => setPrefsForm({ ...prefsForm, min_salary: Number(e.target.value) })} className="w-full bg-[#232327] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-white transition-all" />
                        </div>
                        <div className="col-span-1 space-y-2">
                            <label className="text-xs text-[#A1A1AA]">Preferred Industries</label>
                            <input type="text" value={prefsForm.preferred_industries} onChange={e => setPrefsForm({ ...prefsForm, preferred_industries: e.target.value })} className="w-full bg-[#232327] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-white transition-all" />
                        </div>
                        <div className="col-span-2 flex justify-end pt-4">
                            <button type="submit" disabled={mutUpdate.isPending} className="bg-white text-black px-8 py-2.5 rounded-xl text-sm font-black uppercase tracking-widest hover:bg-gray-200 transition-all shadow-xl">
                                Update Preferences
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {activeTab === "automation" && (
                <div className="space-y-8">
                    <div className="flex items-center justify-between">
                        <h2 className="text-lg font-semibold text-white">Automation Engine</h2>
                    </div>
                    
                    <form onSubmit={e => { e.preventDefault(); mutUpdate.mutate(automationForm); }} className="space-y-8">
                        <div className="flex items-center justify-between p-5 bg-[#232327] border border-white/10 rounded-2xl">
                            <div>
                                <p className="text-sm font-bold text-white mb-1">Autonomous Mode</p>
                                <p className="text-[11px] text-[#A1A1AA]">Let the agent apply automatically based on your score threshold</p>
                            </div>
                            <button 
                                type="button"
                                onClick={() => setAutomationForm({...automationForm, auto_apply_enabled: !automationForm.auto_apply_enabled})}
                                className={cn("w-14 h-7 rounded-full transition-all relative flex items-center px-1", 
                                automationForm.auto_apply_enabled ? "bg-white" : "bg-white/10")}
                            >
                                <motion.div 
                                    className={cn("w-5 h-5 rounded-full shadow-sm", automationForm.auto_apply_enabled ? "bg-black" : "bg-white/40")}
                                    animate={{ x: automationForm.auto_apply_enabled ? 28 : 0 }}
                                />
                            </button>
                        </div>

                        <div className="space-y-4">
                            <div className="flex justify-between items-center text-xs font-bold uppercase tracking-widest text-[#A1A1AA]">
                                <span>Match Threshold</span>
                                <span className="text-white bg-white/5 px-2 py-0.5 rounded">{automationForm.auto_apply_threshold}%</span>
                            </div>
                            <input 
                                type="range" min="0" max="100" 
                                value={automationForm.auto_apply_threshold} 
                                onChange={e => setAutomationForm({...automationForm, auto_apply_threshold: Number(e.target.value)})}
                                className="w-full accent-white h-1.5 bg-white/10 rounded-lg appearance-none cursor-pointer" 
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="text-[10px] font-bold uppercase tracking-widest text-[#A1A1AA]">Telegram Chat ID</label>
                            <input type="text" value={automationForm.telegram_chat_id} onChange={e => setAutomationForm({...automationForm, telegram_chat_id: e.target.value})} className="w-full bg-[#232327] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white" />
                        </div>

                        <div className="flex justify-end pt-4">
                            <button type="submit" disabled={mutUpdate.isPending} className="bg-white text-black px-8 py-3 rounded-xl text-[11px] font-black uppercase tracking-[0.2em] hover:bg-zinc-200 transition-all shadow-2xl">
                                Save Automation Config
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {activeTab === "skills" && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-white">Skills</h2>
                  <button onClick={() => setModalType("skill")} className="bg-white text-black rounded-xl px-4 py-2 text-sm font-medium hover:bg-gray-200 transition-all flex items-center gap-2">
                    <Plus className="w-4 h-4" /> Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-3">
                  {profileSkills?.map((sk: any, i: number) => (
                    <div key={i} className="bg-[#232327] border border-white/10 rounded-full px-4 py-2 flex items-center gap-2 group">
                      <span className="text-xs text-white font-medium">{sk.name}</span>
                      <button 
                        onClick={() => handleDeleteSkill(sk.id)}
                        className="p-0.5 text-[#A1A1AA] hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all"
                        title="Remove skill"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  ))}
                  {!profileSkills?.length && <p className="text-center text-[#A1A1AA] py-10 w-full">No skills listed.</p>}
                </div>
              </div>
            )}


          </motion.div>
        </AnimatePresence>
      </section>

      {/* --- MODALS --- */}
      <AnimatePresence>
        {modalType && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80">
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className={cn(
                "bg-[#1c1c1e] border border-[#262626] rounded-2xl w-full p-6 shadow-2xl space-y-6",
                modalType === "experience" ? "max-w-3xl" : "max-w-lg"
              )}
            >
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white capitalize">{editIndex !== null ? "Edit" : "Add"} {modalType}</h3>
                <button onClick={() => setModalType(null)} className="text-[#A1A1AA] hover:text-white"><X className="w-5 h-5" /></button>
              </div>

              {modalType === "experience" && (
                <form onSubmit={handleAddExperience} className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="sm:col-span-2 space-y-1">
                      <label className="text-xs text-[#A1A1AA]">Job Title</label>
                      <input required type="text" value={expForm.title} onChange={e => setExpForm({...expForm, title: e.target.value})} className="w-full bg-[#232327] border border-[#1C1C24] rounded-xl px-4 py-2.5 text-sm text-white" placeholder="Product Designer" />
                    </div>
                    <div className="sm:col-span-2 space-y-1">
                      <label className="text-xs text-[#A1A1AA]">Company</label>
                      <input required type="text" value={expForm.company} onChange={e => setExpForm({...expForm, company: e.target.value})} className="w-full bg-[#232327] border border-[#1C1C24] rounded-xl px-4 py-2.5 text-sm text-white" placeholder="Google" />
                    </div>
                    <div className="space-y-1">
                      <label className="text-xs text-[#A1A1AA]">Start Period</label>
                      <div className="flex gap-2">
                        <select value={expForm.start_month} onChange={e => setExpForm({...expForm, start_month: e.target.value})} className="w-24 shrink-0 bg-[#232327] border border-[#1C1C24] rounded-xl px-2 py-2.5 text-sm text-white">
                            {["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"].map(m => (
                                <option key={m} value={m}>{new Date(2000, parseInt(m)-1).toLocaleString('en-us', {month:'short'})}</option>
                            ))}
                        </select>
                        <input
                          required
                          type="text"
                          inputMode="numeric"
                          pattern="[0-9]{4}"
                          maxLength={4}
                          value={expForm.start_year}
                          onChange={e => setExpForm({...expForm, start_year: e.target.value.replace(/\D/g, "").slice(0, 4)})}
                          className="w-28 sm:w-32 shrink-0 bg-[#232327] border border-[#1C1C24] rounded-xl px-4 py-2.5 text-sm text-white"
                          placeholder="2023"
                        />
                      </div>
                    </div>
                    <div className="space-y-1">
                      <label className="text-xs text-[#A1A1AA]">End Period</label>
                      {expForm.is_current ? (
                        <div className="w-full bg-[#232327] border border-[#1C1C24] rounded-xl px-4 py-2.5 text-sm text-[#A1A1AA]">
                          Present
                        </div>
                      ) : (
                        <div className="flex gap-2">
                          <select value={expForm.end_month} onChange={e => setExpForm({...expForm, end_month: e.target.value})} className="w-24 shrink-0 bg-[#232327] border border-[#1C1C24] rounded-xl px-2 py-2.5 text-sm text-white">
                              {["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"].map(m => (
                                  <option key={m} value={m}>{new Date(2000, parseInt(m)-1).toLocaleString('en-us', {month:'short'})}</option>
                              ))}
                          </select>
                          <input
                            required
                            type="text"
                            inputMode="numeric"
                            pattern="[0-9]{4}"
                            maxLength={4}
                            value={expForm.end_year}
                            onChange={e => setExpForm({...expForm, end_year: e.target.value.replace(/\D/g, "").slice(0, 4)})}
                            className="w-28 sm:w-32 shrink-0 bg-[#232327] border border-[#1C1C24] rounded-xl px-4 py-2.5 text-sm text-white"
                            placeholder="2024"
                          />
                        </div>
                      )}
                    </div>
                    <label className="sm:col-span-2 flex items-center gap-2 text-xs text-[#A1A1AA] cursor-pointer">
                      <input
                        type="checkbox"
                        checked={expForm.is_current}
                        onChange={e =>
                          setExpForm({
                            ...expForm,
                            is_current: e.target.checked,
                            end_year: e.target.checked ? "" : expForm.end_year,
                          })
                        }
                      />
                      I currently work here
                    </label>
                  </div>
                  <button type="submit" disabled={mutUpdate.isPending} className="w-full bg-white text-black py-3 rounded-xl font-bold flex items-center justify-center gap-2">
                    {mutUpdate.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : (editIndex !== null ? <Save className="w-4 h-4" /> : <Plus className="w-4 h-4" />)}
                    {editIndex !== null ? "Update Experience" : "Add Experience"}
                  </button>
                </form>
              )}

              {modalType === "education" && (
                <form onSubmit={handleAddEducation} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="col-span-2 space-y-1">
                      <label className="text-xs text-[#A1A1AA]">Degree</label>
                      <input required type="text" value={eduForm.degree} onChange={e => setEduForm({...eduForm, degree: e.target.value})} className="w-full bg-[#232327] border border-[#1C1C24] rounded-xl px-4 py-2.5 text-sm text-white" />
                    </div>
                    <div className="col-span-2 space-y-1">
                      <label className="text-xs text-[#A1A1AA]">Institution</label>
                      <input required type="text" value={eduForm.institution} onChange={e => setEduForm({...eduForm, institution: e.target.value})} className="w-full bg-[#232327] border border-[#1C1C24] rounded-xl px-4 py-2.5 text-sm text-white" />
                    </div>
                    <div className="space-y-1">
                      <label className="text-xs text-[#A1A1AA]">Grad Year</label>
                      <input required type="number" value={eduForm.graduation_year} onChange={e => setEduForm({...eduForm, graduation_year: e.target.value})} className="w-full bg-[#232327] border border-[#1C1C24] rounded-xl px-4 py-2.5 text-sm text-white" />
                    </div>
                    <div className="space-y-1">
                      <label className="text-xs text-[#A1A1AA]">GPA</label>
                      <input required type="text" value={eduForm.gpa} onChange={e => setEduForm({...eduForm, gpa: e.target.value})} className="w-full bg-[#232327] border border-[#1C1C24] rounded-xl px-4 py-2.5 text-sm text-white" />
                    </div>
                  </div>
                  <button type="submit" disabled={mutUpdate.isPending} className="w-full bg-white text-black py-3 rounded-xl font-bold flex items-center justify-center gap-2">
                    {mutUpdate.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : (editIndex !== null ? <Save className="w-4 h-4" /> : <Plus className="w-4 h-4" />)}
                    {editIndex !== null ? "Update Education" : "Add Education"}
                  </button>
                </form>
              )}

              {modalType === "skill" && (
                <form onSubmit={handleAddSkill} className="space-y-4">
                  <div className="space-y-1">
                    <label className="text-xs text-[#A1A1AA]">Skill Name</label>
                    <input required type="text" value={skillForm.name} onChange={e => setSkillForm({...skillForm, name: e.target.value})} className="w-full bg-[#232327] border border-[#1C1C24] rounded-xl px-4 py-2.5 text-sm text-white" placeholder="React.js" />
                  </div>
                  {sessionAddedSkills.length > 0 && (
                    <div className="space-y-2">
                      <label className="text-xs text-[#A1A1AA]">Added Now</label>
                      <div className="flex flex-wrap gap-2">
                        {sessionAddedSkills.map((s) => (
                          <span key={s} className="px-3 py-1.5 rounded-full text-xs font-semibold bg-white text-black">{s}</span>
                        ))}
                      </div>
                    </div>
                  )}
                  <div className="space-y-2">
                    <label className="text-xs text-[#A1A1AA]">Recommended Skills (Universal)</label>
                    <div className="flex flex-wrap gap-2 max-h-44 overflow-y-auto pr-1">
                      {UNIVERSAL_SKILLS.filter((s) =>
                        !skillForm.name || s.toLowerCase().includes(skillForm.name.toLowerCase())
                      )
                        .sort((a, b) => {
                          const q = skillForm.name.toLowerCase();
                          const aStarts = q ? a.toLowerCase().startsWith(q) : false;
                          const bStarts = q ? b.toLowerCase().startsWith(q) : false;
                          if (aStarts && !bStarts) return -1;
                          if (!aStarts && bStarts) return 1;
                          return a.localeCompare(b);
                        })
                        .map((s) => {
                          const existsInProfile = profileSkills.some((ps: any) => ps.name?.toLowerCase() === s.toLowerCase());
                          const existsInSession = sessionAddedSkills.some((added) => added.toLowerCase() === s.toLowerCase());
                          const isAdded = existsInProfile || existsInSession;

                          return (
                            <button
                              key={s}
                              type="button"
                              onClick={() => !isAdded && setSkillForm({ name: s })}
                              className={cn(
                                "px-3 py-1.5 rounded-full text-xs font-semibold border transition-all",
                                isAdded
                                  ? "bg-white/10 border-white/10 text-white/40 cursor-not-allowed"
                                  : "bg-[#232327] border-[#1C1C24] text-[#A1A1AA] hover:text-white"
                              )}
                              title={isAdded ? "Already added" : "Click to use this skill"}
                            >
                              {s}
                            </button>
                          );
                        })}
                    </div>
                  </div>
                  <button type="submit" disabled={mutAddSkill.isPending} className="w-full bg-white text-black py-3 rounded-xl font-bold flex items-center justify-center gap-2 pt-4">
                    {mutAddSkill.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                    Add Skill And Continue
                  </button>
                </form>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}


