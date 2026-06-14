"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { createPortal } from "react-dom";
import { SettingSection, SettingCard } from "@/components/settings/card";
import { Toggle } from "@/components/settings/toggle";
import { useSettings } from "@/lib/settings-context";
import { useSubscription } from "@/lib/subscription";
import { Brain, Zap, Gauge, Briefcase, Shield, Lock, Check, ChevronDown, Search } from "lucide-react";
import { cn } from "@/lib/utils";
import type { PlanTier } from "@/lib/subscription";

// ── Types & Data ───────────────────────────────────────────────────────────────

type MinPlan = "starter" | "pro" | "premium";

interface ModelDef {
  key: string;
  label: string;
  provider: "groq" | "gemini" | "openrouter";
  description: string;
  minPlan: MinPlan;
}

const PROVIDERS = [
  { id: "groq" as const,       label: "Groq",       description: "Fast inference, Llama models" },
  { id: "gemini" as const,     label: "Gemini",     description: "Google DeepMind models" },
  { id: "openrouter" as const, label: "OpenRouter", description: "200+ models via one API" },
];

const MODELS: ModelDef[] = [
  { key: "auto",              label: "Auto (Recommended)",  provider: "groq",       description: "Fastest model, auto-selected",       minPlan: "starter" },
  { key: "llama-3.1-8b",     label: "Llama 3.1 8B",        provider: "groq",       description: "Fast, lightweight open model",       minPlan: "starter" },
  { key: "llama-3.3-70b",    label: "Llama 3.3 70B",       provider: "groq",       description: "Powerful open-source model",         minPlan: "starter" },
  { key: "gemini-flash",     label: "Gemini 1.5 Flash",    provider: "gemini",     description: "Google's fast multimodal model",     minPlan: "starter" },
  { key: "deepseek-v3",      label: "DeepSeek V3",         provider: "openrouter", description: "State-of-the-art open model",        minPlan: "starter" },
  { key: "qwen-3",           label: "Qwen 3",              provider: "openrouter", description: "Alibaba's reasoning model",          minPlan: "starter" },
  { key: "llama-4-maverick", label: "Llama 4 Maverick",    provider: "openrouter", description: "Meta's multimodal frontier model",   minPlan: "starter" },
  { key: "gemma-3",          label: "Gemma 3",             provider: "openrouter", description: "Google's open-weight model",         minPlan: "starter" },
  { key: "gpt-oss",          label: "GPT-OSS",             provider: "openrouter", description: "OpenAI-compatible open model",       minPlan: "starter" },
  { key: "claude-sonnet-4",  label: "Claude Sonnet 4",     provider: "openrouter", description: "Anthropic's fast intelligent model", minPlan: "pro" },
  { key: "gpt-5-mini",       label: "GPT-5 Mini",          provider: "openrouter", description: "OpenAI's efficient flagship",        minPlan: "pro" },
  { key: "gemini-2.5-pro",   label: "Gemini 2.5 Pro",      provider: "gemini",     description: "Google's top model",                 minPlan: "pro" },
  { key: "deepseek-r1",      label: "DeepSeek R1",         provider: "openrouter", description: "Top-tier reasoning model",           minPlan: "pro" },
  { key: "grok-fast",        label: "Grok Fast",           provider: "openrouter", description: "xAI's real-time knowledge model",    minPlan: "pro" },
  { key: "claude-opus-4",    label: "Claude Opus 4.1",     provider: "openrouter", description: "Anthropic's most capable model",     minPlan: "premium" },
  { key: "gpt-5",            label: "GPT-5",               provider: "openrouter", description: "OpenAI's most powerful model",       minPlan: "premium" },
  { key: "grok-4",           label: "Grok 4",              provider: "openrouter", description: "xAI's largest model",               minPlan: "premium" },
];

const PLAN_ORDER: Record<MinPlan, number> = { starter: 0, pro: 1, premium: 2 };

