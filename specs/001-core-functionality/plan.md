# Plan 001: 技术实现方案

**Version:** 1.1
**Status:** Draft
**Created:** 2026-04-14
**Updated:** 2026-04-14
**Architect:** Claude Code
**Based on:** Spec 001 v1.1, Constitution v1.0

---

## 架构愿景

构建一个**简单、可测试、显式**的会议纪要系统，严格遵循项目宪法的三大原则：
1. **简单性优先** - YAGNI，标准库优先，拒绝过度抽象
2. **测试先行** - TDD循环，参数化测试，集成测试优先
3. **明确性原则** - 显式错误处理，无全局变量，依赖注入

---

## 1. 技术选型

### 1.1 Web框架

| 需求 | 推荐方案 | 备选方案 | 决策理由 |
|------|----------|----------|----------|
| Web服务 | **FastAPI** | Flask | FastAPI原生异步支持，自动文档，类型提示 |
| 前端 | **原生HTML/JS + fetch API** | React/Vue | 符合"简单性优先"，无需构建工具链 |
| 任务队列 | **asyncio + background tasks** | Celery | P0阶段无需分布式，避免过度工程 |

### 1.2 存储方案

| 数据类型 | 推荐方案 | 备选方案 | 决策理由 |
|----------|----------|----------|----------|
| 元数据（会议、纪要） | **SQLite** | PostgreSQL | 单用户场景，SQLite零配置，Python标准库支持 |
| 音频文件 | **本地文件系统** | OSS/S3 | 简单直接，避免网络依赖 |
| 配置文件 | **JSON** | YAML/TOML | 简单，Python标准库支持 |

### 1.3 LLM集成

| 服务 | SDK | 优先级 | 备注 |
|------|-----|--------|------|
| 豆包 | `volcengine` | **默认** | 国产，性价比高，支持音频输入 |
| 千问 | `dashscope` | P1 | 阿里云，稳定性好 |
| 智谱GLM | `zhipuai` | P1 | 国产，支持GLM-4 |
| Claude | `anthropic` | P2 | 质量高，成本较高 |
| OpenAI | `openai` | P2 | GPT-4o支持音频输入 |

**设计原则**:
- LLM服务抽象为统一接口，支持灵活切换
- 默认使用豆包，用户可通过配置切换其他服务
- 所有LLM服务需支持：音频转文字+说话人识别、纪要生成、标题生成

---

## 2. 项目目录结构

```
my-meeting-recording/
├── config.json                    # API配置文件（用户级，不入库）
├── pyproject.toml                 # 项目配置
├── Makefile                       # 构建脚本
├── main.py                        # 应用入口
│
├── data/                          # 数据目录（.gitignore）
│   ├── meetings.db                # SQLite数据库
│   └── audio/                     # 音频文件存储
│       └── {meeting_id}/
│           └── audio.{ext}
│
├── internal/                      # 内部包（核心业务逻辑）
│   ├── __init__.py
│   │
│   ├── domain/                    # 领域模型
│   │   ├── __init__.py
│   │   ├── meeting.py             # 会议实体
│   │   ├── transcription.py       # 转写结果实体
│   │   ├── summary.py             # 纪要实体
│   │   ├── speaker.py             # 说话人实体
│   │   └── template.py            # 提示词模板实体
│   │
│   ├── repositories/              # 数据访问层
│   │   ├── __init__.py
│   │   ├── base.py                # Repository基类
│   │   ├── meeting.py             # 会议数据访问
│   │   ├── transcription.py       # 转写结果数据访问
│   │   └── summary.py             # 纪要数据访问
│   │
│   ├── services/                  # 业务服务层
│   │   ├── __init__.py
│   │   ├── audio_processor.py     # 音频处理服务
│   │   ├── llm_transcriber.py     # LLM转写服务
│   │   ├── llm_summarizer.py      # LLM纪要生成服务
│   │   ├── title_generator.py     # 标题生成服务
│   │   └── audio_cleaner.py       # 音频清理服务
│   │
│   ├── llm/                       # LLM抽象层
│   │   ├── __init__.py
│   │   ├── base.py                # LLM基类
│   │   ├── doubao.py              # 豆包实现
│   │   ├── qianwen.py             # 千问实现
│   │   ├── claude.py              # Claude实现
│   │   └── factory.py             # LLM工厂
│   │
│   ├── api/                       # API层
│   │   ├── __init__.py
│   │   ├── routes.py              # 路由定义
│   │   ├── models.py              # 请求/响应模型
│   │   └── dependencies.py        # 依赖注入
│   │
│   └── utils/                     # 工具函数
│       ├── __init__.py
│       ├── error.py               # 错误处理工具
│       ├── time.py                # 时间处理工具
│       └── export.py              # 导出工具
│
├── tests/                         # 测试目录
│   ├── __init__.py
│   ├── conftest.py                # pytest配置
│   ├── unit/                      # 单元测试
│   ├── integration/               # 集成测试
│   └── fixtures/                  # 测试固件
│       ├── audio/                 # 测试音频文件
│       └── db/                    # 测试数据库
│
└── static/                        # 静态资源（前端）
    ├── index.html                 # 主页
    ├── history.html               # 历史记录
    ├── detail.html                # 会议详情
    ├── settings.html              # 设置页
    ├── css/
    │   └── styles.css
    └── js/
        └── app.js
```

