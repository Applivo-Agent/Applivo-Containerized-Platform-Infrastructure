"""
app/services/ai_router.py
─────────────────────────
Smart AI Router with per-user settings, OpenRouter support,
reasoning depth injection, application style injection,
and intelligent multi-provider fallback chains.

Providers:
  groq        — Primary, fast, low latency (Llama models)
  gemini      — Secondary, high capacity
  openrouter  — Premium models (Claude, GPT-5, Grok, DeepSeek, etc.)

Fallback Strategies:
  fastest      — groq → gemini → openrouter-fast
  balanced     — user preference → groq → gemini → openrouter
  best_quality — openrouter-quality → groq → gemini
"""

from __future__ import annotations
import asyncio
import time
import structlog
from typing import Optional, Dict, Any

from openai import AsyncOpenAI
from app.core.config import settings

logger = structlog.get_logger()

# ── Reasoning depth configuration ────────────────────────────────────────────

REASONING_CONFIG: Dict[str, Dict[str, Any]] = {
    "fast": {
        "temperature": 0.2,
        "max_tokens_cap": 1000,
        "system_suffix": (
            "\n\nIMPORTANT: Provide concise, direct answers. "
            "Optimize for speed. Avoid verbose reasoning or excessive explanation."
        ),
    },
    "balanced": {
        "temperature": 0.4,
        "max_tokens_cap": 2500,
        "system_suffix": "\n\nBalance speed and quality in your response.",
    },
    "deep": {
        "temperature": 0.7,
        "max_tokens_cap": 5000,
        "system_suffix": (
            "\n\nPerform deep reasoning. Provide detailed analysis. "
            "Consider tradeoffs and edge cases thoroughly."
        ),
    },
}

# ── Application style prompt modifiers ───────────────────────────────────────

STYLE_PROMPTS: Dict[str, str] = {
    "professional": (
        "Use polished, corporate language. Keep content ATS-friendly. "
        "Maintain a professional, formal tone throughout."
    ),
    "technical": (
        "Emphasize engineering achievements. Include specific tools, frameworks, "
        "and architecture decisions. Use precise technical terminology."
    ),
    "startup": (
        "Write with energy and impact focus. Highlight ownership, speed, "
        "and builder mindset. Keep tone conversational but confident."
    ),
    "enterprise": (
        "Use structured, process-oriented language. Emphasize cross-functional "
        "collaboration, risk awareness, and scalability thinking."
    ),
}

# ── Model catalog with provider routing ──────────────────────────────────────

# Maps user-facing model key → (provider, actual_model_id, plan_required)
MODEL_CATALOG: Dict[str, Dict[str, str]] = {
    # Starter models
    "auto":                  {"provider": "groq",       "id": "llama-3.1-8b-instant",              "plan": "starter"},
    "llama-3.1-8b":          {"provider": "groq",       "id": "llama-3.1-8b-instant",              "plan": "starter"},
    "llama-3.3-70b":         {"provider": "groq",       "id": "llama-3.3-70b-versatile",           "plan": "starter"},
    "gemini-flash":          {"provider": "gemini",     "id": "gemini-1.5-flash",                  "plan": "starter"},
    "deepseek-v3":           {"provider": "openrouter", "id": "deepseek/deepseek-chat",            "plan": "starter"},
    "qwen-3":                {"provider": "openrouter", "id": "qwen/qwq-32b",                      "plan": "starter"},
    "llama-4-maverick":      {"provider": "openrouter", "id": "meta-llama/llama-4-maverick",       "plan": "starter"},
    "gemma-3":               {"provider": "openrouter", "id": "google/gemma-3-27b-it:free",        "plan": "starter"},
    "gpt-oss":               {"provider": "openrouter", "id": "openai/gpt-4o-mini",                "plan": "starter"},
    # Pro models
    "claude-sonnet-4":       {"provider": "openrouter", "id": "anthropic/claude-sonnet-4",         "plan": "pro"},
    "gpt-5-mini":            {"provider": "openrouter", "id": "openai/gpt-4o",                     "plan": "pro"},
    "gemini-2.5-pro":        {"provider": "gemini",     "id": "gemini-2.5-pro",                    "plan": "pro"},
    "deepseek-r1":           {"provider": "openrouter", "id": "deepseek/deepseek-r1",              "plan": "pro"},
    "grok-fast":             {"provider": "openrouter", "id": "x-ai/grok-beta",                    "plan": "pro"},
    # Premium models
    "claude-opus-4":         {"provider": "openrouter", "id": "anthropic/claude-opus-4",           "plan": "premium"},
    "gpt-5":                 {"provider": "openrouter", "id": "openai/gpt-4o-2024-11-20",          "plan": "premium"},
    "grok-4":                {"provider": "openrouter", "id": "x-ai/grok-2",                       "plan": "premium"},
}

