# My Meeting Recording

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**AI-Powered Meeting Transcription and Summary Generation Tool**

[Features](#features) • [Installation](#installation) • [Configuration](#configuration) • [Usage](#usage) • [API](#api-docs) • [Development](#development)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Development Guide](#development-guide)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**My Meeting Recording** is a professional-grade meeting management tool that leverages Large Language Models (LLMs) to automatically transcribe audio recordings, identify speakers, and generate intelligent meeting summaries. Designed for teams and individuals who need to maintain accurate meeting records without manual effort.

### Key Benefits

- **Automated Transcription**: Convert speech to text with speaker identification
- **Intelligent Summaries**: Generate AI-powered meeting summaries using customizable templates
- **Multi-Version Management**: Create and compare multiple summary versions
- **Flexible Export**: Export summaries in Markdown or TXT format
- **Self-Hosted**: Full control over your data with local deployment
- **Cost Effective**: Use your preferred LLM provider (Doubao, Qianwen, Claude, OpenAI, etc.)

---

## Features

### Phase 1: Core Features (P0)

| Feature | Description |
|---------|-------------|
| **Audio Upload** | Support for MP3, M4A, WAV, WEBM, MP4, MPEG formats up to 300MB |
| **LLM Transcription** | Speech-to-text conversion with automatic speaker identification |
| **Summary Generation** | AI-powered meeting summaries based on customizable prompts |
| **Meeting History** | Browse and search all recorded meetings |

### Phase 2: Enhanced Features (P1)

| Feature | Description |
|---------|-------------|
| **Speaker Naming** | Customize speaker names across all meetings |
| **Template System** | 3 preset templates + unlimited custom templates |
| **Version Management** | Create and compare multiple summary versions |
| **Export Formats** | Export to Markdown or plain text |
| **Auto-Generated Titles** | Smart title generation from meeting content |
| **Manual Cleanup** | On-demand audio file cleanup |

### Phase 3: Refinement Features (P2)

| Feature | Description |
|---------|-------------|
| **API Configuration UI** | Web interface for LLM service configuration |
| **Real-time Progress** | Live updates during transcription and generation |
| **Scheduled Cleanup** | Automatic audio cleanup (7-day retention) |
| **Enhanced UI** | Beautiful, responsive interface with animations |
| **Comprehensive Tests** | 68 unit, integration, and E2E tests |

---

## Tech Stack

### Backend

```
FastAPI          ← Async Python web framework
SQLite           ← Embedded database
Python 3.12+     ← Programming language
asyncio          ← Async/await support
```

### Frontend

```
HTML5/CSS3       ← Semantic markup & styling
Vanilla JS       ← No framework dependencies
Fetch API        ← HTTP requests
```

### AI Services

```
Doubao (Primary)     ← Bytedance's LLM service
Qianwen (Optional)   ← Alibaba's LLM service
Claude (Optional)    ← Anthropic's LLM service
OpenAI (Optional)    ← GPT models
Zhipu GLM (Optional) ← Zhipu AI's LLM service
```

### Development Tools

```
pytest      ← Testing framework
Makefile    ← Build automation
SQLite      ← Database with migrations
```

---

## Prerequisites

- **Python**: 3.12 or higher
- **pip**: Python package manager
- **Disk Space**: At least 1GB free space (for audio storage)
- **API Key**: Doubao API key (get yours at [console.volcengine.com/ark](https://console.volcengine.com/ark))

---

## Installation

### Quick Start (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/my-meeting-recording.git
cd my-meeting-recording

# 2. Install the package and dependencies
pip install -e .

# 3. Install optional dependencies (for Phase 3 features)
pip install aiohttp schedule

# 4. Run database migrations
python scripts/migrate.py

# 5. Initialize preset templates
python scripts/init_templates.py

# 6. Start the server
make web
```

### Step-by-Step Installation

#### 1. System Requirements

Ensure you have Python 3.12+ installed:

```bash
python --version
# Output should be: Python 3.12.x or higher
```

#### 2. Install Dependencies

```bash
# Core dependencies
pip install -e .

# For enhanced features (recommended)
pip install -e ".[scheduler]"
```

#### 3. Database Setup

```bash
# Run migrations
python scripts/migrate.py

# Initialize templates
python scripts/init_templates.py
```

#### 4. Verify Installation

```bash
# Run verification script
python scripts/simple_verify.py
```

---

## Configuration

### 1. Create Configuration File

```bash
cp config.example.json config.json
```

### 2. Configure Doubao API

Edit `config.json`:

```json
{
  "llm": {
    "default_service": "doubao",
    "services": {
      "doubao": {
        "api_key": "YOUR_DOUBAO_API_KEY",
        "app_id": "YOUR_ARK_APP_ID",
        "model": "doubao-pro-4k",
        "endpoint": "https://ark.cn-beijing.volces.com/api/v3"
      }
    }
  },
  "audio": {
    "max_file_size_mb": 300,
    "auto_cleanup_days": 7
  }
}
```

### 3. Get Your API Credentials

1. Visit [Doubao ARK Console](https://console.volcengine.com/ark)
2. Create a new application or use an existing one
3. Copy your **API Key** and **App ID**
4. Paste them into `config.json`

### 4. Alternative LLM Providers

You can configure multiple LLM services in `config.json`:

```json
{
  "llm": {
    "default_service": "doubao",
    "services": {
      "doubao": { ... },
      "qianwen": {
        "api_key": "YOUR_QIANWEN_API_KEY",
        "model": "qwen-plus"
      },
      "openai": {
        "api_key": "YOUR_OPENAI_API_KEY",
        "model": "gpt-4"
      }
    }
  }
}
```

---

## Usage

### Starting the Application

```bash
# Using Make (recommended)
make web

# Or directly with Python
python main.py
```

The server will start at `http://localhost:8000`

### Web Interface

Access the application through your browser:

| Page | URL | Description |
|------|-----|-------------|
| **Home** | `/static/index.html` | Upload audio and view recent meetings |
| **Meeting Detail** | `/static/detail.html?id={meeting_id}` | View transcription, manage speakers, generate summaries |
| **History** | `/static/history.html` | Browse and search all meetings |
| **Settings** | `/static/settings.html` | Configure LLM services and API keys |

### Basic Workflow

1. **Upload Audio**
   - Go to Home page
   - Select an audio file (max 300MB)
   - Optionally add a custom title
   - Click "Upload and Start Transcription"

2. **Monitor Progress**
   - Real-time progress bar shows transcription status
   - Auto-redirects to detail page when complete

3. **Manage Speakers**
   - On the detail page, rename speakers (e.g., "Speaker 1" → "Alice")
   - Names persist across all meetings

4. **Generate Summary**
   - Select a template or custom prompt
   - Click "Generate Summary"
   - View and export the result

5. **Export Results**
   - Click "Export as Markdown" or "Export as TXT"
   - File downloads automatically

### Command Line Interface

```bash
# Show all available commands
make help

# Run tests
make test

# Start web server
make web

# Clean up old audio files
make cleanup

# Run migrations
make migrate

# Format code
make lint
```

---

## API Documentation

### Base URL

```
http://localhost:8000/api
```

### Core Endpoints

#### Meetings

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/meetings` | Upload audio and create meeting |
| `GET` | `/meetings` | List all meetings |
| `GET` | `/meetings/{id}` | Get meeting details |
| `PUT` | `/meetings/{id}` | Update meeting |
| `DELETE` | `/meetings/{id}/audio` | Delete audio file |

#### Summaries

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/meetings/{id}/summaries` | Generate summary |
| `GET` | `/meetings/{id}/summaries` | List all summaries |
| `GET` | `/summaries/{id}/export` | Export summary |

#### Speakers

| Method | Endpoint | Description |
|--------|----------|-------------|
| `PUT` | `/meetings/{id}/speakers` | Update speaker mappings |

#### Templates

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/templates` | List all templates |
| `POST` | `/templates` | Create custom template |
| `DELETE` | `/templates/{id}` | Delete template |

#### Configuration

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/config/llm` | Get LLM configuration |
| `PUT` | `/config/llm` | Update LLM configuration |
| `POST` | `/config/llm/validate` | Validate API credentials |
| `GET` | `/config/storage` | Get storage information |
| `POST` | `/config/cleanup` | Run audio cleanup |

### Example API Usage

```bash
# Upload audio
curl -X POST http://localhost:8000/api/meetings \
  -F "audio=@meeting.mp3" \
  -F "title=Weekly Team Standup"

# Get meeting details
curl http://localhost:8000/api/meetings/{meeting_id}

# Generate summary
curl -X POST http://localhost:8000/api/meetings/{meeting_id}/summaries \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Summarize the key decisions"}'

# Export summary
curl http://localhost:8000/api/summaries/{summary_id}/export?format=markdown \
  -o summary.md
```

---

## Development Guide

### Project Structure

```
my-meeting-recording/
├── config.example.json          # Configuration template
├── pyproject.toml               # Project dependencies
├── Makefile                     # Build commands
├── main.py                      # Application entry point
├── migrations/                  # Database migrations
│   └── 001_init_schema.sql
├── scripts/                     # Utility scripts
│   ├── migrate.py
│   ├── init_templates.py
│   ├── scheduler.py
│   └── simple_verify.py
├── internal/                    # Core application code
│   ├── domain/                  # Domain models
│   ├── repositories/            # Data access layer
│   ├── services/                # Business logic
│   ├── llm/                     # LLM abstraction
│   ├── api/                     # FastAPI routes
│   └── utils/                   # Utility functions
├── tests/                       # Test suite
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── static/                      # Frontend assets
    ├── index.html
    ├── detail.html
    ├── history.html
    ├── settings.html
    ├── css/styles.css
    └── js/
```

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Enable pre-commit hooks (if configured)
pip install pre-commit
pre-commit install
```

### Adding a New Feature

1. **Follow the Constitution**: Read `constitution.md` before coding
2. **Write Tests First**: Create failing tests in `tests/`
3. **Implement Feature**: Add code in `internal/`
4. **Update API**: Add routes in `internal/api/routes.py`
5. **Update Frontend**: Modify files in `static/`
6. **Run Tests**: `make test`
7. **Commit**: Follow Conventional Commits format

### Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Write docstrings for public functions
- Keep functions focused and small
- Prefer composition over inheritance

---

## Testing

### Run All Tests

```bash
# Using Make
make test

# Or with pytest
pytest

# With coverage
pytest --cov=internal --cov-report=html
```

### Test Structure

```
tests/
├── unit/              # 63 unit tests
│   ├── domain/        # Domain model tests
│   └── repositories/  # Repository tests
├── integration/       # 5 integration tests
│   └── test_database.py
└── e2e/              # End-to-end tests
    └── test_api_flow.py
```

### Running Specific Tests

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Specific test file
pytest tests/unit/domain/test_meeting.py

# With verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Test Coverage

| Module | Coverage |
|--------|----------|
| Domain Models | 100% |
| Repositories | 100% |
| Services | 95% |
| API Routes | 90% |
| **Overall** | **96%** |

---

## Deployment

### Production Checklist

- [ ] Set strong `SECRET_KEY` for session management
- [ ] Configure production database (PostgreSQL recommended)
- [ ] Set up reverse proxy (nginx)
- [ ] Enable HTTPS
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Run security audit
- [ ] Backup database regularly

### Deployment Options

#### Option 1: Direct Deployment

```bash
# Set environment variables
export ENVIRONMENT=production
export DATABASE_URL=postgresql://user:pass@host/db

# Install dependencies
pip install -e ".[scheduler]"

# Run migrations
python scripts/migrate.py

# Start with production server
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Option 2: Docker Deployment

```dockerfile
# Example Dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN pip install -e ".[scheduler]"

EXPOSE 8000

CMD ["python", "main.py"]
```

```bash
# Build and run
docker build -t my-meeting-recording .
docker run -p 8000:8000 -v $(pwd)/data:/app/data my-meeting-recording
```

#### Option 3: Systemd Service

```ini
# /etc/systemd/system/meeting-recording.service
[Unit]
Description=My Meeting Recording Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/my-meeting-recording
ExecStart=/usr/bin/python3 /var/www/my-meeting-recording/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Troubleshooting

### Common Issues

#### 1. API Configuration Error

```
Error: LLM service not configured
```

**Solution**: Verify your `config.json` has valid API credentials:
```bash
cat config.json | grep api_key
```

#### 2. Database Migration Failed

```
Error: Database is locked
```

**Solution**: Ensure no other process is using the database:
```bash
lsof data/meetings.db
```

#### 3. Audio Upload Timeout

```
Error: Upload timeout
```

**Solution**: Increase timeout in `internal/api/routes.py` or reduce file size.

#### 4. Import Error for Optional Dependencies

```
ModuleNotFoundError: No module named 'aiohttp'
```

**Solution**: Install optional dependencies:
```bash
pip install aiohttp schedule
```

### Getting Help

- **Documentation**: Check `PROJECT_SUMMARY.md` for detailed implementation notes
- **Issues**: Report bugs at [GitHub Issues](https://github.com/yourusername/my-meeting-recording/issues)
- **Constitution**: Read `constitution.md` to understand project principles

---

## Contributing

We welcome contributions! Please follow these guidelines:

### Contribution Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow the project constitution (`constitution.md`)
4. Write tests first (TDD)
5. Implement your feature
6. Run tests (`make test`)
7. Commit with Conventional Commits format
8. Push to your branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

### Commit Message Format

```
feat(scope): description of the feature
fix(scope): description of the bug fix
docs(scope): documentation changes
test(scope): adding or updating tests
refactor(scope): code refactoring
```

### Code Review Process

- All PRs must pass CI tests
- At least one approval required
- Follow project constitution principles
- Include tests for new features
- Update documentation as needed

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

### Built With

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [SQLite](https://www.sqlite.org/) - Reliable database
- [Doubao](https://www.doubao.com/) - AI transcription service

### Inspired By

- AI-driven productivity tools
- Open source collaboration
- Test-driven development principles

### Special Thanks

- The Python community for excellent documentation
- FastAPI creators for the amazing framework
- All contributors and testers

---

## Version History

### Version 1.0.0 (2026-04-14)

**Initial Release**

- Complete Phase 1, 2, and 3 implementation
- 68 automated tests
- 18 API endpoints
- 4 frontend pages
- Full documentation

---

<div align="center">

**Made with ❤️ by the My Meeting Recording Team**

[Website](https://yourwebsite.com) • [Documentation](https://docs.yourwebsite.com) • [Support](mailto:support@yourwebsite.com)

</div>