---

## 3. 核心领域模型

### 3.1 Meeting（会议）

```python
# internal/domain/meeting.py
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

class MeetingStatus(Enum):
    UPLOADING = "uploading"
    TRANSCRIBING = "transcribing"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Meeting:
    id: str                          # UUID
    title: str                       # 会议标题（初始为时间戳）
    original_filename: str           # 原始文件名
    audio_path: Optional[str]        # 音频文件路径
    status: MeetingStatus            # 当前状态
    progress: int = 0                # 进度百分比（0-100）
    error_message: Optional[str] = None  # 错误信息
    created_at: datetime = None      # 创建时间
    updated_at: datetime = None      # 更新时间
    audio_deleted_at: Optional[datetime] = None  # 音频删除时间

    def is_audio_available(self) -> bool:
        """检查音频文件是否可用"""
        return self.audio_path is not None and self.audio_deleted_at is None

    def can_generate_summary(self) -> bool:
        """检查是否可以生成纪要"""
        return self.status == MeetingStatus.COMPLETED

    def can_delete_audio(self) -> bool:
        """检查是否可以删除音频"""
        return self.is_audio_available() and self.status == MeetingStatus.COMPLETED
```

### 3.2 Transcription（转写结果）

```python
# internal/domain/transcription.py
from dataclasses import dataclass
from typing import List
from datetime import datetime

@dataclass
class TranscriptSegment:
    id: str                          # UUID
    meeting_id: str                  # 关联会议ID
    speaker_id: str                  # 说话人ID（如"speaker_a"）
    start_time: float                # 开始时间（秒）
    end_time: float                  # 结束时间（秒）
    text: str                        # 转写文本
    created_at: datetime = None

    def format_timestamp(self) -> str:
        """格式化时间戳为 HH:MM:SS"""
        hours = int(self.start_time // 3600)
        minutes = int((self.start_time % 3600) // 60)
        seconds = int(self.start_time % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

@dataclass
class SpeakerMapping:
    speaker_id: str                  # 原始ID（如"speaker_a"）
    custom_name: Optional[str]       # 自定义名称（如"张三"）

    def display_name(self) -> str:
        """获取显示名称"""
        return self.custom_name if self.custom_name else self.speaker_id.replace("_", " ").title()
```

### 3.3 Summary（会议纪要）

```python
# internal/domain/summary.py
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Summary:
    id: str                          # UUID
    meeting_id: str                  # 关联会议ID
    version: int                     # 版本号
    prompt: str                      # 使用的提示词
    content: str                     # 纪要内容
    created_at: datetime = None      # 创建时间
```

### 3.4 Template（提示词模板）

```python
# internal/domain/template.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Template:
    id: str                          # UUID
    name: str                        # 模板名称
    content: str                     # 提示词内容
    is_default: bool = False         # 是否为默认模板
    is_preset: bool = False          # 是否为预设模板
```

---

## 4. 数据库Schema

### 4.1 meetings表

```sql
CREATE TABLE meetings (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    audio_path TEXT,
    status TEXT NOT NULL,  -- MeetingStatus枚举值
    progress INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    audio_deleted_at TIMESTAMP
);

CREATE INDEX idx_meetings_status ON meetings(status);
CREATE INDEX idx_meetings_created_at ON meetings(created_at DESC);
```

### 4.2 transcript_segments表

```sql
CREATE TABLE transcript_segments (
    id TEXT PRIMARY KEY,
    meeting_id TEXT NOT NULL,
    speaker_id TEXT NOT NULL,
    start_time REAL NOT NULL,
    end_time REAL NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE
);

CREATE INDEX idx_transcript_meeting_id ON transcript_segments(meeting_id);
CREATE INDEX idx_transcript_start_time ON transcript_segments(start_time);
```