# ── Fallback chains ──────────────────────────────────────────────────────────

FALLBACK_CHAINS: Dict[str, list] = {
    "fastest": [
        ("groq", "llama-3.1-8b-instant"),
        ("groq", "llama-3.3-70b-versatile"),
        ("gemini", "gemini-1.5-flash"),
        ("openrouter", "deepseek/deepseek-chat"),
    ],
    "balanced": [
        ("groq", "llama-3.3-70b-versatile"),
        ("gemini", "gemini-1.5-flash"),
        ("openrouter", "deepseek/deepseek-chat"),
        ("groq", "llama-3.1-8b-instant"),
    ],
    "best_quality": [
        ("openrouter", "anthropic/claude-sonnet-4"),
        ("openrouter", "deepseek/deepseek-r1"),
        ("gemini", "gemini-1.5-pro-latest"),
        ("groq", "llama-3.3-70b-versatile"),
    ],
}

# ── Provider clients ─────────────────────────────────────────────────────────

groq_client: Optional[AsyncOpenAI] = None
if settings.GROQ_API_KEY:
    groq_client = AsyncOpenAI(
        api_key=settings.GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
        timeout=30.0,
    )
else:
    logger.warning("GROQ_API_KEY not set — Groq provider disabled")

openrouter_client: Optional[AsyncOpenAI] = None
if settings.OPENROUTER_API_KEY:
    openrouter_client = AsyncOpenAI(
        api_key=settings.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        timeout=60.0,
        default_headers={
            "HTTP-Referer": "https://applivo.com",
            "X-Title": "Applivo AI Agent",
        },
    )
else:
    logger.warning("OPENROUTER_API_KEY not set — OpenRouter provider disabled")

gemini_client = None
if settings.GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        gemini_client = genai
    except ImportError:
        logger.warning("google-generativeai not installed, Gemini unavailable")


# ── Main Router ──────────────────────────────────────────────────────────────

