"""Meeting state machine."""

from datetime import datetime
from typing import Optional
from internal.domain.meeting import Meeting, MeetingStatus
from internal.utils.error import MeetingError


class InvalidStateTransitionError(MeetingError):
    """Raised when invalid state transition is attempted."""
    pass


class MeetingStateMachine:
    """State machine for meeting status transitions."""

    # Valid state transitions
    VALID_TRANSITIONS = {
        MeetingStatus.UPLOADING: [
            MeetingStatus.TRANSCRIBING,
            MeetingStatus.FAILED,
            MeetingStatus.CANCELLED
        ],
        MeetingStatus.TRANSCRIBING: [
            MeetingStatus.COMPLETED,
            MeetingStatus.FAILED,
            MeetingStatus.CANCELLED
        ],
        MeetingStatus.GENERATING: [
            MeetingStatus.COMPLETED,
            MeetingStatus.FAILED
        ],
        MeetingStatus.COMPLETED: [],  # Terminal state
        MeetingStatus.FAILED: [],     # Terminal state
        MeetingStatus.CANCELLED: [],  # Terminal state
    }

    def __init__(self, meeting: Meeting):
        """
        Initialize state machine with a meeting.

        Args:
            meeting: Meeting entity to manage
        """
        self.meeting = meeting

    def can_transition_to(self, new_status: MeetingStatus) -> bool:
        """
        Check if transition to new status is valid.

        Args:
            new_status: Target status

        Returns:
            bool: True if transition is valid
        """
        valid_transitions = self.VALID_TRANSITIONS.get(self.meeting.status, [])
        return new_status in valid_transitions

    def transition_to(
        self,
        new_status: MeetingStatus,
        error_message: Optional[str] = None
    ) -> Meeting:
        """
        Transition meeting to new status.

        Args:
            new_status: Target status
            error_message: Optional error message for failed state

        Returns:
            Meeting: Updated meeting entity

        Raises:
            InvalidStateTransitionError: If transition is invalid
        """
        if not self.can_transition_to(new_status):
            raise InvalidStateTransitionError(
                f"无效的状态转换: {self.meeting.status.value} -> {new_status.value}"
            )

        self.meeting.status = new_status
        self.meeting.updated_at = datetime.now()

        if error_message:
            self.meeting.error_message = error_message

        return self.meeting