### 4.3 speaker_mappings表

```sql
CREATE TABLE speaker_mappings (
    id TEXT PRIMARY KEY,
    meeting_id TEXT NOT NULL,
    speaker_id TEXT NOT NULL,
    custom_name TEXT,
    UNIQUE(meeting_id, speaker_id),
    FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE
);

CREATE INDEX idx_speaker_mappings_meeting_id ON speaker_mappings(meeting_id);
```

### 4.4 summaries表

```sql
CREATE TABLE summaries (
    id TEXT PRIMARY KEY,
    meeting_id TEXT NOT NULL,
    version INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE
);

CREATE INDEX idx_summaries_meeting_id ON summaries(meeting_id);
CREATE INDEX idx_summaries_created_at ON summaries(created_at DESC);
```

### 4.5 templates表

```sql
CREATE TABLE templates (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    content TEXT NOT NULL,
    is_default BOOLEAN DEFAULT 0,
    is_preset BOOLEAN DEFAULT 0
);
```

---

## 5. API设计

### 5.1 RESTful API路由

| 方法 | 路径 | 功能 |
|------|------|------|
| **会议管理** |
| POST | `/api/meetings` | 上传音频，创建会议 |
| GET | `/api/meetings` | 获取会议列表 |
| GET | `/api/meetings/{id}` | 获取会议详情 |
| PUT | `/api/meetings/{id}` | 更新会议信息（标题等） |
| DELETE | `/api/meetings/{id}` | 删除会议 |
| POST | `/api/meetings/{id}/cancel` | 取消处理 |
| **转写结果** |
| GET | `/api/meetings/{id}/transcription` | 获取转写结果 |
| PUT | `/api/meetings/{id}/speakers` | 更新说话人映射 |
| **纪要管理** |
| POST | `/api/meetings/{id}/summaries` | 生成纪要 |
| GET | `/api/meetings/{id}/summaries` | 获取纪要列表 |
| GET | `/api/summaries/{id}` | 获取纪要详情 |
| DELETE | `/api/summaries/{id}` | 删除纪要版本 |
| **导出** |
| GET | `/api/summaries/{id}/export` | 导出纪要（支持format参数） |
| **音频清理** |
| DELETE | `/api/meetings/{id}/audio` | 手动删除音频 |
| **模板管理** |
| GET | `/api/templates` | 获取模板列表 |
| POST | `/api/templates` | 创建自定义模板 |
| PUT | `/api/templates/{id}` | 更新模板 |
| DELETE | `/api/templates/{id}` | 删除模板 |
| **系统配置** |
| GET | `/api/config/llm` | 获取LLM配置 |
| PUT | `/api/config/llm` | 更新LLM配置 |
| POST | `/api/config/llm/validate` | 验证LLM配置 |

### 5.2 请求/响应模型示例

```python
# internal/api/models.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class MeetingCreateRequest(BaseModel):
    file: UploadFile  # FastAPI UploadFile
    title: Optional[str] = None

class MeetingResponse(BaseModel):
    id: str
    title: str
    original_filename: str
    status: str
    progress: int
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_audio_available: bool

class TranscriptionSegmentResponse(BaseModel):
    id: str
    speaker_id: str
    display_name: str  # 应用自定义名称后的显示名
    start_time: float
    end_time: float
    timestamp: str  # 格式化的时间戳
    text: str

class SummaryCreateRequest(BaseModel):
    prompt: str
    save_as_template: bool = False
    template_name: Optional[str] = None

class SummaryResponse(BaseModel):
    id: str
    meeting_id: str
    version: int
    prompt: str
    content: str
    created_at: datetime

class SpeakerMappingUpdateRequest(BaseModel):
    mappings: List[dict]  # [{"speaker_id": "speaker_a", "custom_name": "张三"}]
```

---

## 6. 核心服务设计

### 6.1 LLM抽象层

