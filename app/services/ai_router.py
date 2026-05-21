"""
app/services/ai_router.py
─────────────────────────
Dual AI Provider Router
- Primary: Groq (fast, low latency)
- Fallback: Gemini (high capacity)
- Auto-switches on rate limits (429) or errors
"""

from __future__ import annotations
import asyncio
from concurrent.futures import ThreadPoolExecutor
import structlog
from typing import Optional

from openai import AsyncOpenAI
from app.core.config import settings

logger = structlog.get_logger()

# Initialize clients
groq_client = AsyncOpenAI(
    api_key=settings.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

# Gemini client
gemini_client = None
if settings.GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        gemini_client = genai
    except ImportError:
        logger.warning("google-generativeai not installed, Gemini unavailable")


class AIRouter:
    """Routes AI requests to primary or fallback provider."""

    def __init__(self):
        self.primary = settings.AI_PROVIDER or "groq"
        self.fallback = settings.FALLBACK_PROVIDER or "gemini"
        self.use_gemini = gemini_client is not None

    async def chat_completions_create(
        self,
        messages: list,
        model: str = None,
        max_tokens: int = 1000,
        temperature: float = 0.1,
        user_id: str = None,
        endpoint: str = None,
        **kwargs
    ) -> dict:
        """
        Create chat completion with automatic fallback.
        Tries primary first, falls back to Gemini on failure.
        """
        import time
        start_time = time.time()
        model = model or settings.OPENAI_MODEL_LIGHT or "llama3-8b-8192"
        
        last_error = None
        
        # Try primary provider (Groq) with a quick retry on 429
        for attempt in range(2):
            if self.primary == "groq":
                try:
                    result = await self._groq_completion(messages, model, max_tokens, temperature, **kwargs)
                    # Strip bold stars as requested by user for clean UI
                    if "content" in result and result["content"]:
                        result["content"] = result["content"].replace("**", "")
                    
                    latency = int((time.time() - start_time) * 1000)
                    await self._record_usage(
                        provider="groq",
                        model=result["model"],
                        usage=result["usage"],
                        latency=latency,
                        status_code=200,
                        user_id=user_id,
                        endpoint=endpoint
                    )
                    return result
                except Exception as e:
                    error_msg = str(e)
                    status_code = 429 if ("429" in error_msg or "rate_limit" in error_msg.lower() or "quota" in error_msg.lower()) else 500
                    
                    if status_code == 429 and attempt == 0:
                        logger.warning("Groq rate limited, waiting 2s before retry or fallback")
                        await asyncio.sleep(2)
                        continue
                        
                    latency = int((time.time() - start_time) * 1000)
                    # Log the failure before fallback
                    await self._record_usage(
                        provider="groq",
                        model=model,
                        usage={"total_tokens": 0},
                        latency=latency,
                        status_code=status_code,
                        success=False,
                        user_id=user_id,
                        endpoint=endpoint
                    )
                    
                    if status_code == 429:
                        logger.warning("Groq rate limited, trying fallback", error=error_msg[:100])
                    else:
                        logger.error("Groq failed, trying fallback", error=error_msg[:100])
                    last_error = e
                    break # Go to fallback
        
        # Try fallback (Gemini)
        if self.use_gemini:
            try:
                result = await self._gemini_completion(messages, model, max_tokens, temperature)
                
                # Strip bold stars as requested by user for clean UI
                if "content" in result and result["content"]:
                    result["content"] = result["content"].replace("**", "")
                    
                latency = int((time.time() - start_time) * 1000)
                await self._record_usage(
                    provider="gemini",
                    model=result["model"],
                    usage=result["usage"],
                    latency=latency,
                    status_code=200,
                    user_id=user_id,
                    endpoint=endpoint
                )
                return result
            except Exception as e:
                latency = int((time.time() - start_time) * 1000)
                await self._record_usage(
                    provider="gemini",
                    model=model,
                    usage={"total_tokens": 0},
                    latency=latency,
                    status_code=500,
                    success=False,
                    user_id=user_id,
                    endpoint=endpoint
                )
                logger.error("Gemini fallback failed", error=str(e)[:100])
                last_error = e
        
        # All providers failed
        raise last_error or Exception(f"All AI providers failed. Primary: {self.primary}, Fallback: {self.fallback}")

    async def _record_usage(
        self, 
        provider: str, 
        model: str, 
        usage: dict, 
        latency: int, 
        status_code: int, 
        success: bool = True,
        user_id: str = None,
        endpoint: str = None
    ):
        """Log usage to database in a background-safe way."""
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
                    endpoint_path=endpoint
                )
                db.add(log)
                await db.commit()
        except Exception as e:
            # Don't let logging failures crash the AI request
            logger.error("Failed to log AI usage", error=str(e))

    async def _groq_completion(
        self,
        messages: list,
        model: str,
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> dict:
        """Groq completion call."""
        response = await groq_client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=messages,
            **kwargs
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
                {
                    "id": tc.id,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in getattr(response.choices[0].message, "tool_calls", []) or []
            ]
        }

    async def _gemini_completion(
        self,
        messages: list,
        model: str,
        max_tokens: int,
        temperature: float
    ) -> dict:
        """Gemini completion call (convert OpenAI format to Gemini)."""
        gemini_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            if role == "system":
                gemini_messages.append({"role": "model", "parts": [msg["content"]]})
            elif role == "user":
                gemini_messages.append({"role": "user", "parts": [msg["content"]]})
            elif role == "assistant":
                gemini_messages.append({"role": "model", "parts": [msg["content"]]})
        
        gemini_candidates = [
            "gemini-1.5-flash",
            "gemini-1.5-pro-latest",
            "gemini-2.0-flash"
        ]

        response = None
        selected_model = None
        last_error = None

        for attempt in range(2):
            for candidate in gemini_candidates:
                try:
                    gemini_model = gemini_client.GenerativeModel(candidate)
                    loop = asyncio.get_running_loop()
                    response = await asyncio.wait_for(
                        loop.run_in_executor(
                            None,
                            lambda: gemini_model.generate_content(
                                gemini_messages,
                                generation_config={
                                    "max_output_tokens": max_tokens,
                                    "temperature": temperature,
                                }
                            )
                        ),
                        timeout=10.0
                    )
                    selected_model = candidate
                    break
                except asyncio.TimeoutError:
                    logger.error("Gemini fallback timed out after 10s", model=candidate)
                    last_error = Exception(f"Gemini timeout for model {candidate}")
                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg or "quota" in error_msg.lower():
                        logger.warning("Gemini model quota reached", model=candidate)
                    else:
                        logger.warning("Gemini model unavailable, trying next", model=candidate, error=error_msg[:120])
                    last_error = e
            
            if response is not None:
                break
            
            if attempt == 0 and ("429" in str(last_error) or "quota" in str(last_error).lower()):
                logger.warning("All Gemini models throttled, waiting 3s before final retry")
                await asyncio.sleep(3)
            else:
                break

        if response is None:
            raise Exception(f"Gemini fallback failed for all models: {str(last_error)[:180]}")
        
        usage_metadata = getattr(response, "usage_metadata", None)

        return {
            "content": response.text,
            "model": selected_model,
            "usage": {
                "prompt_tokens": usage_metadata.prompt_token_count if usage_metadata else 0,
                "completion_tokens": usage_metadata.candidates_token_count if usage_metadata else 0,
                "total_tokens": usage_metadata.total_token_count if usage_metadata else 0,
                "cached_tokens": getattr(usage_metadata, "cached_content_token_count", 0) if usage_metadata else 0,
            },
            "provider": "gemini"
        }

    @property
    def available_providers(self) -> list:
        """List available providers."""
        providers = ["groq"]
        if self.use_gemini:
            providers.append("gemini")
        return providers


# Singleton instance
ai_router = AIRouter()


# Convenience function for simple use
async def chat_complete(
    messages: list,
    model: str = None,
    max_tokens: int = 1000,
    user_id: str = None,
    endpoint: str = None,
    **kwargs
) -> str:
    """Simple function to get chat completion with fallback."""
    result = await ai_router.chat_completions_create(
        messages=messages,
        model=model,
        max_tokens=max_tokens,
        user_id=user_id,
        endpoint=endpoint,
        **kwargs,
    )
    return result["content"]