// Provider icon — simple coloured initials badge


function planMeetsRequirement(userPlan: PlanTier, required: MinPlan): boolean {
  if (userPlan === "none") return false;
  return PLAN_ORDER[userPlan as MinPlan] >= PLAN_ORDER[required];
}

// ── Model Dropdown ─────────────────────────────────────────────────────────────

const GROUPS: { key: MinPlan; label: string }[] = [
  { key: "starter",  label: "Free" },
  { key: "pro",      label: "Pro" },
  { key: "premium",  label: "Premium" },
];

function ModelDropdown({
  value,
  models,
  effectivePlan,
  onChange,
}: {
  value: string;
  models: ModelDef[];
  effectivePlan: MinPlan;
  onChange: (key: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [highlighted, setHighlighted] = useState<string | null>(null);
  const [portalStyle, setPortalStyle] = useState<React.CSSProperties>({});
  const triggerRef = useRef<HTMLButtonElement>(null);
  const searchRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);

  const filtered = models.filter(
    (m) =>
      m.label.toLowerCase().includes(search.toLowerCase()) ||
      m.description.toLowerCase().includes(search.toLowerCase())
  );

  const selected = models.find((m) => m.key === value);

  const choose = useCallback(
    (m: ModelDef) => {
      if (!planMeetsRequirement(effectivePlan, m.minPlan)) return;
      onChange(m.key);
      setOpen(false);
      setSearch("");
    },
    [effectivePlan, onChange]
  );

  // Position portal below trigger
  useEffect(() => {
    if (!open || !triggerRef.current) return;
    const rect = triggerRef.current.getBoundingClientRect();
    setPortalStyle({
      position: "fixed",
      top: rect.bottom + 6,
      left: rect.left,
      width: rect.width,
      zIndex: 9999,
    });
    setTimeout(() => searchRef.current?.focus({ preventScroll: true }), 30);
  }, [open]);

  // Reposition on scroll/resize while open
  useEffect(() => {
    if (!open) return;
    const reposition = () => {
      if (!triggerRef.current) return;
      const rect = triggerRef.current.getBoundingClientRect();
      setPortalStyle((s) => ({ ...s, top: rect.bottom + 6, left: rect.left, width: rect.width }));
    };
    window.addEventListener("scroll", reposition, true);
    window.addEventListener("resize", reposition);
    return () => {
      window.removeEventListener("scroll", reposition, true);
      window.removeEventListener("resize", reposition);
    };
  }, [open]);

  useEffect(() => { setHighlighted(filtered[0]?.key ?? null); }, [search]); // eslint-disable-line

  // Close on outside click
  useEffect(() => {
    if (!open) return;
    const handler = (e: MouseEvent) => {
      if (
        panelRef.current && !panelRef.current.contains(e.target as Node) &&
        triggerRef.current && !triggerRef.current.contains(e.target as Node)
      ) {
        setOpen(false);
        setSearch("");
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [open]);

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (!open) {
      if (["Enter", " ", "ArrowDown"].includes(e.key)) { e.preventDefault(); setOpen(true); }
      return;
    }
    const idx = filtered.findIndex((m) => m.key === highlighted);
    if (e.key === "ArrowDown") {
      e.preventDefault();
      const next = filtered[idx + 1];
      if (next) setHighlighted(next.key);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      const prev = filtered[idx - 1];
      if (prev) setHighlighted(prev.key);
    } else if (e.key === "Enter") {
      e.preventDefault();
      const m = filtered.find((m) => m.key === highlighted);
      if (m) choose(m);
    } else if (e.key === "Escape") {
      setOpen(false);
      setSearch("");
    }
  };

  // Scroll highlighted into view
  useEffect(() => {
    if (!open || !listRef.current || !highlighted) return;
    const el = listRef.current.querySelector(`[data-key="${highlighted}"]`) as HTMLElement | null;
    el?.scrollIntoView({ block: "nearest" });
  }, [highlighted, open]);

  const groupedFiltered = GROUPS.map((g) => ({
    ...g,
    models: filtered.filter((m) => m.minPlan === g.key),
  })).filter((g) => g.models.length > 0);

  const panel = open ? (
    <div
      ref={panelRef}
      style={portalStyle}
      onKeyDown={onKeyDown}
      className="rounded-xl border border-zinc-700 bg-[#141414] shadow-2xl shadow-black/80 overflow-hidden"
    >
      {/* Search */}
      <div className="flex items-center gap-2 px-3 py-2.5 border-b border-zinc-800">
        <Search className="w-3.5 h-3.5 text-zinc-500 shrink-0" />
        <input
          ref={searchRef}
          type="text"
          placeholder="Search models"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 bg-transparent text-sm text-zinc-200 placeholder:text-zinc-600 outline-none"
        />
      </div>

      {/* List */}
      <div ref={listRef} className="max-h-72 overflow-y-auto">
        {groupedFiltered.length === 0 ? (
          <p className="px-4 py-4 text-sm text-zinc-500">No models match</p>
        ) : (
          groupedFiltered.map((group) => (
            <div key={group.key}>
              <div className="sticky top-0 px-3 py-1.5 bg-[#141414] border-b border-zinc-800/50">
                <span className="text-[10px] font-semibold uppercase tracking-widest text-zinc-500">
                  {group.label}
                </span>
              </div>

              {group.models.map((m) => {
                const locked = !planMeetsRequirement(effectivePlan, m.minPlan);
                const isSelected = m.key === value;
                const isHigh = m.key === highlighted;

                return (
                  <button
                    key={m.key}
                    type="button"
                    data-key={m.key}
                    disabled={locked}
                    onMouseEnter={() => !locked && setHighlighted(m.key)}
                    onClick={() => choose(m)}
                    className={cn(
                      "w-full flex items-center gap-2.5 px-3 py-2.5 text-left transition-colors",
                      isHigh && !locked ? "bg-zinc-800/60" : "",
                      locked ? "cursor-not-allowed" : "cursor-pointer"
                    )}
                  >
                    <div className="flex-1 min-w-0">
                      <span className={cn(
                        "text-sm truncate block",
                        locked ? "text-zinc-600" : isSelected ? "text-white font-medium" : "text-zinc-300"
                      )}>
                        {m.label}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      {locked && (
                        <span className="flex items-center gap-1 text-[10px] text-zinc-600">
                          <Lock className="w-2.5 h-2.5" />
                          {group.label}
                        </span>
                      )}
                      {isSelected && !locked && <Check className="w-3.5 h-3.5 text-zinc-400" />}
                    </div>
                  </button>
                );
              })}
            </div>
          ))
        )}
      </div>
    </div>
  ) : null;

  return (
    <div onKeyDown={onKeyDown}>
      <button
        ref={triggerRef}
        type="button"
        onMouseDown={(e) => e.preventDefault()}
        onClick={() => setOpen((o) => !o)}
        className={cn(
          "w-full flex items-center justify-between gap-3 px-3.5 py-2.5 rounded-xl border text-left transition-all",
          "bg-[#161616] border-zinc-800 hover:border-zinc-600 focus:outline-none focus:border-zinc-500",
          open && "border-zinc-600"
        )}
      >
        <div className="flex items-center gap-2.5 min-w-0">
          <span className="text-sm font-medium text-white truncate">
            {selected?.label ?? "Select model"}
          </span>
        </div>
        <ChevronDown className={cn("w-4 h-4 text-zinc-500 shrink-0 transition-transform duration-150", open && "rotate-180")} />
      </button>

      {typeof document !== "undefined" && panel
        ? createPortal(panel, document.body)
        : null}
    </div>
  );
}

// ── Option cards (Reasoning / Style / Fallback) ────────────────────────────────

const REASONING_OPTIONS = [
  { id: "fast" as const,     label: "Fast",     description: "Max speed, lower cost. temperature=0.2, 1k tokens." },
  { id: "balanced" as const, label: "Balanced", description: "Speed/quality tradeoff. temperature=0.4, 2.5k tokens." },
  { id: "deep" as const,     label: "Deep",     description: "Maximum reasoning depth. temperature=0.7, 5k tokens." },
];

const STYLE_OPTIONS = [
  { id: "professional" as const, label: "Professional", description: "Polished corporate tone. ATS-friendly." },
  { id: "technical" as const,    label: "Technical",    description: "Engineering-focused with precise terminology." },
  { id: "startup" as const,      label: "Startup",      description: "Energetic, impact-driven, builder mindset." },
  { id: "enterprise" as const,   label: "Enterprise",   description: "Structured, process-oriented, risk-aware." },
];

const FALLBACK_STRATEGY_OPTIONS = [
  { id: "fastest" as const,      label: "Fastest",      description: "Groq → Gemini Flash → DeepSeek. Prioritize speed." },
  { id: "balanced" as const,     label: "Balanced",     description: "Groq 70B → Gemini → DeepSeek. Best all-round." },
  { id: "best_quality" as const, label: "Best Quality", description: "Claude Sonnet → DeepSeek R1 → Gemini Pro. Max quality." },
];

// ── Main ───────────────────────────────────────────────────────────────────────

export function AISettingsSection() {
  const { settings, saveSection } = useSettings();
  const { plan } = useSubscription();
  const effectivePlan = (plan === "none" ? "starter" : plan) as MinPlan;

  const filteredModels = MODELS.filter((m) =>
    settings.aiProvider === "groq"
      ? m.provider === "groq"
      : settings.aiProvider === "gemini"
        ? m.provider === "gemini"
        : true
  );

  const save = (data: Record<string, unknown>) => saveSection("ai", data);

  return (
    <SettingSection>
      {/* Provider */}
      <SettingCard
        title="AI Provider"
        description="Choose which AI engine powers your agent"
        icon={<Brain className="w-4 h-4 text-white" />}
      >
        <div className="grid grid-cols-3 gap-3">
          {PROVIDERS.map((p) => (
            <button
              key={p.id}
              onClick={() => save({ ai_provider: p.id, ai_model: "auto" })}
              className={cn(
                "p-4 rounded-xl border text-left transition-all",
                settings.aiProvider === p.id
                  ? "bg-white text-black border-white shadow-lg"
                  : "bg-[#161616] text-[#A1A1AA] border-zinc-800 hover:border-white/30"
              )}
            >
              <p className="text-sm font-bold">{p.label}</p>
              <p className={cn("text-[10px] mt-1", settings.aiProvider === p.id ? "text-black/60" : "opacity-60")}>
                {p.description}
              </p>
            </button>
          ))}
        </div>
      </SettingCard>

      {/* Model */}
      <SettingCard
        title="Model"
        description="Select the AI model. Locked models require a plan upgrade."
        icon={<Zap className="w-4 h-4 text-white" />}
      >
        <ModelDropdown
          value={settings.aiModel}
          models={filteredModels}
          effectivePlan={effectivePlan}
          onChange={(key) => save({ ai_model: key })}
        />
      </SettingCard>

      {/* Reasoning Depth */}
      <SettingCard
        title="Reasoning Depth"
        description="Controls temperature, max tokens, and reasoning instructions injected into every AI request"
        icon={<Gauge className="w-4 h-4 text-white" />}
      >
        <div className="grid gap-3">
          {REASONING_OPTIONS.map((opt) => (
            <button
              key={opt.id}
              onClick={() => save({ reasoning_depth: opt.id })}
              className={cn(
                "flex items-center gap-4 p-4 rounded-xl border text-left transition-all",
                settings.reasoningDepth === opt.id
                  ? "bg-[#1a1a1a] border-white/30 ring-1 ring-white/10"
                  : "bg-[#161616] border-zinc-800 hover:border-zinc-700"
              )}
            >
              <div className={cn(
                "w-8 h-8 rounded-lg flex items-center justify-center shrink-0",
                settings.reasoningDepth === opt.id ? "bg-white" : "bg-[#242424]"
              )}>
                <Zap className={cn("w-4 h-4", settings.reasoningDepth === opt.id ? "text-black" : "text-[#A1A1AA]")} />
              </div>
              <div>
                <p className="text-sm font-bold text-white">{opt.label}</p>
                <p className="text-xs text-[#A1A1AA] mt-0.5">{opt.description}</p>
              </div>
            </button>
          ))}
        </div>
      </SettingCard>

      {/* Application Generation Style */}
      <SettingCard
        title="Application Generation Style"
        description="Injected into every cover letter, resume optimization, follow-up, and AI chat response"
        icon={<Briefcase className="w-4 h-4 text-white" />}
      >
        <div className="grid grid-cols-2 gap-3">
          {STYLE_OPTIONS.map((opt) => (
            <button
              key={opt.id}
              onClick={() => save({ app_gen_style: opt.id })}
              className={cn(
                "p-4 rounded-xl border text-left transition-all",
                settings.applicationStyle === opt.id
                  ? "bg-[#1a1a1a] border-white/30 ring-1 ring-white/10"
                  : "bg-[#161616] border-zinc-800 hover:border-zinc-700"
              )}
            >
              <p className="text-sm font-bold text-white mb-1">{opt.label}</p>
              <p className="text-xs text-[#A1A1AA] leading-relaxed">{opt.description}</p>
            </button>
          ))}
        </div>
      </SettingCard>

      {/* Smart Fallback */}
      <SettingCard
        title="Smart Fallback"
        description="Automatically switch to another model if your preferred model is unavailable or rate-limited"
        icon={<Shield className="w-4 h-4 text-white" />}
        action={
          <Toggle
            checked={settings.fallbackEnabled}
            onChange={(v) => save({ fallback_enabled: v })}
          />
        }
      >
        {settings.fallbackEnabled && (
          <div className="mt-2 space-y-2">
            <p className="text-xs text-zinc-500 mb-3">Fallback Strategy</p>
            {FALLBACK_STRATEGY_OPTIONS.map((opt) => (
              <button
                key={opt.id}
                onClick={() => save({ fallback_strategy: opt.id })}
                className={cn(
                  "w-full flex items-start gap-3 p-3.5 rounded-xl border text-left transition-all",
                  settings.fallbackStrategy === opt.id
                    ? "bg-[#1a1a1a] border-white/20 ring-1 ring-white/10"
                    : "bg-[#161616] border-zinc-800 hover:border-zinc-700"
                )}
              >
                <div className={cn(
                  "w-4 h-4 mt-0.5 rounded-full border-2 shrink-0 flex items-center justify-center",
                  settings.fallbackStrategy === opt.id ? "border-white bg-white" : "border-zinc-600"
                )}>
                  {settings.fallbackStrategy === opt.id && <div className="w-1.5 h-1.5 rounded-full bg-black" />}
                </div>
                <div>
                  <p className="text-sm font-semibold text-white">{opt.label}</p>
                  <p className="text-[11px] text-zinc-500 mt-0.5">{opt.description}</p>
                </div>
              </button>
            ))}
          </div>
        )}
        {!settings.fallbackEnabled && (
          <div className="mt-2 p-3 bg-amber-500/5 border border-amber-500/20 rounded-xl">
            <p className="text-xs text-amber-400">
              Smart fallback is disabled. If your preferred model fails, the request will error instead of trying another model.
            </p>
          </div>
        )}
      </SettingCard>
    </SettingSection>
  );
}