```python
# internal/llm/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class LLMService(ABC):
    """LLM服务抽象基类"""

    @abstractmethod
    async def transcribe_audio(
        self,
        audio_path: str,
        progress_callback: Optional[callable] = None
    ) -> List[dict]:
        """
        转写音频并识别说话人

        Args:
            audio_path: 音频文件路径
            progress_callback: 进度回调函数 callback(percent: int)

        Returns:
            List[dict]: [{"speaker_id": "speaker_a", "start": 0.0, "end": 5.0, "text": "..."}]

        Raises:
            ValueError: 转写失败时抛出
        """
        pass

    @abstractmethod
    async def generate_summary(
        self,
        transcription_text: str,
        prompt: str
    ) -> str:
        """
        生成会议纪要

        Args:
            transcription_text: 转写文本（不含说话人标识）
            prompt: 用户提示词

        Returns:
            str: 生成的纪要内容

        Raises:
            ValueError: 生成失败时抛出
        """
        pass

    @abstractmethod
    async def generate_title(
        self,
        summary_content: str
    ) -> str:
        """
        生成会议标题

        Args:
            summary_content: 纪要内容

        Returns:
            str: 生成的标题（≤30字符）

        Raises:
            ValueError: 生成失败时抛出
        """
        pass

    @abstractmethod
    async def validate_config(self) -> bool:
        """验证LLM配置是否有效"""
        pass
```

### 6.2 音频处理服务

```python
# internal/services/audio_processor.py
class AudioProcessor:
    """音频处理服务"""

    MAX_FILE_SIZE = 300 * 1024 * 1024  # 300MB
    SUPPORTED_FORMATS = {".mp3", ".m4a", ".wav", ".webm", ".mp4", ".mpeg"}

    def validate_file(self, filename: str, file_size: int) -> None:
        """
        验证音频文件

        Args:
            filename: 文件名
            file_size: 文件大小（字节）

        Raises:
            ValueError: 文件不符合要求时抛出
        """
        # 检查文件格式
        ext = Path(filename).suffix.lower()
        if ext not in self.SUPPORTED_FORMATS:
            raise ValueError(f"不支持的音频格式: {ext}，支持的格式: {', '.join(self.SUPPORTED_FORMATS)}")

        # 检查文件大小
        if file_size > self.MAX_FILE_SIZE:
            raise ValueError(f"文件大小超过限制（最大300MB，当前: {file_size / 1024 / 1024:.1f}MB）")

    async def save_audio(self, file: UploadFile, meeting_id: str) -> str:
        """
        保存音频文件

        Args:
            file: 上传的文件
            meeting_id: 会议ID

        Returns:
            str: 音频文件路径
        """
        audio_dir = Path("data/audio") / meeting_id
        audio_dir.mkdir(parents=True, exist_ok=True)

        ext = Path(file.filename).suffix
        audio_path = audio_dir / f"audio{ext}"

        try:
            async with aiofiles.open(audio_path, "wb") as f:
                content = await file.read()
                await f.write(content)
            return str(audio_path)
        except Exception as err:
            raise ValueError(f"保存音频文件失败") from err
```

### 6.3 错误处理策略

```python
# internal/utils/error.py
class MeetingError(Exception):
    """会议相关错误基类"""
    pass

class AudioUploadError(MeetingError):
    """音频上传错误"""
    pass

class TranscriptionError(MeetingError):
    """转写错误"""
    pass

class SummaryGenerationError(MeetingError):
    """纪要生成错误"""
    pass

class LLMConfigError(MeetingError):
    """LLM配置错误"""
    pass

# 使用示例
try:
    await llm_service.transcribe_audio(audio_path, progress_callback)
except LLMConfigError as err:
    # LLM配置错误，提示用户检查API密钥
    raise ValueError("LLM配置无效，请检查API密钥") from err
except Exception as err:
    # 其他未知错误
    raise ValueError(f"转写失败: {str(err)}") from err
```

---

## 7. 状态机设计

```python
# internal/services/state_machine.py
from enum import Enum
from typing import Optional

class MeetingStateMachine:
    """会议状态机"""

    def __init__(self, meeting: Meeting):
        self.meeting = meeting

    def can_transition_to(self, new_status: MeetingStatus) -> bool:
        """检查是否可以转换到新状态"""
        valid_transitions = {
            MeetingStatus.UPLOADING: [MeetingStatus.TRANSCRIBING, MeetingStatus.FAILED, MeetingStatus.CANCELLED],
            MeetingStatus.TRANSCRIBING: [MeetingStatus.COMPLETED, MeetingStatus.FAILED, MeetingStatus.CANCELLED],
            MeetingStatus.GENERATING: [MeetingStatus.COMPLETED, MeetingStatus.FAILED],
            MeetingStatus.COMPLETED: [],  # 终态
            MeetingStatus.FAILED: [],     # 终态
            MeetingStatus.CANCELLED: [],  # 终态
        }
        return new_status in valid_transitions.get(self.meeting.status, [])

    def transition_to(self, new_status: MeetingStatus, error_message: Optional[str] = None) -> Meeting:
        """转换到新状态"""
        if not self.can_transition_to(new_status):
            raise ValueError(f"无效的状态转换: {self.meeting.status} -> {new_status}")

        self.meeting.status = new_status
        self.meeting.updated_at = datetime.now()

        if error_message:
            self.meeting.error_message = error_message

        return self.meeting
```

