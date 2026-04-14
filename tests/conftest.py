"""Pytest configuration and fixtures."""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def test_db_path(temp_dir: Path) -> str:
    """Create a test database path."""
    return str(temp_dir / "test.db")


@pytest.fixture
def test_audio_dir(temp_dir: Path) -> Path:
    """Create a test audio directory."""
    audio_dir = temp_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    return audio_dir


@pytest.fixture
def mock_config(temp_dir: Path) -> dict:
    """Create a mock configuration for testing."""
    return {
        "llm": {
            "default_service": "doubao",
            "services": {
                "doubao": {
                    "api_key": "test_key",
                    "model": "test-model",
                    "endpoint": "https://test.example.com"
                }
            }
        },
        "audio": {
            "max_file_size_mb": 300,
            "supported_formats": [".mp3", ".m4a", ".wav", ".webm", ".mp4", ".mpeg"],
            "auto_cleanup_days": 7
        },
        "database": {
            "path": str(temp_dir / "test.db")
        }
    }
