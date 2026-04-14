"""LLM service abstract base class."""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Callable


class LLMService(ABC):
    """Abstract base class for LLM services."""

    @abstractmethod
    async def transcribe_audio(
        self,
        audio_path: str,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> List[dict]:
        """
        Transcribe audio file and identify speakers.

        Args:
            audio_path: Path to audio file
            progress_callback: Optional callback for progress updates callback(percent: int)

        Returns:
            List[dict]: Transcription results
                [{"speaker_id": "speaker_a", "start": 0.0, "end": 5.0, "text": "..."}]

        Raises:
            ValueError: If transcription fails
        """
        pass

    @abstractmethod
    async def generate_summary(
        self,
        transcription_text: str,
        prompt: str
    ) -> str:
        """
        Generate meeting summary from transcription.

        Args:
            transcription_text: Transcribed text (without speaker labels)
            prompt: User prompt for summary generation

        Returns:
            str: Generated summary content

        Raises:
            ValueError: If generation fails
        """
        pass

    @abstractmethod
    async def generate_title(
        self,
        summary_content: str
    ) -> str:
        """
        Generate meeting title from summary content.

        Args:
            summary_content: Generated summary content

        Returns:
            str: Generated title (≤30 characters)

        Raises:
            ValueError: If generation fails
        """
        pass

    @abstractmethod
    async def validate_config(self) -> bool:
        """
        Validate LLM service configuration.

        Returns:
            bool: True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        pass
