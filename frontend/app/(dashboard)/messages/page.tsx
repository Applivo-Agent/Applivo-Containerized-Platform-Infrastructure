"use client";
import React, { useEffect, useState } from "react";
import { Mail, RefreshCw, Loader2, Star, AlertTriangle } from "lucide-react";
import { platformApi } from "@/lib/api";
import { toast } from "sonner";

interface PlatformMessage {
  id: string;
  sender: string;
  subject: string;
  content: string;
  is_important: boolean;
  importance_keywords: string | null;
  received_at: string | null;
  platform: string;
}

export default function MessagesPage() {
  const [messages, setMessages] = useState<PlatformMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [filter, setFilter] = useState<"all" | "important" | "urgent">("all");

  useEffect(() => { loadMessages(); }, []);

  const loadMessages = async () => {
    setLoading(true);
    try {
      const res = await platformApi.messages("internshala", 50);
      setMessages(res.data);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Failed to load messages");
    } finally {
      setLoading(false);
    }
  };

  const handleScan = async () => {
    setScanning(true); setLoading(true);
    try {
      await platformApi.scanMessages("internshala");
      toast.success("Sync completed");
      loadMessages();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Sync failed");
    } finally {
      setScanning(false);
    }
  };

  const filteredMessages = messages.filter((msg) => {
    if (filter === "important") return msg.is_important;
    if (filter === "urgent") {
      const c = msg.content.toLowerCase();
      return c.includes("deadline") || c.includes("expires") || c.includes("urgent");
    }
    return true;
  });

  const importantCount = messages.filter(m => m.is_important).length;
  const urgentCount = messages.filter(m => {
    const c = m.content.toLowerCase();
    return c.includes("deadline") || c.includes("expires") || c.includes("urgent");
  }).length;

  const formatMessage = (content: string, sender: string) => {
    const lines = content.split('\n').map(l => l.trim()).filter(l => l);
    
    let company = sender && sender !== "Internshala Chat" ? sender : "";
    let jobTitle = "";
    let time = "";
    let date = "";
    let isUrgent = false;
    
    // If company not from sender, try to extract from content
    if (!company) {
      // Look for pattern like "Company | Chatting with..."
      for (const line of lines) {
        if (line.includes('|') && line.includes('Chatting')) {
          company = line.split('|')[0].trim();
          break;
        }
      }
      // Or first line that's not "Internshala Chat" or "You:"
      if (!company) {
        for (const line of lines) {
          if (line && !line.includes('Chat') && !line.startsWith('You:') && line.length > 2 && line.length < 40) {
            company = line;
            break;
          }
        }
      }
    }
    
    // Find job title - look for "internship" in any line
    for (const line of lines) {
      if (line.toLowerCase().includes('internship')) {
        jobTitle = line.replace(/internship/gi, '').trim();
        break;
      }
    }
    
    // Find time
    for (const line of lines) {
      const timeMatch = line.match(/^(\d{1,2}:\d{2}\s*(?:AM|PM)?)/i);
      if (timeMatch) {
        time = timeMatch[1];
        break;
      }
    }
    
    // Find date
    for (const line of lines) {
      const dateMatch = line.match(/^(\d{2}\/\d{2}\/\d{4})/);
      if (dateMatch) {
        date = dateMatch[1];
        break;
      }
    }
    
    // Check urgent
    if (content.toLowerCase().includes('deadline') || content.toLowerCase().includes('expires')) {
      isUrgent = true;
    }
    
    return { company, jobTitle, time, date, isUrgent };
  };

  const [selectedMessage, setSelectedMessage] = useState<PlatformMessage | null>(null);

  return (
    <div className="dash-page p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-[#242424] border border-white/[0.08] rounded-lg">
            <Mail className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">Platform Messages</h1>
            <p className="text-sm text-zinc-400 mt-1">Real-time updates from Internshala recruiter chats and invites.</p>
          </div>
        </div>
        <button
          onClick={handleScan}
          disabled={scanning}
          className="flex items-center gap-2 px-4 py-2 bg-white text-black hover:bg-gray-200 rounded-lg disabled:opacity-80 disabled:cursor-not-allowed transition-all text-sm font-medium shadow-lg"
        >
          {scanning ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
          {scanning ? "Syncing Inbox..." : "Sync Messages"}
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-3">
        <div className="dash-stat-card bg-[#242424] border-white/[0.08] shadow-[inset_0_1px_0_rgba(255,255,255,0.035)]">
          <div className="dash-value">{messages.length}</div>
          <div className="dash-label mt-1">Total Messages</div>
        </div>
        <div className="dash-stat-card bg-[#242424] border-white/[0.08] shadow-[inset_0_1px_0_rgba(255,255,255,0.035)]">
          <div className="dash-value">{importantCount}</div>
          <div className="dash-label mt-1">Important</div>
        </div>
        <div className="dash-stat-card bg-[#242424] border-white/[0.08] shadow-[inset_0_1px_0_rgba(255,255,255,0.035)]">
          <div className="dash-value">{urgentCount}</div>
          <div className="dash-label mt-1">Urgent Action</div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-2">
        <button onClick={() => setFilter("all")} className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${filter === "all" ? "bg-white text-black shadow-lg" : " hover:bg-white/5 text-zinc-400"}`}>
          All ({messages.length})
        </button>
        <button onClick={() => setFilter("important")} className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${filter === "important" ? "bg-white text-black shadow-lg" : " hover:bg-white/5 text-zinc-400"}`}>
          Important ({importantCount})
        </button>
        <button onClick={() => setFilter("urgent")} className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${filter === "urgent" ? "bg-white text-black shadow-lg" : " hover:bg-white/5 text-zinc-400"}`}>
          Urgent ({urgentCount})
        </button>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 gap-3">
          <Loader2 className="w-10 h-10 animate-spin text-white" />
          <p className="text-sm text-muted-foreground animate-pulse">Scanning platform inboxes...</p>
        </div>
      ) : filteredMessages.length === 0 ? (
        <div className="text-center py-20 bg-[#242424] border border-white/[0.08] rounded-[20px] shadow-[inset_0_1px_0_rgba(255,255,255,0.035)] transition-all">
          <div className="w-12 h-12 rounded-full bg-[#1d1d1d] border border-white/[0.08] flex items-center justify-center mx-auto mb-6">
            <Mail className="w-5 h-5 text-zinc-600" />
          </div>
          <p className="text-[11px] font-black uppercase tracking-[0.2em] text-zinc-500 mb-2">Inbox Deployed / No outreach detected</p>
          <p className="text-[10px] font-bold text-zinc-700 max-w-[200px] mx-auto uppercase tracking-wider leading-relaxed italic">
            Sync your platform credentials to scan for hidden recruiter callbacks.
          </p>
        </div>
      ) : (
        <div className="grid gap-3">
          {filteredMessages.map((msg) => {
            const isUrgent = msg.content.toLowerCase().includes('deadline') || msg.content.toLowerCase().includes('expires');
            const receivedDate = msg.received_at ? new Date(msg.received_at) : null;
            const timeStr = receivedDate ? receivedDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "";
            const dateStr = receivedDate ? receivedDate.toLocaleDateString([], { month: 'short', day: 'numeric' }) : "Recently";
            
            let displaySender = msg.sender;
            if (displaySender && displaySender.includes('. Accept')) displaySender = displaySender.split('. Accept')[0];
            if (displaySender && displaySender.includes('. Get')) displaySender = displaySender.split('. Get')[0];
            
            if (!displaySender || displaySender === "Internshala Chat" || displaySender === "Unknown") {
                const pat = /(?:internship|role|position|opportunity) at ([A-Z][A-Za-z0-9 &]+?)(?:\.|,|\n| Accept| Get| Please| We| I| This)/i;
                const match = msg.content.match(pat);
                if (match && match[1]) {
                    displaySender = match[1].trim();
                }
            }
            if (!displaySender || displaySender === "Internshala Chat" || displaySender === "Unknown") {
                const pat = /(?:message from|team from|on behalf of) ([A-Z][A-Za-z0-9 &]+?)(?:\.|,|\n| Accept| Get| Please)/i;
                const match = msg.content.match(pat);
                if (match && match[1]) displaySender = match[1].trim();
            }
            if (!displaySender || displaySender === "Internshala Chat" || displaySender === "Unknown") {
                const pat = /(?:We are interested in your profile for.*?at )([A-Z][A-Za-z0-9 &]+)/i;
                const match = msg.content.match(pat);
                if (match && match[1]) displaySender = match[1].trim();
            }
            
            return (
              <div
                key={msg.id}
                onClick={() => setSelectedMessage(msg)}
                className={`p-5 rounded-2xl bg-[#242424] border border-white/[0.08] cursor-pointer hover:border-white/20 transition-all shadow-[inset_0_1px_0_rgba(255,255,255,0.035)] group`}
              >
                <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2">
                      {msg.is_important && <Star className="w-4 h-4 text-white fill-white" />}
                      {isUrgent && <AlertTriangle className="w-4 h-4 text-white" />}
                      <span className="font-bold text-lg group-hover:text-white transition-colors">{displaySender}</span>
                    </div>
                  <div className="text-[9px] text-muted-foreground uppercase tracking-[0.2em] font-bold bg-white/5 px-2 py-1 rounded">
                    {msg.platform}
                  </div>
                </div>
                
                <div className="text-white font-semibold text-sm mb-3 ml-0">
                  {msg.subject || "Platform Notification"}
                </div>

                <div className="flex items-end justify-between gap-6">
                  <div className="text-sm text-white/50 line-clamp-2 leading-relaxed flex-1 italic">
                    "{msg.content}"
                  </div>
                  <div className="text-[11px] text-zinc-500 whitespace-nowrap text-right font-medium">
                    <div className="text-white/80">{timeStr}</div>
                    <div className="opacity-60">{dateStr}</div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Message Detail Modal */}
      {selectedMessage && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#111118]/90 backdrop-blur-sm animate-in fade-in duration-200" onClick={() => setSelectedMessage(null)}>
          <div className="bg-[#242424] w-full max-w-2xl max-h-[80vh] overflow-hidden flex flex-col border border-white/[0.08] rounded-2xl shadow-2xl animate-in zoom-in-95 duration-200" onClick={e => e.stopPropagation()}>
            <div className="p-6 border-b border-white/[0.08] bg-[#232327]">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-2xl font-bold text-white">
                      {selectedMessage.sender.includes('. Accept') ? selectedMessage.sender.split('. Accept')[0] : 
                       (selectedMessage.sender === 'Internshala Chat' ? (() => {
                         const match = selectedMessage.content.match(/(?:internship|role|position|opportunity) at ([A-Z][A-Za-z0-9 &]+?)(?:\.|,|\n| Accept)/i) || selectedMessage.content.match(/(?:We are interested in your profile for.*?at )([A-Z][A-Za-z0-9 &]+)/i);
                         return match && match[1] ? match[1].trim() : "Internshala Chat";
                       })() : selectedMessage.sender)}
                    </span>
                    <span className="text-[10px] text-muted-foreground uppercase tracking-wider bg-white/10 px-2 py-0.5 rounded-full font-bold">
                      {selectedMessage.platform}
                    </span>
                  </div>
                  <div className="text-white font-bold tracking-tight">
                    {selectedMessage.subject}
                  </div>
                </div>
                <button onClick={() => setSelectedMessage(null)} className="p-2 hover:bg-white/10 rounded-full transition-colors">
                  <RefreshCw className="w-5 h-5 rotate-45" />
                </button>
              </div>
              <div className="text-xs text-muted-foreground flex gap-4">
                <span>Received: {selectedMessage.received_at ? new Date(selectedMessage.received_at).toLocaleString() : "Unknown"}</span>
                {selectedMessage.is_important && (
                  <span className="flex items-center gap-1 text-white">
                    <Star className="w-3 h-3 fill-white" />
                    Important
                  </span>
                )}
              </div>
            </div>
            <div className="p-8 flex-1 overflow-y-auto bg-[#232327]">
              <div className="text-white/90 leading-7 whitespace-pre-wrap text-base sm:text-lg font-normal tracking-wide">
                {selectedMessage.content}
              </div>
            </div>
            <div className="p-4 bg-[#232327] border-t border-white/[0.08] flex justify-end">
              <button onClick={() => setSelectedMessage(null)} className="px-6 py-2 bg-white text-black hover:bg-gray-200 transition-colors rounded-lg font-medium shadow-lg border border-white/[0.08]">
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}