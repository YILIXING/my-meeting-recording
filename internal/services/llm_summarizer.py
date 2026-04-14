"""LLM summary generation service."""

import uuid
from typing import List
from internal.domain.summary import Summary
from internal.domain.meeting import MeetingStatus
from internal.repositories.summary import SummaryRepository
from internal.repositories.transcription import TranscriptionRepository
from internal.repositories.meeting import MeetingRepository
from internal.llm.base import LLMService
from internal.utils.error import SummaryGenerationError


class LLMSummarizer:
    """Service for generating meeting summaries using LLM."""

    def __init__(
        self,
        summary_repo: SummaryRepository,
        transcription_repo: TranscriptionRepository,
        meeting_repo: MeetingRepository,
        llm_service: LLMService
    ):
        """
        Initialize summarizer service.

        Args:
            summary_repo: Summary repository
            transcription_repo: Transcription repository
            meeting_repo: Meeting repository
            llm_service: LLM service for generation
        """
        self.summary_repo = summary_repo
        self.transcription_repo = transcription_repo
        self.meeting_repo = meeting_repo
        self.llm_service = llm_service

    async def generate_summary(
        self,
        meeting_id: str,
        prompt: str
    ) -> Summary:
        """
        Generate meeting summary from transcription.

        Args:
            meeting_id: Meeting ID
            prompt: User prompt for summary generation

        Returns:
            Summary: Generated summary entity

        Raises:
            SummaryGenerationError: If generation fails
        """
        # Check if meeting can generate summary
        meeting = self.meeting_repo.get_by_id(meeting_id)
        if not meeting or not meeting.can_generate_summary():
            raise SummaryGenerationError(
                f"Meeting cannot generate summary: {meeting_id}"
            )

        try:
            # Get transcription text (without speaker labels)
            segments = self.transcription_repo.get_segments_by_meeting(meeting_id)
            transcription_text = "\n".join([seg.text for seg in segments])

            # Generate summary using LLM
            content = await self.llm_service.generate_summary(
                transcription_text,
                prompt
            )

            # Get next version number
            existing_summaries = self.summary_repo.get_by_meeting(meeting_id)
            next_version = len(existing_summaries) + 1

            # Create summary
            summary = Summary(
                id=str(uuid.uuid4()),
                meeting_id=meeting_id,
                version=next_version,
                prompt=prompt,
                content=content
            )

            self.summary_repo.create(summary)
            return summary

        except Exception as err:
            raise SummaryGenerationError(f"Summary generation failed: {err}") from err

    async def generate_summary_with_title(
        self,
        meeting_id: str,
        prompt: str
    ) -> Summary:
        """
        Generate summary and auto-update meeting title.

        Args:
            meeting_id: Meeting ID
            prompt: User prompt for summary generation

        Returns:
            Summary: Generated summary entity
        """
        # Generate summary
        summary = await self.generate_summary(meeting_id, prompt)

        # Generate and update title
        try:
            title = await self.llm_service.generate_title(summary.content)

            # Update meeting title (truncate to 30 chars if needed)
            if len(title) > 30:
                title = title[:30]

            meeting = self.meeting_repo.get_by_id(meeting_id)
            if meeting:
                meeting.title = title
                self.meeting_repo.update(meeting)

        except Exception:
            # Title generation failure should not fail the summary
            pass

        return summary