---

## 8. 测试策略

### 8.1 TDD流程

```
1. Red: 编写失败的测试
2. Green: 编写最小代码使测试通过
3. Refactor: 重构代码，保持测试通过
```

### 8.2 测试目录结构

```
tests/
├── conftest.py                    # pytest配置和fixtures
├── unit/                          # 单元测试
│   ├── domain/                    # 领域模型测试
│   │   ├── test_meeting.py
│   │   ├── test_transcription.py
│   │   └── test_summary.py
│   ├── services/                  # 服务测试
│   │   ├── test_audio_processor.py
│   │   ├── test_llm_transcriber.py
│   │   └── test_audio_cleaner.py
│   └── utils/                     # 工具测试
│       └── test_error.py
├── integration/                   # 集成测试
│   ├── test_api_endpoints.py      # API集成测试
│   ├── test_llm_integration.py    # LLM集成测试
│   └── test_database.py           # 数据库集成测试
└── fixtures/                      # 测试固件
    ├── audio/                     # 测试音频文件
    │   └── test_audio.mp3
    └── db/                        # 测试数据库
        └── test.db
```

### 8.3 参数化测试示例

```python
# tests/unit/services/test_audio_processor.py
import pytest
from internal.services.audio_processor import AudioProcessor

@pytest.mark.parametrize("filename,file_size,should_pass", [
    ("test.mp3", 100 * 1024 * 1024, True),        # 100MB - 通过
    ("test.wav", 300 * 1024 * 1024, True),        # 300MB - 边界通过
    ("test.mp3", 301 * 1024 * 1024, False),       # 301MB - 拒绝
    ("test.txt", 10 * 1024 * 1024, False),        # 不支持格式
])
async def test_validate_audio_file(filename, file_size, should_pass):
    """测试音频文件验证"""
    processor = AudioProcessor()

    if should_pass:
        processor.validate_file(filename, file_size)
    else:
        with pytest.raises(ValueError):
            processor.validate_file(filename, file_size)
```

---

## 9. 实现步骤

### Phase 1: P0核心功能（Week 1-2）

| 任务 | AC | 优先级 |
|------|----|-------|
| 1.1 项目脚手架搭建 | - | P0 |
| 1.2 数据库Schema实现 | - | P0 |
| 1.3 音频上传与验证 | AC1 | P0 |
| 1.4 LLM转写服务集成 | AC2, AC3 | P0 |
| 1.5 基础纪要生成 | AC5 | P0 |
| 1.6 历史记录列表 | - | P0 |

**测试目标**：
- 所有P0相关的AC测试通过
- 集成测试覆盖核心流程

### Phase 2: P1增强功能（Week 3-4）

| 任务 | AC | 优先级 |
|------|----|-------|
| 2.1 说话人自定义命名 | AC4 | P1 |
| 2.2 提示词模板系统 | - | P1 |
| 2.3 多版本纪要管理 | AC5 | P1 |
| 2.4 导出功能（MD/TXT） | AC8 | P1 |
| 2.5 会议标题自动生成 | AC11, AC12 | P1 |
| 2.6 手动清理音频 | AC13 | P1 |

**测试目标**：
- 所有P1相关的AC测试通过
- E2E测试覆盖完整用户流程

### Phase 3: P2完善功能（Week 5）

| 任务 | AC | 优先级 |
|------|----|-------|
| 3.1 API配置Web界面 | AC7 | P2 |
| 3.2 进度百分比显示 | AC2 | P2 |
| 3.3 音频自动清理 | AC6 | P2 |

**测试目标**：
- 所有AC测试通过
| 性能测试 |  |  |

---

## 10. 数据库迁移策略

### 推荐方案：**手写SQL脚本 + 版本控制**

#### 理由
1. **符合简单性原则**：项目处于早期阶段，Schema变化频繁，Alembic引入不必要的复杂度
2. **SQLite友好**：手写SQL对SQLite支持更直接，无需ORM迁移层
3. **透明可控**：每个迁移都是纯SQL，易于审查和调试
4. **YAGNI**：当前单用户场景，无需复杂的迁移回滚和分支管理

