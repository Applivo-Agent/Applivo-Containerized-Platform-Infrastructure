"use client";
import { useState, useRef, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { chatApi } from "@/lib/api";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Bot, User as UserIcon, Sparkles, Zap } from "lucide-react";
import { cn } from "@/lib/utils";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: "Hi! I'm the Applivo AI Assistant. I can help you tailor your resume padding, optimize keywords for a specific role, analyze job descriptions, or answer questions about your interview prep. How can I help today?" }
  ]);
  const [input, setInput] = useState("");
  const endRef = useRef<HTMLDivElement>(null);

  const queryClient = useQueryClient();

  const { data: credits } = useQuery({
    queryKey: ["chat-credits"],
    queryFn: () => chatApi.credits().then((r) => r.data),
  });

  const chatMut = useMutation({
    mutationFn: (msg: string) => chatApi.send({ message: msg, history: messages.map(m => ({ role: m.role, content: m.content })) }),
    onMutate: (msg) => {
      setMessages(prev => [...prev, { role: "user", content: msg }, { role: "assistant", content: "..." }]);
      setInput("");
    },
    onSuccess: (res) => {
      setMessages(prev => {
        const newMsgs = [...prev];
        newMsgs[newMsgs.length - 1] = { role: "assistant", content: res.data.response };
        return newMsgs;
      });
    },
    onError: () => {
      setMessages(prev => {
        const newMsgs = [...prev];
        newMsgs[newMsgs.length - 1] = { role: "assistant", content: "Sorry, I ran into an error processing that request." };
        return newMsgs;
      });
    },
    onSettled: () => {
      // Refresh credits after sending a message
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
      return { label: "Unlimited", color: "text-amber-400" };
    }
    if (credits.remaining <= 10) {
      return { label: `${credits.remaining} credits left`, color: "text-red-400" };
    }
    return { label: `${credits.remaining} credits`, color: "text-emerald-400" };
  };

  const creditDisplay = getCreditDisplay();

  return (
    <div className="flex flex-col h-[calc(100vh-6rem)] relative">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-border shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-purple to-brand-blue flex items-center justify-center shadow-lg">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold font-display leading-tight">Career Assistant</h1>
            <p className="text-xs text-brand-purple-light font-medium">Powered by LLaMA</p>
          </div>
        </div>
        
        {/* Credits Display */}
        {creditDisplay && (
          <div className={cn("flex items-center gap-2 px-3 py-1.5 rounded-full bg-muted/50", creditDisplay.color)}>
            <Zap className="w-4 h-4" />
            <span className="text-sm font-medium">{creditDisplay.label}</span>
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto py-6 space-y-6 scrollbar-hide">
        <AnimatePresence initial={false}>
          {messages.map((m, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={cn("flex gap-4 max-w-3xl", m.role === "user" ? "ml-auto flex-row-reverse" : "")}
            >
              <div className={cn("w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1",
                m.role === "user" ? "bg-muted" : "bg-brand-purple/20 text-brand-purple-light")}>
                {m.role === "user" ? <UserIcon className="w-4 h-4 text-muted-foreground" /> : <Bot className="w-4 h-4" />}
              </div>
              <div className={cn("px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap",
                m.role === "user" ? "bg-brand-purple text-white rounded-tr-none" : "glass rounded-tl-none")}>
                {m.content === "..." ? (
                  <div className="flex gap-1 items-center h-4">
                    <div className="w-1.5 h-1.5 bg-brand-purple-light rounded-full animate-bounce [animation-delay:-0.3s]" />
                    <div className="w-1.5 h-1.5 bg-brand-purple-light rounded-full animate-bounce [animation-delay:-0.15s]" />
                    <div className="w-1.5 h-1.5 bg-brand-purple-light rounded-full animate-bounce" />
                  </div>
                ) : m.content}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        <div ref={endRef} />
      </div>

      {/* Input */}
      <div className="pt-4 border-t border-border shrink-0">
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
            className="w-full bg-muted border border-border rounded-xl pl-4 pr-14 py-4 text-sm focus:outline-none focus:ring-2 focus:ring-brand-purple/50 resize-none h-[68px]"
            rows={1}
          />
          <button
            type="submit"
            disabled={!input.trim() || chatMut.isPending}
            className="absolute right-2 top-2 bottom-2 w-10 flex items-center justify-center bg-brand-purple text-white rounded-lg hover:bg-brand-purple/90 disabled:opacity-50 disabled:bg-muted"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
        <p className="text-center text-[10px] text-muted-foreground mt-2">Assistant uses your profile data and applications context to generate answers.</p>
      </div>
    </div>
  );
}
