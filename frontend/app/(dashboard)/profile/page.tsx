"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { profileApi } from "@/lib/api";
import { toast } from "sonner";
import { User as UserIcon, Briefcase, GraduationCap, Code, Edit3, Plus, X, Link } from "lucide-react";
import { cn } from "@/lib/utils";

export default function ProfilePage() {
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState("basic");
  
  const { data: profile, isLoading } = useQuery({
    queryKey: ["profile"],
    queryFn: () => profileApi.get().then(r => r.data),
  });

  const [editBasic, setEditBasic] = useState(false);
  const [basicForm, setBasicForm] = useState({ full_name: "", professional_summary: "", unique_value_proposition: "" });

  const mutBasic = useMutation({
    mutationFn: (d: any) => profileApi.update({ ...profile, basic_info: d }),
    onSuccess: () => { toast.success("Updated!"); setEditBasic(false); qc.invalidateQueries({ queryKey: ["profile"] }); }
  });

  if (isLoading) return <div className="skeleton h-[500px] rounded-xl" />;

  const handleEditBasicOpen = () => {
    setBasicForm({
      full_name: profile?.basic_info?.full_name || "",
      professional_summary: profile?.basic_info?.professional_summary || "",
      unique_value_proposition: profile?.basic_info?.unique_value_proposition || "",
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
                <div><label className="block text-xs text-muted-foreground mb-1">Professional Summary</label><textarea rows={4} value={basicForm.professional_summary} onChange={e => setBasicForm({ ...basicForm, professional_summary: e.target.value })} className="w-full bg-muted border border-border px-3 py-2 rounded-lg text-sm resize-none" /></div>
                <div><label className="block text-xs text-muted-foreground mb-1">Unique Value Proposition</label><textarea rows={3} value={basicForm.unique_value_proposition} onChange={e => setBasicForm({ ...basicForm, unique_value_proposition: e.target.value })} className="w-full bg-muted border border-border px-3 py-2 rounded-lg text-sm resize-none" /></div>
                <div className="flex justify-end gap-2 pt-2">
                  <button type="button" onClick={() => setEditBasic(false)} className="px-4 py-2 glass rounded-lg text-sm">Cancel</button>
                  <button type="submit" disabled={mutBasic.isPending} className="px-4 py-2 bg-brand-purple text-white rounded-lg text-sm">Save</button>
                </div>
              </form>
            ) : (
              <div className="space-y-4">
                <div><p className="text-xs text-muted-foreground">Full Name</p><p className="font-medium">{profile?.basic_info?.full_name || "—"}</p></div>
                <div><p className="text-xs text-muted-foreground">Professional Summary</p><p className="text-sm whitespace-pre-wrap">{profile?.basic_info?.professional_summary || "—"}</p></div>
                <div><p className="text-xs text-muted-foreground">Unique Value Proposition</p><p className="text-sm whitespace-pre-wrap">{profile?.basic_info?.unique_value_proposition || "—"}</p></div>
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
      </div>
    </div>
  );
}
