"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { resumesApi } from "@/lib/api";
import { useSubscription } from "@/lib/subscription";
import { cn, formatDate } from "@/lib/utils";
import { toast } from "sonner";
import { motion } from "framer-motion";
import { useDropzone } from "react-dropzone";
import { FileText, Upload, Plus, Download, Eye, Star, Trash2, Check, ChevronDown, Lock , Loader2} from "lucide-react";
import Link from "next/link";
import axios from "axios";

export default function ResumesPage() {
  const qc = useQueryClient();
  const { isPro, isPremium } = useSubscription();
  
  const downloadResume = async (id: string, filename: string) => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get(`/api/resumes/${id}/file`, {
        headers: { Authorization: `Bearer ${token}` },
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename || "resume.pdf");
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      toast.error("Failed to download resume");
    }
  };

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
    onSuccess: () => {
      toast.success("Resume uploaded");
      setFile(null);
      setUploadOpen(false);
      qc.invalidateQueries({ queryKey: ["resumes"] });
    },
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
  
  const deleteMut = useMutation({
    mutationFn: (id: string) => resumesApi.delete(id),
    onSuccess: () => { 
      toast.success("Resume deleted"); 
      qc.invalidateQueries({ queryKey: ["resumes"] }); 
    },
    onError: (err: any) => toast.error(err.response?.data?.detail || "Failed to delete resume"),
  });

  const handleUpload = () => { if (file) { setIsUploading(true); uploadMut.mutate(); } };

  const resumeCount = resumes?.length || 0;
  const isAtLimit = resumeCount >= 3;

  return (
    <div className="dash-page">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-[#242424] border border-white/[0.08] rounded-lg">
          <FileText className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-white flex items-center gap-2.5">
            Resumes & Templates.
            <span className={cn("px-2.5 py-1 rounded-full text-[10px] font-black tracking-widest uppercase", isAtLimit ? "bg-red-500/10 text-red-400 border border-red-500/20" : "bg-white/5 text-zinc-400 border border-white/10")}>
              {resumeCount}/3 RESUMES
            </span>
          </h1>
          <p className="text-sm text-zinc-400 mt-1">Manage your baseline PDF files and choose AI generation templates for your automated applications.</p>
        </div>
        <button 
          onClick={() => setUploadOpen(true)} 
          disabled={isAtLimit}
          className="px-4 py-2 bg-white text-black rounded-lg text-sm font-medium hover:bg-zinc-200 transition-all flex gap-2 items-center disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-white/5"
        >
           <Plus className={cn("w-5 h-5", isAtLimit ? "text-zinc-500" : "text-black")} />
           <span>{isAtLimit ? "Limit Reached" : "Upload Baseline"}</span>
        </button>
      </div>

      {uploadOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm" onClick={() => !isUploading && setUploadOpen(false)}>
           <div className="-card p-6 w-full max-w-md" onClick={e => e.stopPropagation()}>
             <h3 className="font-semibold mb-4">Upload Base Resume</h3>
              <div {...getRootProps()} className={cn(
                "border rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 relative overflow-hidden group",
                isDragActive 
                  ? "border-white bg-white/5 shadow-[0_0_20px_rgba(255,255,255,0.05)]" 
                  : "border-white/5 bg-[#0b0b0f] hover:border-white/20"
              )}>
                <input {...getInputProps()} />
                <div className="w-12 h-12 rounded-full bg-white/[0.02] border border-white/5 flex items-center justify-center mx-auto mb-4 group-hover:bg-white/[0.05] transition-colors">
                  <Upload className="w-5 h-5 text-zinc-600 group-hover:text-zinc-400 transition-colors" />
                </div>
                {file ? (
                  <p className="text-white font-black uppercase tracking-widest text-[10px]">{file.name}</p>
                ) : (
                  <>
                    <p className="text-[11px] font-black uppercase tracking-[0.2em] text-zinc-500 mb-1">Baseline Deployment</p>
                    <p className="text-[10px] font-bold text-zinc-700 uppercase tracking-wider italic">Drag PDF here or click to initialize</p>
                  </>
                )}
              </div>
             <div className="flex justify-end gap-3 mt-6">
                <button onClick={() => setUploadOpen(false)} disabled={isUploading} className="px-4 py-2  rounded-lg text-sm">Cancel</button>
                <button onClick={handleUpload} disabled={!file || isUploading} className="px-5 py-2 bg-white text-black rounded-lg text-sm disabled:opacity-80 disabled:cursor-not-allowed flex items-center gap-2 font-bold transition-all shadow-lg shadow-white/5">
                     {isUploading ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : "Upload Resume"}
                </button>
             </div>
           </div>
        </div>
      )}

      {/* Resumes List */}
      <div className="dash-card p-4 md:p-5">
        <div className="flex items-center justify-between mb-5 border-b border-white/5 pb-4">
          <h2 className="text-lg font-bold text-white flex items-center gap-2.5">
             <FileText className="w-5 h-5 text-serious-lavender fill-white/10 stroke-white" />
             Base Documents
          </h2>
        </div>
        
        {isLoading ? (
           <div className="grid grid-cols-1 md:grid-cols-2 gap-6">{[1,2].map(i => <div key={i} className="skeleton h-32 rounded-[2rem]" />)}</div>
        ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {resumes?.map((res: any) => (
                <div key={res.id} className={cn("p-4 rounded-xl border transition-all flex flex-col group", res.is_default ? "bg-gradient-to-br from-white/10 via-white/5 to-transparent/30 border-serious-lavender" : "bg-white/5 border-white/5 hover:bg-[#1c1c1e] hover:border-white/10 shadow-sm")}>
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex items-center gap-3">
                      <div className={cn("w-11 h-11 rounded-xl flex items-center justify-center shadow-sm", res.is_default ? "bg-white text-black" : "bg-[#1c1c1e] border border-white/5 text-zinc-400")}>
                        <FileText className={cn("w-5 h-5", res.is_default ? "text-black" : "text-zinc-400")} />
                          </div>
                          <div>
                        <p className="font-black text-sm text-white truncate pr-2 max-w-[150px] tracking-tight">{res.name}</p>
                             <p className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest">{formatDate(res.created_at)}</p>
                          </div>
                       </div>
                    {res.is_default && <span className="bg-white text-black px-2.5 py-1 rounded-full text-[8px] font-black tracking-widest">PRIMARY</span>}
                    </div>
                  <div className="flex items-center gap-2 mt-auto pt-4 border-t border-white/10/50">
                       {!res.is_default && (
                         <>
                          <button onClick={() => setDefault.mutate(res.id)} className="flex-1 py-2.5 px-3 bg-[#1c1c1e] border border-white/10 rounded-xl text-[9px] font-black uppercase tracking-widest text-zinc-400 hover:bg-white hover:text-black transition-all shadow-sm">
                                Primary
                             </button>
                          <button 
                            onClick={() => {
                              if (confirm("Are you sure you want to delete this resume?")) {
                                deleteMut.mutate(res.id);
                              }
                            }}
                            className="p-2.5 bg-[#1c1c1e] border border-white/10 rounded-xl text-zinc-500 hover:bg-red-500 transition-all shadow-sm"
                            title="Delete Resume"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                         </>
                       )}
                    <button onClick={() => downloadResume(res.id, `${res.name || 'resume'}.pdf`)} className={cn("py-2.5 px-3 bg-[#1c1c1e] border border-white/10 rounded-xl text-[9px] font-black uppercase tracking-widest text-zinc-400 hover:bg-white hover:text-black transition-all shadow-sm flex items-center justify-center gap-2", res.is_default ? "flex-1" : "")}>
                          <Download className="w-3.5 h-3.5" /> <span>Download</span>
                       </button>
                    </div>
                 </div>
              ))}
              {resumes?.length === 0 && (
               <div className="col-span-full min-h-[200px] md:min-h-[240px] text-center bg-[#1c1c1e] border border-zinc-800 rounded-[20px] transition-all relative overflow-hidden group flex flex-col items-center justify-center px-5 py-8">
                <div className="w-12 h-12 rounded-full bg-white/[0.02] border border-white/5 flex items-center justify-center mx-auto mb-4 group-hover:bg-white/[0.04] transition-colors">
                  <FileText className="w-5 h-5 text-zinc-600 group-hover:text-zinc-400 transition-colors" />
                  </div>
                  <p className="text-[11px] font-black uppercase tracking-[0.2em] text-zinc-500 mb-2">Baseline Library / Empty</p>
                  <p className="text-[10px] font-bold text-zinc-700 max-w-[240px] mx-auto uppercase tracking-wider leading-relaxed italic">
                    Upload your baseline PDF to initialize the AI generation engine.
                  </p>
                </div>
              )}
           </div>
        )}
      </div>

      {/* Templates List */}
      <div className="dash-card p-4 md:p-5 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-white/10 via-white/5 to-transparent rounded-bl-full -mr-10 -mt-10 opacity-50" />
        
        <div className="mb-6 relative z-10">
           <h2 className="text-lg font-bold text-white flex items-center gap-2.5">
             Presentation Themes
             <span className="px-2.5 py-1 bg-white text-black rounded-full text-[8px] font-black uppercase tracking-widest">AI Matrix</span>
           </h2>
           <p className="text-zinc-400 text-sm font-medium mt-2 max-w-xl">When the agent deploys an application, it dynamically builds an ATS-optimized profile using one of these structural themes.</p>
        </div>

         <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5 relative z-10">
            {templates?.available?.map((tpl: any) => {
               const isSelected = templates.selected === tpl.name;
               const isLocked = tpl.tier !== "starter" && tpl.tier === "premium" && !isPremium || tpl.tier === "pro" && !isPro && !isPremium;

               return (
                  <motion.div 
                    key={tpl.name} 
                    whileHover={!isLocked ? { y: -8, scale: 1.02 } : {}}
                    className={cn(
                      "relative group rounded-xl overflow-hidden border-2 transition-all cursor-pointer flex flex-col h-full bg-[#1c1c1e]", 
                      isSelected ? "border-white/10 shadow-xl" : "border-white/5 hover:border-white/10 shadow-sm"
                    )} 
                    onClick={() => !isLocked && selectTemplate.mutate(tpl.name)}
                  >
                    <div className="aspect-[1/1.18] bg-white/5 p-3 border-b border-white/5 overflow-hidden">
                        {tpl.preview_img_url ? (
                        <img src={tpl.preview_img_url} alt={tpl.name} className={cn("w-full h-full object-contain rounded-lg shadow-lg opacity-90 group-hover:opacity-100 transition-opacity", isLocked ? "blur-[4px] opacity-40 grayscale" : "")} />
                        ) : (
                           <div className="w-full h-full flex items-center justify-center">
                          <FileText className="w-14 h-14 text-zinc-200" />
                           </div>
                        )}
                     </div>
                     {isLocked && (
                        <div className="absolute inset-0 flex flex-col items-center justify-center bg-[#1c1c1e]/70 backdrop-blur-[4px] z-20">
                          <div className="bg-white text-black p-3 rounded-2xl shadow-xl text-center">
                            <Lock className="w-5 h-5 text-serious-yellow mx-auto mb-1.5" />
                              <span className="text-[10px] font-black text-white uppercase tracking-widest">{tpl.tier} ACCESS</span>
                           </div>
                        </div>
                     )}
                      <div className="p-4 bg-[#1c1c1e] flex flex-col gap-1 relative z-10 mt-auto">
                        <div className="flex items-center justify-between">
                          <p className="font-black text-sm text-white capitalize tracking-tight">{tpl.name.replace(/-/g, " ").replace(/_/g, " ")}</p>
                          {isSelected && <div className="w-5 h-5 bg-white text-black rounded-full flex items-center justify-center"><Check className="w-3.5 h-3.5 text-black stroke-[3]" /></div>}
                        </div>
                        <p className="text-[10px] font-bold text-zinc-400 uppercase tracking-wide line-clamp-1">{tpl.description}</p>
                     </div>
                  </motion.div>
               );
            })}
        </div>
      </div>
    </div>
  );
}
