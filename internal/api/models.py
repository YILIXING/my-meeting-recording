"""API request and response models."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Meeting models
class MeetingCreateRequest(BaseModel):
    """Request model for creating a meeting."""
    title: Optional[str] = None


class MeetingResponse(BaseModel):
    """Response model for meeting data."""
    id: str
    title: str
    original_filename: str
    status: str
    progress: int
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_audio_available: bool


class MeetingUpdateRequest(BaseModel):
    """Request model for updating a meeting."""
    title: str = Field(..., min_length=1, max_length=100)


# Transcription models
class TranscriptionSegmentResponse(BaseModel):
    """Response model for transcription segment."""
    id: str
    speaker_id: str
    display_name: str
    start_time: float
    end_time: float
    timestamp: str
    text: str


class SpeakerMappingUpdateRequest(BaseModel):
    """Request model for updating speaker mappings."""
    mappings: List[dict] = Field(
        ...,
        min_items=1,
        examples=[[{"speaker_id": "speaker_a", "custom_name": "张三"}]]
    )


# Summary models
class SummaryCreateRequest(BaseModel):
    """Request model for creating a summary."""
    prompt: str = Field(..., min_length=1, max_length=2000)
    save_as_template: bool = False
    template_name: Optional[str] = Field(None, max_length=100)


class SummaryResponse(BaseModel):
    """Response model for summary data."""
    id: str
    meeting_id: str
    version: int
    prompt: str
    content: str
    created_at: datetime


# Template models
class TemplateCreateRequest(BaseModel):
    """Request model for creating a template."""
    name: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1, max_length=2000)
    is_default: bool = False


class TemplateResponse(BaseModel):
    """Response model for template data."""
    id: str
    name: str
    content: str
    is_default: bool
    is_preset: bool


# Config models
class LLMConfigResponse(BaseModel):
    """Response model for LLM configuration."""
    default_service: str
    available_services: List[str]


class LLMConfigUpdateRequest(BaseModel):
    """Request model for updating LLM configuration."""
    default_service: str
    api_key: Optional[str] = None
