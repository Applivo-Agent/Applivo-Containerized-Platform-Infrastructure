"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { profileApi, api } from "@/lib/api";
import { toast } from "sonner";
import { User as UserIcon, Briefcase, GraduationCap, Code, Edit3, Plus, X, Link, Laptop, Smartphone, Monitor, LogOut, Trash2, RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";

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

export default function ProfilePage() {
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState("basic");
  
  const { data: profile, isLoading } = useQuery({
    queryKey: ["profile"],
    queryFn: () => profileApi.get().then(r => r.data),
  });

  const [editBasic, setEditBasic] = useState(false);
  const [basicForm, setBasicForm] = useState({ 
    full_name: "", 
    professional_summary: "", 
    unique_value_proposition: "",
    desired_roles: [] as string[],
    experience_level: "",
    location: "",
  });

  const mutBasic = useMutation({
    mutationFn: (d: any) => profileApi.update({ 
      ...profile, 
      basic_info: {
        full_name: d.full_name,
        professional_summary: d.professional_summary,
        unique_value_proposition: d.unique_value_proposition,
      },
      desired_roles: d.desired_roles,
      experience_level: d.experience_level,
      location: d.location,
    }),
    onSuccess: () => { toast.success("Updated!"); setEditBasic(false); qc.invalidateQueries({ queryKey: ["profile"] }); }
  });

  if (isLoading) return <div className="skeleton h-[500px] rounded-xl" />;

  const handleEditBasicOpen = () => {
    setBasicForm({
      full_name: profile?.full_name || profile?.basic_info?.full_name || "",
      professional_summary: profile?.professional_summary || profile?.basic_info?.professional_summary || "",
      unique_value_proposition: profile?.unique_value_proposition || profile?.basic_info?.unique_value_proposition || "",
      desired_roles: profile?.desired_roles || [],
      experience_level: profile?.experience_level || "",
      location: profile?.location || "",
    });
    setEditBasic(true);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold font-display">Your Profile</h1>
        <p className="text-muted-foreground text-sm mt-1">This data is injected into your AI resume tailoring pipeline.</p>
      </div>

      {/* Tabs */}
      <div className="flex bg-muted/30 p-1 rounded-lg w-max">
        {[
          { id: "basic", label: "Basic Info", icon: UserIcon },
          { id: "experience", label: "Experience", icon: Briefcase },
          { id: "education", label: "Education", icon: GraduationCap },
          { id: "skills", label: "Skills", icon: Code },
          { id: "security", label: "Security", icon: LogOut },
        ].map(t => (
          <button key={t.id} onClick={() => setActiveTab(t.id)}
            className={cn("flex items-center gap-2 px-4 py-2 rounded-md text-sm transition-all", activeTab === t.id ? "bg-background shadow font-medium text-brand-purple-light" : "text-muted-foreground hover:text-foreground text-sm")}>
            <t.icon className="w-4 h-4" /> {t.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="glass-card p-6">
        {activeTab === "basic" && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="font-semibold text-lg flex items-center gap-2"><UserIcon className="w-5 h-5 text-brand-purple-light" /> Basic Information</h2>
              {!editBasic && <button onClick={handleEditBasicOpen} className="p-2 glass rounded-lg hover:bg-white/5"><Edit3 className="w-4 h-4" /></button>}
            </div>

            {editBasic ? (
              <form onSubmit={e => { e.preventDefault(); mutBasic.mutate(basicForm); }} className="space-y-4">
                <div><label className="block text-xs text-muted-foreground mb-1">Full Name</label><input type="text" value={basicForm.full_name} onChange={e => setBasicForm({ ...basicForm, full_name: e.target.value })} className="w-full bg-muted border border-border px-3 py-2 rounded-lg text-sm" /></div>
                <div><label className="block text-xs text-muted-foreground mb-1">Experience Level</label>
                  <select value={basicForm.experience_level} onChange={e => setBasicForm({ ...basicForm, experience_level: e.target.value })} className="w-full bg-muted border border-border px-3 py-2 rounded-lg text-sm">
                    <option value="">Select level</option>
                    <option value="fresher">Fresher</option>
                    <option value="junior">Junior (1-2 years)</option>
                    <option value="mid">Mid-level (3-5 years)</option>
                    <option value="senior">Senior (5+ years)</option>
                  </select>
                </div>
                <div><label className="block text-xs text-muted-foreground mb-1">Location</label><input type="text" value={basicForm.location} onChange={e => setBasicForm({ ...basicForm, location: e.target.value })} className="w-full bg-muted border border-border px-3 py-2 rounded-lg text-sm" placeholder="e.g., Bangalore, Remote" /></div>
                <div><label className="block text-xs text-muted-foreground mb-1">Desired Roles (comma separated)</label><input type="text" value={basicForm.desired_roles.join(", ")} onChange={e => setBasicForm({ ...basicForm, desired_roles: e.target.value.split(",").map(s => s.trim()).filter(Boolean) })} className="w-full bg-muted border border-border px-3 py-2 rounded-lg text-sm" placeholder="e.g., Machine Learning, Data Scientist" /></div>
                <div><label className="block text-xs text-muted-foreground mb-1">Professional Summary</label><textarea rows={4} value={basicForm.professional_summary} onChange={e => setBasicForm({ ...basicForm, professional_summary: e.target.value })} className="w-full bg-muted border border-border px-3 py-2 rounded-lg text-sm resize-none" /></div>
                <div><label className="block text-xs text-muted-foreground mb-1">Unique Value Proposition</label><textarea rows={3} value={basicForm.unique_value_proposition} onChange={e => setBasicForm({ ...basicForm, unique_value_proposition: e.target.value })} className="w-full bg-muted border border-border px-3 py-2 rounded-lg text-sm resize-none" /></div>
                <div className="flex justify-end gap-2 pt-2">
                  <button type="button" onClick={() => setEditBasic(false)} className="px-4 py-2 glass rounded-lg text-sm">Cancel</button>
                  <button type="submit" disabled={mutBasic.isPending} className="px-4 py-2 bg-brand-purple text-white rounded-lg text-sm">Save</button>
                </div>
              </form>
            ) : (
              <div className="space-y-4">
                <div><p className="text-xs text-muted-foreground">Full Name</p><p className="font-medium">{profile?.full_name || profile?.basic_info?.full_name || "—"}</p></div>
                <div><p className="text-xs text-muted-foreground">Experience Level</p><p className="font-medium capitalize">{profile?.experience_level || "—"}</p></div>
                <div><p className="text-xs text-muted-foreground">Location</p><p className="font-medium">{profile?.location || "—"}</p></div>
                <div><p className="text-xs text-muted-foreground">Desired Roles</p><div className="flex flex-wrap gap-1 mt-1">{profile?.desired_roles?.length ? profile.desired_roles.map((r: string) => <span key={r} className="px-2 py-0.5 bg-brand-purple/20 text-brand-purple-light text-xs rounded-full">{r}</span>) : "—"}</div></div>
                <div><p className="text-xs text-muted-foreground">Professional Summary</p><p className="text-sm whitespace-pre-wrap">{profile?.professional_summary || profile?.basic_info?.professional_summary || "—"}</p></div>
                <div><p className="text-xs text-muted-foreground">Unique Value Proposition</p><p className="text-sm whitespace-pre-wrap">{profile?.unique_value_proposition || profile?.basic_info?.unique_value_proposition || "—"}</p></div>
              </div>
            )}
          </div>
        )}

        {activeTab === "experience" && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="font-semibold text-lg flex items-center gap-2"><Briefcase className="w-5 h-5 text-brand-purple-light" /> Work Experience</h2>
              <button disabled className="flex items-center gap-1 text-sm bg-brand-purple text-white px-3 py-1.5 rounded-lg opacity-50"><Plus className="w-4 h-4" /> Add</button>
            </div>
            <div className="space-y-4">
              {profile?.work_experience?.map((exp: any, i: number) => (
                <div key={i} className="p-4 bg-muted/30 rounded-lg relative group border border-border/50">
                  <p className="font-semibold">{exp.title}</p>
                  <p className="text-sm text-brand-purple-light">{exp.company}</p>
                  <p className="text-xs text-muted-foreground mt-1">{exp.start_date} – {exp.is_current ? "Present" : exp.end_date}</p>
                  <p className="text-sm mt-3 text-muted-foreground whitespace-pre-wrap">{exp.description}</p>
                </div>
              ))}
              {!profile?.work_experience?.length && <p className="text-sm text-muted-foreground">No experience listed.</p>}
            </div>
          </div>
        )}

        {activeTab === "education" && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="font-semibold text-lg flex items-center gap-2"><GraduationCap className="w-5 h-5 text-brand-purple-light" /> Education</h2>
              <button disabled className="flex items-center gap-1 text-sm bg-brand-purple text-white px-3 py-1.5 rounded-lg opacity-50"><Plus className="w-4 h-4" /> Add</button>
            </div>
            <div className="space-y-4">
              {profile?.education?.map((edu: any, i: number) => (
                <div key={i} className="p-4 bg-muted/30 rounded-lg border border-border/50">
                  <p className="font-semibold">{edu.degree} in {edu.field}</p>
                  <p className="text-sm text-brand-purple-light">{edu.institution}</p>
                  <p className="text-xs text-muted-foreground mt-1">Graduated: {edu.graduation_year} • GPA: {edu.gpa}</p>
                </div>
              ))}
              {!profile?.education?.length && <p className="text-sm text-muted-foreground">No education listed.</p>}
            </div>
          </div>
        )}

        {activeTab === "skills" && (
           <div className="space-y-6">
             <div className="flex items-center justify-between">
                <h2 className="font-semibold text-lg flex items-center gap-2"><Code className="w-5 h-5 text-brand-purple-light" /> Skills</h2>
             </div>
             <div className="flex flex-wrap gap-2">
               {profile?.skills?.map((sk: any, i: number) => (
                 <div key={i} className="flex flex-col items-center p-3 bg-muted/40 rounded-xl border border-border/50 min-w-[100px]">
                   <span className="font-medium text-sm capitalize">{sk.name}</span>
                   <span className="text-[10px] text-muted-foreground capitalize mt-1 border border-border px-2 py-0.5 rounded-full bg-background">{sk.proficiency}</span>
                 </div>
               ))}
               {!profile?.skills?.length && <p className="text-sm text-muted-foreground">No skills listed.</p>}
             </div>
           </div>
        )}

        {activeTab === "security" && <SecurityTab />}
      </div>
    </div>
  );
}

function SecurityTab() {
  const qc = useQueryClient();
  
  const { data: sessions, isLoading, refetch } = useQuery({
    queryKey: ["sessions"],
    queryFn: () => api.get("/auth/sessions").then(r => r.data),
  });

  const revokeMutation = useMutation({
    mutationFn: (sessionId: string) => api.delete(`/auth/sessions/${sessionId}`),
    onSuccess: () => { toast.success("Session revoked"); qc.invalidateQueries({ queryKey: ["sessions"] }); },
    onError: () => toast.error("Failed to revoke session"),
  });

  const revokeAllMutation = useMutation({
    mutationFn: () => api.delete("/auth/sessions"),
    onSuccess: () => { toast.success("All other sessions logged out"); qc.invalidateQueries({ queryKey: ["sessions"] }); },
    onError: () => toast.error("Failed to revoke sessions"),
  });

  const getDeviceIcon = (deviceType: string | null) => {
    if (deviceType === "mobile") return <Smartphone className="w-5 h-5" />;
    if (deviceType === "desktop") return <Monitor className="w-5 h-5" />;
    return <Laptop className="w-5 h-5" />;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="font-semibold text-lg flex items-center gap-2"><LogOut className="w-5 h-5 text-brand-purple-light" /> Active Sessions</h2>
        <button 
          onClick={() => revokeAllMutation.mutate()} 
          disabled={revokeAllMutation.isPending}
          className="flex items-center gap-2 text-sm text-red-400 hover:text-red-300"
        >
          <LogOut className="w-4 h-4" />
          Logout All Other Devices
        </button>
      </div>

      <p className="text-sm text-muted-foreground">Manage your active sessions. You can revoke any session except your current one.</p>

      {isLoading ? (
        <div className="space-y-3">
          {[1,2,3].map(i => <div key={i} className="h-20 bg-muted/30 rounded-lg animate-pulse" />)}
        </div>
      ) : (
        <div className="space-y-3">
          {sessions?.map((session: Session) => (
            <div key={session.id} className="flex items-center justify-between p-4 bg-muted/30 rounded-lg border border-border/50">
              <div className="flex items-center gap-4">
                <div className="p-2 bg-brand-purple/20 rounded-lg text-brand-purple-light">
                  {getDeviceIcon(session.device_type)}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{session.device_name || "Unknown Device"}</span>
                    {session.is_current && <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 text-xs rounded-full">Current</span>}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {session.browser && `${session.browser} on ${session.os}`}
                    {session.ip_address && ` • ${session.ip_address}`}
                    {session.location && ` • ${session.location}`}
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {session.last_used_at ? `Last used: ${new Date(session.last_used_at).toLocaleString()}` : `Created: ${new Date(session.created_at).toLocaleString()}`}
                  </div>
                </div>
              </div>
              {!session.is_current && (
                <button
                  onClick={() => revokeMutation.mutate(session.id)}
                  disabled={revokeMutation.isPending}
                  className="p-2 hover:bg-red-500/20 rounded-lg text-red-400"
                  title="Revoke session"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
            </div>
          ))}
          {!sessions?.length && <p className="text-muted-foreground text-center py-8">No active sessions found.</p>}
        </div>
      )}

      {/* Refresh Token Info */}
      <div className="glass-card p-6">
        <div className="flex items-center gap-2 mb-2">
          <RefreshCw className="w-5 h-5 text-brand-purple-light" />
          <h3 className="font-semibold">Token Security</h3>
        </div>
        <p className="text-sm text-muted-foreground">
          Access tokens expire after 30 minutes. Use the refresh token to get a new access token without logging in again.
          Each device login creates a new session with its own refresh token.
        </p>
      </div>
    </div>
  );
}