#### 实施方式

**迁移脚本目录结构**：
```
migrations/
├── 001_init_schema.sql           # 初始化Schema
├── 002_add_summary_table.sql     # 添加纪要表
├── 003_add_audio_deleted_at.sql  # 添加音频删除时间字段
└── _migration_log.sql            # 迁移记录表（自动创建）
```

**迁移脚本示例**：
```sql
-- migrations/001_init_schema.sql
BEGIN TRANSACTION;

-- meetings表
CREATE TABLE IF NOT EXISTS meetings (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    audio_path TEXT,
    status TEXT NOT NULL,
    progress INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    audio_deleted_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_meetings_status ON meetings(status);
CREATE INDEX IF NOT EXISTS idx_meetings_created_at ON meetings(created_at DESC);

COMMIT;
```

**版本表**（自动维护）：
```sql
CREATE TABLE IF NOT EXISTS _migration_log (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**迁移工具**（`scripts/migrate.py`）：
```python
import sqlite3
import re
from pathlib import Path

def apply_migrations(db_path: str, migrations_dir: str = "migrations"):
    """应用未应用的迁移"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 创建迁移记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS _migration_log (
            version INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 获取已应用的迁移
    applied = {row[0] for row in cursor.execute("SELECT version FROM _migration_log")}

    # 应用新迁移
    for migration_file in sorted(Path(migrations_dir).glob("*.sql")):
        version = int(migration_file.name.split("_")[0])
        if version not in applied:
            sql = migration_file.read_text()
            cursor.executescript(sql)
            cursor.execute(
                "INSERT INTO _migration_log (version, name) VALUES (?, ?)",
                (version, migration_file.name)
            )
            print(f"Applied migration: {migration_file.name}")

    conn.commit()
    conn.close()
```

#### 未来演进
当项目满足以下条件时，再考虑引入Alembic：
- Schema结构稳定，变化频率降低
- 需要支持多用户环境
- 需要复杂的迁移回滚和分支管理
- 团队规模扩大，需要更规范的迁移工作流

---

## 11. Makefile规范

```makefile
# Makefile
.PHONY: help test web clean install

help:                   ## 显示帮助信息
	@echo "可用命令:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:                ## 安装依赖
	pip install -e .
	pip install pytest pytest-asyncio pytest-cov

test:                   ## 运行所有测试
	pytest tests/ -v

test-unit:              ## 运行单元测试
	pytest tests/unit/ -v

test-integration:       ## 运行集成测试
	pytest tests/integration/ -v

test-cov:               ## 运行测试并生成覆盖率报告
	pytest tests/ --cov=internal --cov-report=html

web:                    ## 启动Web服务
	python main.py

clean:                  ## 清理临时文件
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	rm -rf .pytest_cache htmlcov/

lint:                   ## 代码检查
	pylint internal/
```

---

## 12. 安全考虑

| 风险 | 缓解措施 |
|------|----------|
| API密钥泄露 | config.json加入.gitignore，提供config.example.json |
| 文件上传攻击 | 严格验证文件类型和大小，隔离音频文件存储 |
| SQL注入 | 使用参数化查询，ORM（如SQLAlchemy） |
| XSS攻击 | 前端输出转义，CSP策略 |
| 路径遍历 | 严格限制文件路径在data/目录内 |

---

## 13. 性能指标

| 指标 | 目标值 | 测量方法 |
|------|--------|----------|
| 音频上传延迟 | < 2s (100MB) | API响应时间 |
| 转写处理速度 | ~1min/10min音频 | 端到端时间 |
| 纪要生成速度 | < 30s | API响应时间 |
| 数据库查询 | < 100ms | EXPLAIN QUERY PLAN |
| 内存占用 | < 500MB (空闲) | memory_profiler |

---

## 14. 技术债务跟踪

| 项目 | 优先级 | 计划处理时间 |
|------|--------|--------------|
| LLM服务抽象层完善 | P1 | Phase 2 |
| 错误处理统一化 | P0 | Phase 1 |
| 测试覆盖率提升到80% | P1 | Phase 2 |
| 前端交互优化 | P2 | Phase 3 |

---

**下一步行动**：
1. ~~LLM服务选型确认~~ ✅ 已确认：默认豆包，支持千问、GLM、Claude、OpenAI
2. 搭建项目脚手架（目录结构、配置文件、Makefile）
3. 实现AC1的失败测试（音频上传300MB限制）
4. 设置数据库迁移脚本（migrations/001_init_schema.sql）
