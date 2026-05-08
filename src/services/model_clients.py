"""
Concrete implementations of LLM clients
"""

import time
from typing import Dict, Any, Optional
import httpx
from src.services.llm_client import LLMClient, ModelConfig
from src.utils.logging import get_logger
from src.config import settings

logger = get_logger(__name__)


# ============================================================================
# PHASE 1: Local Model Client (Llama)
# ============================================================================


class LlamaClient(LLMClient):
    """
    Client for local Llama model
    Simulates a self-hosted model endpoint
    """

    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.endpoint = settings.local_llama_endpoint.rstrip("/")

    async def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate response using local Llama model endpoint"""
        start_time = time.time()

        try:
            payload = {
                "prompt": prompt,
                "max_tokens": max_tokens or self.config.max_tokens,
                "temperature": temperature,
            }

            timeout = httpx.Timeout(settings.request_timeout)
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(f"{self.endpoint}/generate", json=payload)
                resp.raise_for_status()
                data = resp.json()

            response_text = data.get("response") or data.get("text")
            if not response_text:
                raise ValueError("Local model returned empty response")

            tokens_used = int(data.get("tokens_used") or len(prompt.split()) + 50)

            latency_ms = (time.time() - start_time) * 1000

            logger.info(
                "llama_generation_complete",
                model=self.config.name,
                latency_ms=latency_ms,
                tokens=tokens_used,
            )

            return {
                "response": response_text,
                "tokens_used": tokens_used,
                "latency_ms": latency_ms,
                "model": self.config.name,
            }

        except Exception as e:
            logger.error("llama_generation_error", error=str(e))
            raise

    async def health_check(self) -> bool:
        """Check if Llama endpoint is available"""
        try:
            timeout = httpx.Timeout(5.0)
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.get(f"{self.endpoint}/health")
                return resp.status_code < 500
        except Exception:
            return False


# ============================================================================
# PHASE 1: Premium Model Client (GPT-4 / Claude)
# ============================================================================


class OpenAIClient(LLMClient):
    """Client for OpenAI models"""

    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.api_key = settings.openai_api_key
        self.base_url = settings.openai_base_url.rstrip("/")

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate response using OpenAI API"""
        start_time = time.time()

        try:
            if not self.api_key:
                raise RuntimeError("OPENAI_API_KEY not configured")

            payload = {
                "model": self.config.name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
            }
            if max_tokens is not None:
                payload["max_tokens"] = max_tokens

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            timeout = httpx.Timeout(settings.request_timeout)
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()

            choices = data.get("choices", [])
            if not choices:
                raise ValueError("OpenAI returned no choices")

            message = choices[0].get("message", {})
            response_text = message.get("content", "")
            usage = data.get("usage", {})
            tokens_used = int(usage.get("total_tokens") or len(prompt.split()) + 100)

            latency_ms = (time.time() - start_time) * 1000

            logger.info(
                "openai_generation_complete",
                model=self.config.name,
                latency_ms=latency_ms,
                tokens=tokens_used,
            )

            return {
                "response": response_text,
                "tokens_used": tokens_used,
                "latency_ms": latency_ms,
                "model": self.config.name,
            }

        except Exception as e:
            logger.error("openai_generation_error", error=str(e))
            raise

    async def health_check(self) -> bool:
        """Check if OpenAI API is available"""
        try:
            if not self.api_key:
                return False

            timeout = httpx.Timeout(5.0)
            headers = {"Authorization": f"Bearer {self.api_key}"}
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.get(f"{self.base_url}/models", headers=headers)
                return resp.status_code < 500
        except Exception:
            return False


class ClaudeClient(LLMClient):
    """Client for Anthropic Claude models"""

    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.api_key = settings.anthropic_api_key
        self.base_url = settings.anthropic_base_url.rstrip("/")

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate response using Claude API"""
        start_time = time.time()

        try:
            if not self.api_key:
                raise RuntimeError("ANTHROPIC_API_KEY not configured")

            payload = {
                "model": self.config.name,
                "max_tokens": max_tokens or 1024,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}],
            }

            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }

            timeout = httpx.Timeout(settings.request_timeout)
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(
                    f"{self.base_url}/messages",
                    json=payload,
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()

            content_blocks = data.get("content", [])
            text_chunks = [block.get("text", "") for block in content_blocks if block.get("type") == "text"]
            response_text = "\n".join(chunk for chunk in text_chunks if chunk)
            usage = data.get("usage", {})
            tokens_used = int(
                usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
            ) or len(prompt.split()) + 80

            latency_ms = (time.time() - start_time) * 1000

            logger.info(
                "claude_generation_complete",
                model=self.config.name,
                latency_ms=latency_ms,
                tokens=tokens_used,
            )

            return {
                "response": response_text,
                "tokens_used": tokens_used,
                "latency_ms": latency_ms,
                "model": self.config.name,
            }

        except Exception as e:
            logger.error("claude_generation_error", error=str(e))
            raise

    async def health_check(self) -> bool:
        """Check if Claude API is available"""
        try:
            if not self.api_key:
                return False

            timeout = httpx.Timeout(5.0)
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            }
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.get(f"{self.base_url}/models", headers=headers)
                return resp.status_code < 500
        except Exception:
            return False
