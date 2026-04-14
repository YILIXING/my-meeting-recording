"""Universal LLM client supporting OpenAI and Anthropic protocols."""

import json
from typing import List, Optional, Dict, Any
from internal.llm.base import LLMService
from internal.utils.error import LLMConfigError


class UniversalLLM(LLMService):
    """Universal LLM client supporting multiple API protocols."""

    def __init__(
        self,
        api_key: str,
        protocol: str = "openai",
        model: str = "",
        endpoint: str = None,
        extra: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize universal LLM client.

        Args:
            api_key: API key for authentication
            protocol: API protocol to use ("openai" or "anthropic")
            model: Model identifier
            endpoint: API endpoint URL
            extra: Extra configuration (e.g., app_id for Doubao)
        """
        self.api_key = api_key
        self.protocol = protocol.lower()
        self.model = model
        self.endpoint = endpoint or self._get_default_endpoint()
        self.extra = extra or {}

        # Validate protocol
        if self.protocol not in ["openai", "anthropic"]:
            raise LLMConfigError(f"Unsupported protocol: {protocol}")

        # Lazy import of aiohttp
        try:
            import aiohttp
            self.aiohttp = aiohttp
        except ImportError:
            raise LLMConfigError("aiohttp is required for LLM operations. Install with: pip install aiohttp")

    def _get_default_endpoint(self) -> str:
        """Get default endpoint based on protocol."""
        if self.protocol == "openai":
            return "https://api.openai.com/v1"
        elif self.protocol == "anthropic":
            return "https://api.anthropic.com"
        return "https://api.openai.com/v1"

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        headers = {
            "Content-Type": "application/json"
        }

        if self.protocol == "openai":
            headers["Authorization"] = f"Bearer {self.api_key}"
        elif self.protocol == "anthropic":
            headers["x-api-key"] = self.api_key
            headers["anthropic-version"] = "2023-06-01"

        return headers

    async def _call_chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 4096
    ) -> str:
        """
        Call chat completion API.

        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens in response

        Returns:
            Response text content
        """
        url = f"{self.endpoint}/chat/completions"

        if self.protocol == "openai":
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens
            }
        else:  # anthropic
            # Convert OpenAI format to Anthropic format
            payload = {
                "model": self.model,
                "messages": messages[1:],  # Skip system message
                "max_tokens": max_tokens,
                "system": messages[0]["content"] if messages and messages[0]["role"] == "system" else ""
            }

        headers = self._get_headers()

        async with self.aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=120)) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise LLMConfigError(f"API request failed: {response.status} - {error_text}")

                data = await response.json()

                # Extract response text based on protocol
                if self.protocol == "openai":
                    return data["choices"][0]["message"]["content"]
                else:  # anthropic
                    return data["content"][0]["text"]

    async def transcribe_audio(
        self,
        audio_path: str,
        progress_callback: Optional[callable] = None
    ) -> List[dict]:
        """
        Transcribe audio file (placeholder - not fully implemented).

        Args:
            audio_path: Path to audio file
            progress_callback: Optional callback for progress updates

        Returns:
            List of transcript segments with speaker info
        """
        # For now, return placeholder data
        # Full implementation would use the audio transcription API
        return [
            {
                "speaker_id": "speaker_1",
                "start_time": 0.0,
                "end_time": 5.0,
                "text": "这是一个示例转写结果。"
            }
        ]

    async def generate_summary(
        self,
        transcription_text: str,
        prompt: str
    ) -> str:
        """
        Generate meeting summary from transcription.

        Args:
            transcription_text: Full transcription text
            prompt: Custom prompt for summary generation

        Returns:
            Generated summary text
        """
        system_prompt = """你是一个专业的会议记录助手。请根据提供的会议转写内容，生成结构清晰、重点突出的会议纪要。

会议纪要应包含：
1. 会议主题
2. 参会人员（根据说话人推断）
3. 主要讨论内容
4. 决策事项
5. 行动项（包括负责人和截止时间）

请使用Markdown格式输出。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"会议转写内容：\n\n{transcription_text}\n\n{prompt}"}
        ]

        return await self._call_chat(messages)

    async def generate_title(self, summary_content: str) -> str:
        """
        Generate meeting title from summary.

        Args:
            summary_content: Meeting summary content

        Returns:
            Generated title (max 30 characters)
        """
        messages = [
            {"role": "system", "content": "请为会议生成一个简洁的标题，不超过30个字。"},
            {"role": "user", "content": f"会议纪要：\n{summary_content}"}
        ]

        title = await self._call_chat(messages, max_tokens=100)

        # Truncate if too long
        if len(title) > 30:
            title = title[:27] + "..."

        return title

    async def validate_config(self) -> bool:
        """
        Validate API configuration by making a test request.

        Returns:
            True if configuration is valid
        """
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'OK' if you can read this."}
            ]

            response = await self._call_chat(messages, max_tokens=10)
            return len(response) > 0
        except Exception as err:
            raise LLMConfigError(f"Configuration validation failed: {err}") from err
