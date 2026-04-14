"""FastAPI routes definition."""

import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from typing import List

from internal.api.models import (
    MeetingCreateRequest, MeetingResponse, MeetingUpdateRequest,
    TranscriptionSegmentResponse, SpeakerMappingUpdateRequest,
    SummaryCreateRequest, SummaryResponse,
    TemplateCreateRequest, TemplateResponse
)
from fastapi.responses import Response, StreamingResponse
from internal.api.dependencies import (
    get_meeting_repo, get_transcription_repo, get_summary_repo, get_template_repo,
    get_audio_processor, get_transcriber, get_summarizer
)
from internal.repositories.meeting import MeetingRepository
from internal.repositories.transcription import TranscriptionRepository
from internal.repositories.summary import SummaryRepository
from internal.repositories.template import TemplateRepository
from internal.services.audio_processor import AudioProcessor
from internal.services.llm_transcriber import LLMTranscriber
from internal.services.llm_summarizer import LLMSummarizer
from internal.domain.meeting import Meeting, MeetingStatus
from internal.domain.transcription import SpeakerMapping
from internal.domain.template import Template
from internal.utils.error import AudioUploadError
from internal.utils.config import ConfigManager
from internal.services.audio_cleaner import AudioCleanupService

# Create router
router = APIRouter(prefix="/api", tags=["api"])


# Meeting routes
@router.post("/meetings", response_model=MeetingResponse)
async def create_meeting(
    file: UploadFile = File(...),
    title: str = Query(None),
    audio_processor: AudioProcessor = Depends(get_audio_processor),
    meeting_repo: MeetingRepository = Depends(get_meeting_repo),
    transcriber: LLMTranscriber = Depends(get_transcriber)
):
    """Upload audio file and create meeting."""
    # Validate file
    content = await file.read()
    audio_processor.validate_file(file.filename, len(content))

    # Reset file position for later reading
    await file.seek(0)

    # Create meeting
    meeting_id = str(uuid.uuid4())
    default_title = title or f"{uuid.uuid4()[:8]}会议"

    meeting = Meeting(
        id=meeting_id,
        title=default_title,
        original_filename=file.filename,
        status=MeetingStatus.UPLOADING
    )
    meeting_repo.create(meeting)

    # Save audio file
    audio_path = await audio_processor.save_audio(file, meeting_id)
    meeting.audio_path = audio_path
    meeting_repo.update(meeting)

    # Start transcription (background task would be better in production)
    # For now, we'll do it synchronously for simplicity
    try:
        await transcriber.transcribe_meeting(meeting_id, audio_path)
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))

    # Return updated meeting
    meeting = meeting_repo.get_by_id(meeting_id)
    return _meeting_to_response(meeting)


@router.get("/meetings", response_model=List[MeetingResponse])
async def list_meetings(
    meeting_repo: MeetingRepository = Depends(get_meeting_repo)
):
    """List all meetings."""
    meetings = meeting_repo.list_all()
    return [_meeting_to_response(m) for m in meetings]


