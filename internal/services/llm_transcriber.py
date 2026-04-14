"""LLM transcription service."""

import uuid
from typing import Optional, Callable
from internal.domain.meeting import Meeting, MeetingStatus
from internal.domain.transcription import TranscriptSegment
from internal.repositories.meeting import MeetingRepository
from internal.repositories.transcription import TranscriptionRepository
from internal.llm.base import LLMService
from internal.services.state_machine import MeetingStateMachine
from internal.utils.error import TranscriptionError


class LLMTranscriber:
    """Service for transcribing audio using LLM."""

    def __init__(
        self,
        meeting_repo: MeetingRepository,
        transcription_repo: TranscriptionRepository,
        llm_service: LLMService
    ):
        """
        Initialize transcriber service.

        Args:
            meeting_repo: Meeting repository
            transcription_repo: Transcription repository
            llm_service: LLM service for transcription
        """
        self.meeting_repo = meeting_repo
        self.transcription_repo = transcription_repo
        self.llm_service = llm_service

    async def transcribe_meeting(
        self,
        meeting_id: str,
        audio_path: str,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> None:
        """
        Transcribe meeting audio and store results.

        Args:
            meeting_id: Meeting ID
            audio_path: Path to audio file
            progress_callback: Optional progress callback

        Raises:
            TranscriptionError: If transcription fails
        """
        # Get meeting
        meeting = self.meeting_repo.get_by_id(meeting_id)
        if not meeting:
            raise TranscriptionError(f"Meeting not found: {meeting_id}")

        # Update state to transcribing
        state_machine = MeetingStateMachine(meeting)
        state_machine.transition_to(MeetingStatus.TRANSCRIBING)
        self.meeting_repo.update(meeting)

        try:
            # Transcribe using LLM
            results = await self.llm_service.transcribe_audio(
                audio_path,
                progress_callback
            )

            # Store transcription results
            for result in results:
                segment = TranscriptSegment(
                    id=str(uuid.uuid4()),
                    meeting_id=meeting_id,
                    speaker_id=result["speaker_id"],
                    start_time=result["start"],
                    end_time=result["end"],
                    text=result["text"]
                )
                self.transcription_repo.create_segment(segment)

            # Update state to completed
            state_machine.transition_to(MeetingStatus.COMPLETED)
            self.meeting_repo.update(meeting)

        except Exception as err:
            # Update state to failed
            state_machine.transition_to(
                MeetingStatus.FAILED,
                error_message=str(err)
            )
            self.meeting_repo.update(meeting)
            raise TranscriptionError(f"Transcription failed: {err}") from err