class AIRouter:
    """
    Smart AI Router.
    - Routes to user's preferred provider/model
    - Injects reasoning depth (temperature, max_tokens, system prompt)
    - Injects application style (system prompt modifier)
    - Falls back through a provider chain on failure
    - Tracks all calls in ai_usage_logs
    """

    def __init__(self):
        self.default_provider = settings.AI_PROVIDER or "groq"
        self.default_fallback = settings.FALLBACK_PROVIDER or "gemini"

    async def chat_completions_create(
        self,
        messages: list,
        model: str = None,
        max_tokens: int = 1000,
        temperature: float = 0.4,
        user_id: str = None,
        endpoint: str = None,
        # User settings injection
        ai_settings: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> dict:
        """
        Create a chat completion with smart fallback.

        If ai_settings is provided, uses the user's configured provider/model/
        reasoning depth/style. Otherwise falls back to system defaults.

        ai_settings dict shape:
            provider, model, reasoning_depth, app_gen_style,
            fallback_enabled, fallback_strategy
        """
        start = time.time()

        # ── Resolve user settings ────────────────────────────────────────────
        user_provider = "groq"
        user_model_key = "auto"
        reasoning_depth = "balanced"
        app_style = None
        fallback_enabled = True
        fallback_strategy = "balanced"

        if ai_settings:
            user_provider = ai_settings.get("ai_provider", "groq") or "groq"
            user_model_key = ai_settings.get("ai_model", "auto") or "auto"
            reasoning_depth = ai_settings.get("reasoning_depth", "balanced") or "balanced"
            app_style = ai_settings.get("app_gen_style")
            fallback_enabled = ai_settings.get("fallback_enabled", True)
            fallback_strategy = ai_settings.get("fallback_strategy", "balanced") or "balanced"

        # ── Apply reasoning depth ────────────────────────────────────────────
        rdepth = REASONING_CONFIG.get(reasoning_depth, REASONING_CONFIG["balanced"])
        temperature = rdepth["temperature"]
        max_tokens = min(max_tokens, rdepth["max_tokens_cap"]) if max_tokens > rdepth["max_tokens_cap"] else max_tokens

        # Inject reasoning depth and style modifiers into system message
        messages = self._inject_modifiers(messages, rdepth["system_suffix"], app_style)

        # ── Resolve actual provider + model ─────────────────────────────────
        catalog_entry = MODEL_CATALOG.get(user_model_key)
        if catalog_entry:
            resolved_provider = catalog_entry["provider"]
            resolved_model = catalog_entry["id"]
        else:
            # user_model_key might already be a raw model ID
            resolved_provider = user_provider
            resolved_model = user_model_key or model or "llama-3.1-8b-instant"

        # ── Try preferred provider first ─────────────────────────────────────
        result, fallback_triggered = await self._try_providers(
            primary_provider=resolved_provider,
            primary_model=resolved_model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            fallback_enabled=fallback_enabled,
            fallback_strategy=fallback_strategy,
            start_time=start,
            user_id=user_id,
            endpoint=endpoint,
            **kwargs,
        )

        # Strip bold stars for clean UI
        if result.get("content"):
            result["content"] = result["content"].replace("**", "")

        return result

    def _inject_modifiers(
        self,
        messages: list,
        reasoning_suffix: str,
        app_style: Optional[str],
    ) -> list:
        """Inject reasoning depth and style modifiers into the system message."""
        messages = list(messages)  # copy
        style_suffix = ""
        if app_style and app_style in STYLE_PROMPTS:
            style_suffix = f"\n\nApplication Style: {STYLE_PROMPTS[app_style]}"

        combined_suffix = reasoning_suffix + style_suffix
        if not combined_suffix.strip():
            return messages

        # Find existing system message and append, or prepend a new one
        for i, msg in enumerate(messages):
            if msg.get("role") == "system":
                messages[i] = {**msg, "content": msg["content"] + combined_suffix}
                return messages

        # No system message — prepend one
        messages.insert(0, {"role": "system", "content": combined_suffix.strip()})
        return messages

    async def _try_providers(
        self,
        primary_provider: str,
        primary_model: str,
        messages: list,
        max_tokens: int,
        temperature: float,
        fallback_enabled: bool,
        fallback_strategy: str,
        start_time: float,
        user_id: str,
        endpoint: str,
        **kwargs,
    ) -> tuple[dict, bool]:
        """Try primary provider, then fallback chain if needed."""
        fallback_triggered = False
        last_error = None

        # Build attempt list: [primary, ...fallback_chain]
        attempts = [(primary_provider, primary_model)]
        if fallback_enabled:
            chain = FALLBACK_CHAINS.get(fallback_strategy, FALLBACK_CHAINS["balanced"])
            for p, m in chain:
                if (p, m) != (primary_provider, primary_model):
                    attempts.append((p, m))

        for i, (provider, model_id) in enumerate(attempts):
            is_fallback = i > 0
            if is_fallback:
                fallback_triggered = True

            try:
                result = await self._call_provider(
                    provider=provider,
                    model=model_id,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs,
                )
                latency = int((time.time() - start_time) * 1000)
                await self._record_usage(
                    provider=provider,
                    model=result.get("model", model_id),
                    usage=result.get("usage", {}),
                    latency=latency,
                    status_code=200,
                    fallback_triggered=fallback_triggered,
                    user_id=user_id,
                    endpoint=endpoint,
                )
                return result, fallback_triggered

            except Exception as e:
                error_str = str(e)
                status_code = 429 if ("429" in error_str or "rate_limit" in error_str.lower() or "quota" in error_str.lower()) else 500
                latency = int((time.time() - start_time) * 1000)
                await self._record_usage(
                    provider=provider,
                    model=model_id,
                    usage={},
                    latency=latency,
                    status_code=status_code,
                    success=False,
                    fallback_triggered=fallback_triggered,
                    user_id=user_id,
                    endpoint=endpoint,
                )
                logger.warning(
                    "AI provider failed",
                    provider=provider,
                    model=model_id,
                    status=status_code,
                    error=error_str[:120],
                    will_fallback=i + 1 < len(attempts),
                )
                last_error = e

                # Brief pause before next attempt on rate limit
                if status_code == 429 and i + 1 < len(attempts):
                    await asyncio.sleep(1)

        raise last_error or Exception("All AI providers failed")

    async def _call_provider(
        self,
        provider: str,
        model: str,
        messages: list,
        max_tokens: int,
        temperature: float,
        **kwargs,
    ) -> dict:
        """Dispatch to the correct provider."""
        if provider == "groq":
            return await self._groq_completion(messages, model, max_tokens, temperature, **kwargs)
        elif provider == "gemini":
            return await self._gemini_completion(messages, model, max_tokens, temperature)
        elif provider == "openrouter":
            return await self._openrouter_completion(messages, model, max_tokens, temperature, **kwargs)
        else:
            # Unknown provider — try groq as safe default
            return await self._groq_completion(messages, "llama-3.1-8b-instant", max_tokens, temperature)

    async def _groq_completion(self, messages, model, max_tokens, temperature, **kwargs) -> dict:
        if not groq_client:
            raise RuntimeError("Groq client not initialized — check GROQ_API_KEY")
        response = await groq_client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=messages,
            **kwargs,
        )
        return {
            "content": response.choices[0].message.content,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            },
            "provider": "groq",
            "tool_calls": [
                {"id": tc.id, "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in getattr(response.choices[0].message, "tool_calls", []) or []
            ],
        }

    async def _openrouter_completion(self, messages, model, max_tokens, temperature, **kwargs) -> dict:
        if not openrouter_client:
            raise RuntimeError("OpenRouter client not initialized — check OPENROUTER_API_KEY")
        response = await openrouter_client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=messages,
            **{k: v for k, v in kwargs.items() if k not in ("tools", "tool_choice")},
        )
        return {
            "content": response.choices[0].message.content,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            },
            "provider": "openrouter",
            "tool_calls": [],
        }

    async def _gemini_completion(self, messages, model, max_tokens, temperature) -> dict:
        if not gemini_client:
            raise RuntimeError("Gemini client not initialized — check GEMINI_API_KEY")

        gemini_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            if role == "system":
                gemini_messages.append({"role": "model", "parts": [msg["content"]]})
            elif role == "user":
                gemini_messages.append({"role": "user", "parts": [msg["content"]]})
            elif role == "assistant":
                gemini_messages.append({"role": "model", "parts": [msg["content"]]})

        candidates = [model] if model and "gemini" in model else [
            "gemini-1.5-flash",
            "gemini-1.5-pro-latest",
            "gemini-2.0-flash",
        ]

        last_error = None
        for candidate in candidates:
            try:
                gemini_model = gemini_client.GenerativeModel(candidate)
                loop = asyncio.get_running_loop()
                response = await asyncio.wait_for(
                    loop.run_in_executor(
                        None,
                        lambda: gemini_model.generate_content(
                            gemini_messages,
                            generation_config={"max_output_tokens": max_tokens, "temperature": temperature},
                        ),
                    ),
                    timeout=15.0,
                )
                usage_metadata = getattr(response, "usage_metadata", None)
                return {
                    "content": response.text,
                    "model": candidate,
                    "usage": {
                        "prompt_tokens": usage_metadata.prompt_token_count if usage_metadata else 0,
                        "completion_tokens": usage_metadata.candidates_token_count if usage_metadata else 0,
                        "total_tokens": usage_metadata.total_token_count if usage_metadata else 0,
                    },
                    "provider": "gemini",
                    "tool_calls": [],
                }
            except asyncio.TimeoutError:
                last_error = Exception(f"Gemini timeout on {candidate}")
            except Exception as e:
                last_error = e
                logger.warning("Gemini model failed", model=candidate, error=str(e)[:100])

        raise last_error or Exception("All Gemini models failed")

    async def _record_usage(
        self,
        provider: str,
        model: str,
        usage: dict,
        latency: int,
        status_code: int,
        success: bool = True,
        fallback_triggered: bool = False,
        user_id: str = None,
        endpoint: str = None,
    ):
        try:
            from app.core.database import get_db_context
            from app.models.ai_usage import AIUsageLog
            async with get_db_context() as db:
                log = AIUsageLog(
                    user_id=user_id,
                    provider=provider,
                    model=model,
                    prompt_tokens=usage.get("prompt_tokens", 0),
                    completion_tokens=usage.get("completion_tokens", 0),
                    total_tokens=usage.get("total_tokens", 0),
                    cached_tokens=usage.get("cached_tokens", 0),
                    latency_ms=latency,
                    status_code=status_code,
                    success=success,
                    endpoint_path=endpoint,
                )
                # Set fallback_triggered if column exists
                try:
                    log.fallback_triggered = fallback_triggered
                except Exception:
                    pass
                db.add(log)
                await db.commit()
        except Exception as e:
            logger.error("Failed to log AI usage", error=str(e))

    @staticmethod
    async def load_user_ai_settings(user_id: str) -> Optional[Dict[str, Any]]:
        """Load AI settings for a user from the database."""
        if not user_id:
            return None
        try:
            from app.core.database import get_db_context
            from app.models.user_settings import UserSettings
            from sqlalchemy import select
            async with get_db_context() as db:
                result = await db.execute(
                    select(UserSettings).where(UserSettings.user_id == user_id)
                )
                s = result.scalar_one_or_none()
                if not s:
                    return None
                return {
                    "ai_provider": s.ai_provider.value,
                    "ai_model": s.ai_model,
                    "reasoning_depth": s.reasoning_depth.value,
                    "app_gen_style": s.app_gen_style.value,
                    "fallback_enabled": s.fallback_enabled,
                    "fallback_strategy": s.fallback_strategy.value,
                }
        except Exception as e:
            logger.warning("Failed to load user AI settings", user_id=user_id, error=str(e))
            return None

    @property
    def available_providers(self) -> list:
        providers = []
        if groq_client:
            providers.append("groq")
        if gemini_client:
            providers.append("gemini")
        if openrouter_client:
            providers.append("openrouter")
        return providers


# ── Singleton ──────────────────────────────────────────────────────────────

ai_router = AIRouter()


async def chat_complete(
    messages: list,
    model: str = None,
    max_tokens: int = 1000,
    user_id: str = None,
    endpoint: str = None,
    load_user_settings: bool = False,
    **kwargs,
) -> str:
    """
    Simple helper to get a completion string.
    If load_user_settings=True, fetches the user's AI settings from DB.
    """
    ai_settings = None
    if load_user_settings and user_id:
        ai_settings = await AIRouter.load_user_ai_settings(user_id)

    result = await ai_router.chat_completions_create(
        messages=messages,
        model=model,
        max_tokens=max_tokens,
        user_id=user_id,
        endpoint=endpoint,
        ai_settings=ai_settings,
        **kwargs,
    )
    return result["content"]
