"use client";
import { useState, useRef, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { chatApi } from "@/lib/api";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Bot, BotMessageSquare, User as UserIcon, Brain, Zap, Trash2, Sparkles, Target, Search, FileText, Mail, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp?: Date;
}

const personas = [
  { id: "general", label: "General", icon: Sparkles, color: "text-white" },
  { id: "career_coach", label: "Career Coach", icon: Target, color: "text-white" },
  { id: "resume_expert", label: "Resume Expert", icon: FileText, color: "text-white" },
  { id: "job_scout", label: "Job Scout", icon: Search, color: "text-white" },
  { id: "application_assistant", label: "Apply Helper", icon: Mail, color: "text-white" },
];

function TypingIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center gap-1 px-4 py-3 bg-white/10 rounded-2xl rounded-bl-md"
    >
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          className="w-2 h-2 bg-white text-black border border-zinc-800/60 rounded-full"
          animate={{ y: [0, -4, 0], opacity: [0.5, 1, 0.5] }}
          transition={{
            duration: 0.6,
            repeat: Infinity,
            delay: i * 0.15,
          }}
        />
      ))}
    </motion.div>
  );
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: "Hi! I'm Lumi, your personal career assistant. Need help? Call 📞 9751120169 (Mon-Sat, 9AM-6PM) or email applivoagent@gmail.com. I can help with resume tailoring, job searches, interview prep, and more!", timestamp: new Date() }
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [persona, setPersona] = useState("general");
  const endRef = useRef<HTMLDivElement>(null);

  const queryClient = useQueryClient();

  const { data: credits } = useQuery({
    queryKey: ["chat-credits"],
    queryFn: () => chatApi.credits().then((r) => r.data),
  });

  const { data: history, isLoading: historyLoading } = useQuery({
    queryKey: ["chat-history"],
    queryFn: () => chatApi.history(50).then((r) => r.data),
  });

  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => {
    if (history && history.length > 0) {
      const loadedMessages: Message[] = history.reverse().map((m: { role: string; content: string; created_at?: string }) => ({
        role: m.role as "user" | "assistant",
        content: m.content,
        timestamp: m.created_at ? new Date(m.created_at) : new Date(),
      }));
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setMessages([
        { role: "assistant", content: "Hi! I'm Lumi, your personal career assistant. Need help? Call 📞 9751120169 (Mon-Sat, 9AM-6PM) or email support@applivo.com. I can help with resume tailoring, job searches, interview prep, and more!", timestamp: new Date() },
        ...loadedMessages,
      ]);
    }
  }, [history]);

  const clearHistoryMut = useMutation({
    mutationFn: () => chatApi.clearHistory(),
    onSuccess: () => {
      setMessages([
        { role: "assistant", content: "Hi! I'm Lumi, your personal career assistant. Need help? Call 📞 9751120169 (Mon-Sat, 9AM-6PM) or email support@applivo.com. I can help with resume tailoring, job searches, interview prep, and more!", timestamp: new Date() }
      ]);
      queryClient.invalidateQueries({ queryKey: ["chat-history"] });
    },
  });

  const chatMut = useMutation({
    mutationFn: (msg: string) => chatApi.send({
      message: msg,
      history: messages.map(m => ({ role: m.role, content: m.content })),
      persona,
    }),
    onMutate: (msg) => {
      setMessages(prev => [...prev, { role: "user", content: msg, timestamp: new Date() }, { role: "assistant", content: "...", timestamp: new Date() }]);
      setInput("");
      setIsTyping(true);
    },
    onSuccess: (res) => {
      setIsTyping(false);
      setMessages(prev => {
        const newMsgs = [...prev];
        newMsgs[newMsgs.length - 1] = { role: "assistant", content: res.data.response, timestamp: new Date() };
        return newMsgs;
      });
    },
    onError: () => {
      setIsTyping(false);
      setMessages(prev => {
        const newMsgs = [...prev];
        newMsgs[newMsgs.length - 1] = { role: "assistant", content: "Sorry, I ran into an error processing that request.", timestamp: new Date() };
        return newMsgs;
      });
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["chat-credits"] });
    }
  });

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || chatMut.isPending) return;
    chatMut.mutate(input);
  };

  const getCreditDisplay = () => {
    if (!credits) return null;
    if (credits.is_unlimited) {
      return { label: "Unlimited", color: "text-white" };
    }
    if (credits.remaining <= 10) {
      return { label: `${credits.remaining} credits`, color: "text-zinc-400" };
    }
    return { label: `${credits.remaining} credits`, color: "text-white" };
  };

  const creditDisplay = getCreditDisplay();

  return (
    <div className="flex flex-col h-[calc(100vh-4.5rem)] relative">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between pb-4 border-b border-white/10 shrink-0"
      >
        <div className="flex items-center gap-4">
          <motion.div
            whileHover={{ scale: 1.1 }}
            className="w-12 h-12 rounded-2xl bg-[#1c1c1e] text-white border border-zinc-800 flex items-center justify-center shadow-lg shadow-white/5"
          >
            <BotMessageSquare className="w-6 h-6 text-white" />
          </motion.div>
          <div>
            <h1 className="text-xl font-bold text-white leading-tight">Lumi</h1>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse" />
              <p className="text-xs text-zinc-400 font-medium">Powered by LLaMA-3.1-8B</p>
            </div>
          </div>
        </div>

        {/* Persona Picker */}
        <div className="flex items-center gap-1.5 bg-white/10 p-1 rounded-xl">
          {personas.map((p) => {
            const Icon = p.icon;
            const isActive = persona === p.id;
            return (
              <button
                key={p.id}
                onClick={() => setPersona(p.id)}
                className={cn(
                  "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all",
                  isActive
                    ? "bg-[#1c1c1e] shadow-sm text-white border border-zinc-800"
                    : "text-zinc-400 hover:text-zinc-300"
                )}
                title={p.label}
              >
                <Icon className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">{p.label}</span>
              </button>
            );
          })}
        </div>

        {/* Credits Display */}
        {creditDisplay && (
          <div className="flex items-center gap-3">
            <button
              onClick={() => clearHistoryMut.mutate()}
              disabled={clearHistoryMut.isPending}
              className="p-2.5 rounded-xl hover:bg-[#1c1c1e]/10 text-zinc-400 hover:text-zinc-400 transition-colors"
              title="Clear chat history"
            >
              <Trash2 className="w-4 h-4" />
            </button>
            <motion.div
              whileHover={{ scale: 1.05 }}
              className={cn("flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10", creditDisplay.color)}
            >
              <Zap className="w-4 h-4" />
              <span className="text-sm font-semibold">{creditDisplay.label}</span>
            </motion.div>
          </div>
        )}
      </motion.div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto py-6 px-4 space-y-6 scrollbar-hide">
        <AnimatePresence initial={false}>
          {messages.map((m, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.3 }}
              className={cn("flex gap-4 max-w-3xl", m.role === "user" ? "ml-auto flex-row-reverse" : "")}
            >
              <motion.div
                whileHover={{ scale: 1.05 }}
                className={cn("w-9 h-9 rounded-xl flex items-center justify-center shrink-0 mt-1",
                  m.role === "user"
                    ? "bg-white text-black border border-zinc-800"
                    : "bg-[#1c1c1e] text-white border border-zinc-800 shadow-sm")}
              >
                {m.role === "user" ? <UserIcon className="w-4 h-4" /> : <BotMessageSquare className="w-4 h-4" />}
              </motion.div>
              <div className={cn("px-5 py-4 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap shadow-sm max-w-[80%]",
                m.role === "user"
                  ? "bg-[#2a2a2a] text-white rounded-tr-none border border-zinc-700"
                  : "bg-[#1c1c1e] border border-white/10 text-zinc-300 rounded-tl-none")}>
                {m.content === "..." ? <TypingIndicator /> : m.content}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        <div ref={endRef} />
      </div>

      {/* Input */}
      <div className="pt-4 pb-0 border-t border-white/10 shrink-0 bg-[#050505] backdrop-blur">
        <form onSubmit={handleSubmit} className="relative">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            placeholder="Ask about interviewing, resume tailoring, or job matching..."
            className="w-full bg-white/5 border border-white/10 rounded-2xl pl-5 pr-14 py-4 text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/30 focus:bg-[#1c1c1e] resize-none h-[72px] transition-all"
            rows={1}
          />
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            type="submit"
            disabled={!input.trim() || chatMut.isPending}
            className="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 flex items-center justify-center bg-white text-black border border-zinc-800 text-black rounded-xl hover:shadow-lg hover:shadow-brand-primary/30 disabled:opacity-80 disabled:cursor-not-allowed disabled:bg-zinc-200 transition-all"
          >
            {chatMut.isPending ? (
              <motion.div
                className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              />
            ) : (
              <Send className="w-4 h-4 text-black" />
            )}
          </motion.button>
        </form>
        <p className="text-center text-[10px] text-zinc-400 mt-2">Assistant uses your profile data and applications context to generate answers.</p>
      </div>
    </div>
  );
}
