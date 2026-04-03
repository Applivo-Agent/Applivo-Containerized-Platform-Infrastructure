"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { resumesApi } from "@/lib/api";
import { useSubscription } from "@/lib/subscription";
import { cn, formatDate } from "@/lib/utils";
import { toast } from "sonner";
import { useDropzone } from "react-dropzone";
import { FileText, Upload, Plus, Download, Eye, Star, Trash2, CheckCircle2, ChevronDown, Lock } from "lucide-react";
import Link from "next/link";

export default function ResumesPage() {
  const qc = useQueryClient();
  const { isPro, isPremium } = useSubscription();

  const { data: resumes, isLoading } = useQuery({ queryKey: ["resumes"], queryFn: () => resumesApi.list().then(r => r.data) });
  const { data: templates } = useQuery({ queryKey: ["latex-templates"], queryFn: () => resumesApi.getLatexTemplates().then(r => r.data) });

  const [uploadOpen, setUploadOpen] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { "application/pdf": [".pdf"] }, maxFiles: 1,
    onDrop: (f) => setFile(f[0]),
  });

  const uploadMut = useMutation({
    mutationFn: () => {
      const fd = new FormData();
      fd.append("file", file!);
      fd.append("name", file!.name.replace(".pdf", ""));
      return resumesApi.upload(fd);
    },
    onSuccess: () => { toast.success("Uploaded & Parsed!"); setFile(null); setUploadOpen(false); qc.invalidateQueries({ queryKey: ["resumes"] }); },
    onError: () => toast.error("Failed to upload"),
    onSettled: () => setIsUploading(false),
  });

  const setDefault = useMutation({
    mutationFn: (id: string) => resumesApi.setDefault(id),
    onSuccess: () => { toast.success("Default resume updated"); qc.invalidateQueries({ queryKey: ["resumes"] }); }
  });

  const selectTemplate = useMutation({
    mutationFn: (name: string) => resumesApi.selectLatexTemplate(name),
    onSuccess: () => { toast.success("LaTeX Template changed"); qc.invalidateQueries({ queryKey: ["latex-templates"] }); },
  });

  const handleUpload = () => { if (file) { setIsUploading(true); uploadMut.mutate(); } };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold font-display">Resumes & Templates</h1>
          <p className="text-muted-foreground text-sm mt-1">Manage your base PDFs and AI generation templates</p>
        </div>
        <button onClick={() => setUploadOpen(true)} className="px-4 py-2 bg-brand-purple text-white rounded-lg text-sm font-medium hover:bg-brand-purple/90 flex gap-2 items-center">
           <Upload className="w-4 h-4" /> Upload Base PDF
        </button>
      </div>

      {uploadOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm" onClick={() => !isUploading && setUploadOpen(false)}>
           <div className="glass-card p-6 w-full max-w-md" onClick={e => e.stopPropagation()}>
             <h3 className="font-semibold mb-4">Upload Base Resume</h3>
             <div {...getRootProps()} className={cn("border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors", isDragActive ? "border-brand-purple bg-brand-purple/10" : "border-border hover:border-brand-purple/50")}>
               <input {...getInputProps()} />
               <Upload className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
               {file ? <p className="text-brand-green font-medium text-sm">{file.name}</p> : <p className="text-sm">Drag & drop PDF here, or click to select</p>}
             </div>
             <div className="flex justify-end gap-3 mt-6">
                <button onClick={() => setUploadOpen(false)} disabled={isUploading} className="px-4 py-2 glass rounded-lg text-sm">Cancel</button>
                <button onClick={handleUpload} disabled={!file || isUploading} className="px-4 py-2 bg-brand-purple text-white rounded-lg text-sm disabled:opacity-50 flex items-center gap-2">
                   {isUploading ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : "Upload & Parse"}
                </button>
             </div>
           </div>
        </div>
      )}

      {/* Resumes List */}
      <div className="glass-card p-6">
        <h2 className="font-semibold mb-4">Your Resumes</h2>
        {isLoading ? (
           <div className="space-y-3">{[1,2].map(i => <div key={i} className="skeleton h-20 rounded-xl" />)}</div>
        ) : (
           <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {resumes?.map((res: any) => (
                 <div key={res.id} className={cn("p-4 rounded-xl border transition-all", res.is_default ? "bg-brand-purple/5 border-brand-purple/30" : "glass hover:bg-white/5 border-transparent")}>
                    <div className="flex justify-between items-start mb-3">
                       <div className="flex items-center gap-3">
                          <div className={cn("w-10 h-10 rounded-lg flex items-center justify-center", res.is_default ? "bg-brand-purple" : "bg-muted text-muted-foreground")}>
                             <FileText className="w-5 h-5 text-white" />
                          </div>
                          <div>
                             <p className="font-medium text-sm truncate pr-2 max-w-[150px]">{res.name}</p>
                             <p className="text-[10px] text-muted-foreground">{formatDate(res.created_at)}</p>
                          </div>
                       </div>
                       {res.is_default && <span className="bg-brand-purple/20 text-brand-purple-light px-2 py-0.5 rounded text-[10px] font-bold">DEFAULT</span>}
                    </div>
                    <div className="flex items-center gap-2 mt-4">
                       {!res.is_default && (
                          <button onClick={() => setDefault.mutate(res.id)} className="flex-1 py-1.5 px-2 bg-muted/50 rounded-md text-xs hover:bg-muted transition-colors flex items-center justify-center gap-1.5">
                            <Star className="w-3 h-3" /> Set Default
                          </button>
                       )}
                       <a href={res.s3_url || "#"} target="_blank" rel="noopener noreferrer" className={cn("py-1.5 px-2 bg-muted/50 rounded-md text-xs hover:bg-muted transition-colors flex items-center justify-center gap-1.5", res.is_default ? "flex-1" : "")}>
                          <Download className="w-3 h-3" /> PDF
                       </a>
                    </div>
                 </div>
              ))}
              {resumes?.length === 0 && <div className="col-span-full py-8 text-center text-muted-foreground"><FileText className="w-8 h-8 opacity-50 mx-auto mb-2" /><p className="text-sm">No resumes uploaded.</p></div>}
           </div>
        )}
      </div>

      {/* Templates List */}
      <div className="glass-card p-6">
        <div className="mb-6">
           <h2 className="font-semibold text-lg flex items-center gap-2">LaTeX Output Templates <span className="px-2 py-0.5 bg-brand-purple/20 text-brand-purple-light rounded-full text-[10px] font-bold">AI GEN</span></h2>
           <p className="text-sm text-muted-foreground mt-1">When the bot applies, it dynamically injects ATS keywords into your profile data and compiles one of these templates.</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-5">
           {templates?.available?.map((tpl: any) => {
              const isSelected = templates.selected === tpl.name;
              const isLocked = tpl.tier !== "starter" && tpl.tier === "premium" && !isPremium || tpl.tier === "pro" && !isPro && !isPremium;

              return (
                 <div key={tpl.name} className={cn("relative group rounded-xl overflow-hidden border-2 transition-all cursor-pointer", isSelected ? "border-brand-purple shadow-lg shadow-brand-purple/20" : "border-border/50 hover:border-brand-purple/50")} onClick={() => !isLocked && selectTemplate.mutate(tpl.name)}>
                    <div className="aspect-[1/1.4] bg-muted/30 p-2">
                       <img src={tpl.preview_img_url} alt={tpl.name} className={cn("w-full h-full object-cover rounded shadow-sm opacity-80 group-hover:opacity-100 transition-opacity", isLocked ? "blur-[2px] opacity-40 grayscale" : "")} />
                    </div>
                    {isLocked && (
                       <div className="absolute inset-0 flex flex-col items-center justify-center bg-background/50 backdrop-blur-[2px]">
                          <Lock className="w-6 h-6 text-amber-400 mb-2" />
                          <span className="text-xs font-bold px-2 py-1 bg-amber-500/20 text-amber-400 rounded-full capitalize">{tpl.tier} Plan</span>
                       </div>
                    )}
                    <div className="absolute bottom-0 inset-x-0 p-3 bg-background/90 backdrop-blur flex items-center justify-between border-t border-border">
                       <div>
                          <p className="font-medium text-sm capitalize">{tpl.name.replace("-", " ")}</p>
                          <p className="text-[10px] text-muted-foreground">{tpl.description}</p>
                       </div>
                       {isSelected ? <CheckCircle2 className="w-5 h-5 text-brand-purple-light" /> : <div className="w-5 h-5 rounded-full border-2 border-muted-foreground/30 group-hover:border-brand-purple/50" />}
                    </div>
                 </div>
              );
           })}
        </div>
      </div>
    </div>
  );
}