@router.get("/meetings/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(
    meeting_id: str,
    meeting_repo: MeetingRepository = Depends(get_meeting_repo)
):
    """Get meeting by ID."""
    meeting = meeting_repo.get_by_id(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return _meeting_to_response(meeting)


@router.put("/meetings/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: str,
    request: MeetingUpdateRequest,
    meeting_repo: MeetingRepository = Depends(get_meeting_repo)
):
    """Update meeting (e.g., title)."""
    meeting = meeting_repo.get_by_id(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    meeting.title = request.title
    meeting_repo.update(meeting)

    return _meeting_to_response(meeting)


@router.get("/meetings/{meeting_id}/transcription", response_model=List[TranscriptionSegmentResponse])
async def get_transcription(
    meeting_id: str,
    transcription_repo: TranscriptionRepository = Depends(get_transcription_repo),
    meeting_repo: MeetingRepository = Depends(get_meeting_repo)
):
    """Get transcription for a meeting."""
    meeting = meeting_repo.get_by_id(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    segments = transcription_repo.get_segments_by_meeting(meeting_id)
    mappings = {m.speaker_id: m for m in transcription_repo.get_speaker_mappings(meeting_id)}

    return [
        TranscriptionSegmentResponse(
            id=seg.id,
            speaker_id=seg.speaker_id,
            display_name=mappings.get(seg.speaker_id, SpeakerMapping(seg.speaker_id)).display_name(),
            start_time=seg.start_time,
            end_time=seg.end_time,
            timestamp=seg.format_timestamp(),
            text=seg.text
        )
        for seg in segments
    ]


@router.post("/meetings/{meeting_id}/summaries", response_model=SummaryResponse)
async def create_summary(
    meeting_id: str,
    request: SummaryCreateRequest,
    summarizer: LLMSummarizer = Depends(get_summarizer)
):
    """Generate meeting summary."""
    try:
        summary = await summarizer.generate_summary_with_title(
            meeting_id,
            request.prompt
        )
        return _summary_to_response(summary)
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.get("/meetings/{meeting_id}/summaries", response_model=List[SummaryResponse])
async def list_summaries(
    meeting_id: str,
    summary_repo: SummaryRepository = Depends(get_summary_repo)
):
    """List all summaries for a meeting."""
    summaries = summary_repo.get_by_meeting(meeting_id)
    return [_summary_to_response(s) for s in summaries]


@router.put("/meetings/{meeting_id}/speakers")
async def update_speaker_mappings(
    meeting_id: str,
    request: SpeakerMappingUpdateRequest,
    transcription_repo: TranscriptionRepository = Depends(get_transcription_repo),
    meeting_repo: MeetingRepository = Depends(get_meeting_repo)
):
    """Update speaker mappings for a meeting."""
    meeting = meeting_repo.get_by_id(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # Update each speaker mapping
    for mapping_data in request.mappings:
        mapping = SpeakerMapping(
            speaker_id=mapping_data["speaker_id"],
            custom_name=mapping_data.get("custom_name")
        )
        transcription_repo.update_speaker_mapping(meeting_id, mapping)

    # Get updated mappings
    mappings = transcription_repo.get_speaker_mappings(meeting_id)
    return {"mappings": [{"speaker_id": m.speaker_id, "custom_name": m.custom_name} for m in mappings]}


@router.delete("/meetings/{meeting_id}/audio")
async def delete_audio(
    meeting_id: str,
    meeting_repo: MeetingRepository = Depends(get_meeting_repo)
):
    """Manually delete audio file for a meeting."""
    meeting = meeting_repo.get_by_id(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    if not meeting.can_delete_audio():
        raise HTTPException(status_code=400, detail="Audio cannot be deleted")

    # Mark audio as deleted
    from datetime import datetime
    meeting.audio_deleted_at = datetime.now()
    meeting_repo.update(meeting)

    # Delete actual file
    import os
    if meeting.audio_path and os.path.exists(meeting.audio_path):
        os.remove(meeting.audio_path)

    return {"message": "Audio deleted successfully"}


@router.get("/summaries/{summary_id}/export")
async def export_summary(
    summary_id: str,
    format: str = Query("markdown", enum=["markdown", "txt"]),
    summary_repo: SummaryRepository = Depends(get_summary_repo)
):
    """Export summary in specified format."""
    from internal.utils.export import export_as_markdown, export_as_txt

    summary = summary_repo.get_by_id(summary_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")

    if format == "markdown":
        content = export_as_markdown(summary)
        filename = f"summary_{summary.id}.md"
        media_type = "text/markdown"
    else:  # txt
        content = export_as_txt(summary)
        filename = f"summary_{summary.id}.txt"
        media_type = "text/plain"

    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


# Template routes
@router.get("/templates", response_model=List[TemplateResponse])
async def list_templates(
    template_repo: TemplateRepository = Depends(get_template_repo)
):
    """List all templates."""
    templates = template_repo.list_all()
    return [_template_to_response(t) for t in templates]


@router.post("/templates", response_model=TemplateResponse)
async def create_template(
    request: TemplateCreateRequest,
    template_repo: TemplateRepository = Depends(get_template_repo)
):
    """Create a custom template."""
    template = Template(
        id=None,  # Will be generated
        name=request.name,
        content=request.content,
        is_default=request.is_default,
        is_preset=False
    )
    template_repo.create(template)

    # Retrieve created template
    created = template_repo.get_by_name(request.name)
    if not created:
        raise HTTPException(status_code=500, detail="Failed to create template")

    return _template_to_response(created)


@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: str,
    template_repo: TemplateRepository = Depends(get_template_repo)
):
    """Delete a custom template."""
    template = template_repo.get_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    if template.is_preset:
        raise HTTPException(status_code=400, detail="Cannot delete preset templates")

    template_repo.delete(template_id)
    return {"message": "Template deleted successfully"}


# Config management routes
@router.get("/config/llm")
async def get_llm_config():
    """Get current LLM configuration (without sensitive data)."""
    config_manager = ConfigManager()

    try:
        config = config_manager.load()
        llm_config = config.get("llm", {})

        # Return config without API keys
        services_info = {}
        for service_name, service_config in llm_config.get("services", {}).items():
            services_info[service_name] = {
                "model": service_config.get("model", ""),
                "configured": config_manager.is_service_configured(service_name)
            }

        return {
            "default_service": llm_config.get("default_service", ""),
            "available_services": list(llm_config.get("services", {}).keys()),
            "services": services_info
        }
    except FileNotFoundError:
        return {
            "default_service": "",
            "available_services": [],
            "services": {}
        }


@router.put("/config/llm")
async def update_llm_config(request: dict):
    """Update LLM service configuration."""
    service_name = request.get("service")
    api_key = request.get("api_key")
    app_id = request.get("app_id")
    model = request.get("model")

    if not service_name:
        raise HTTPException(status_code=400, detail="Service name is required")

    config_manager = ConfigManager()

    try:
        config_manager.update_llm_service(service_name, api_key, app_id, model)
        return {"message": "Configuration updated successfully"}
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/config/llm/validate")
async def validate_llm_service(request: dict):
    """Validate LLM service configuration."""
    service_name = request.get("service")

    if not service_name:
        raise HTTPException(status_code=400, detail="Service name is required")

    try:
        from internal.llm.factory import validate_llm_config
        validate_llm_config()
        return {"valid": True, "message": "Configuration is valid"}
    except Exception as err:
        return {"valid": False, "message": str(err)}


@router.get("/config/storage")
async def get_storage_info():
    """Get audio storage information."""
    try:
        cleanup_service = AudioCleanupService()
        info = cleanup_service.get_audio_storage_info()
        return info
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/config/cleanup")
async def run_audio_cleanup():
    """Manually trigger audio cleanup."""
    try:
        cleanup_service = AudioCleanupService()
        result = cleanup_service.cleanup_expired_audios()
        return result
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


def _meeting_to_response(meeting: Meeting) -> MeetingResponse:
    """Convert Meeting entity to response model."""
    return MeetingResponse(
        id=meeting.id,
        title=meeting.title,
        original_filename=meeting.original_filename,
        status=meeting.status.value,
        progress=meeting.progress,
        error_message=meeting.error_message,
        created_at=meeting.created_at,
        updated_at=meeting.updated_at,
        is_audio_available=meeting.is_audio_available()
    )


def _summary_to_response(summary) -> SummaryResponse:
    """Convert Summary entity to response model."""
    return SummaryResponse(
        id=summary.id,
        meeting_id=summary.meeting_id,
        version=summary.version,
        prompt=summary.prompt,
        content=summary.content,
        created_at=summary.created_at
    )


def _template_to_response(template: Template) -> TemplateResponse:
    """Convert Template entity to response model."""
    return TemplateResponse(
        id=template.id,
        name=template.name,
        content=template.content,
        is_default=template.is_default,
        is_preset=template.is_preset
    )
