"""Audio processing service."""

from pathlib import Path
from fastapi import UploadFile
from internal.utils.error import AudioUploadError


class AudioProcessor:
    """Service for processing audio files."""

    MAX_FILE_SIZE = 300 * 1024 * 1024  # 300MB
    SUPPORTED_FORMATS = {".mp3", ".m4a", ".wav", ".webm", ".mp4", ".mpeg"}

    def validate_file(self, filename: str, file_size: int) -> None:
        """
        Validate audio file format and size.

        Args:
            filename: Name of the uploaded file
            file_size: Size of the file in bytes

        Raises:
            AudioUploadError: If file format or size is invalid
        """
        # Check file format
        ext = Path(filename).suffix.lower()
        if ext not in self.SUPPORTED_FORMATS:
            raise AudioUploadError(
                f"不支持的音频格式: {ext}，支持的格式: {', '.join(self.SUPPORTED_FORMATS)}"
            )

        # Check file size
        if file_size > self.MAX_FILE_SIZE:
            size_mb = file_size / 1024 / 1024
            raise AudioUploadError(
                f"文件大小超过限制（最大300MB，当前: {size_mb:.1f}MB）"
            )

    async def save_audio(self, file: UploadFile, meeting_id: str, audio_dir: str = "data/audio") -> str:
        """
        Save uploaded audio file.

        Args:
            file: Uploaded file
            meeting_id: Meeting ID for organizing audio files
            audio_dir: Base directory for audio storage

        Returns:
            str: Path to saved audio file

        Raises:
            AudioUploadError: If file save fails
        """
        audio_path = Path(audio_dir) / meeting_id
        audio_path.mkdir(parents=True, exist_ok=True)

        ext = Path(file.filename).suffix
        file_path = audio_path / f"audio{ext}"

        try:
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            return str(file_path)
        except Exception as err:
            raise AudioUploadError(f"保存音频文件失败") from err
