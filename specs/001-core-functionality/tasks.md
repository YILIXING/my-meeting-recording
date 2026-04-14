# Tasks 001: 任务列表

**Version:** 1.0
**Status:** Active
**Created:** 2026-04-14
**Based on:** Plan 001 v1.1, Spec 001 v1.1
**Constitution:** 测试先行铁律 - 所有实现任务前必须先有测试

---

## 任务说明

- **[P]** 标记表示可并行执行的任务（无依赖关系）
- **[TDD]** 标记表示测试先行任务
- **依赖关系**: 任务编号表示执行顺序，如 1.1.1 → 1.1.2 → 1.1.3
- **原子化**: 每个任务只涉及一个主要文件的创建或修改

---

# Phase 1: P0核心功能（Week 1-2）

## 1.1 项目脚手架搭建

### 1.1.1 [P] 创建项目目录结构
**文件**: 创建目录结构
```bash
internal/{domain,repositories,services,llm,api,utils}
tests/{unit,integration,fixtures/{audio,db}}
static/{css,js}
migrations
scripts
data/audio
```
**依赖**: 无
**验证**: 目录结构存在

### 1.1.2 [P] 创建 `pyproject.toml`
**文件**: `pyproject.toml`
**内容**: 项目配置、依赖（FastAPI, pytest, aiofiles等）
**依赖**: 无
**验证**: `pip install -e .` 成功

### 1.1.3 [P] 创建 `Makefile`
**文件**: `Makefile`
**内容**: help, install, test, web, clean, lint等目标
**依赖**: 1.1.2
**验证**: `make help` 显示所有命令

### 1.1.4 [P] 创建 `.gitignore`
**文件**: `.gitignore`
**内容**: data/, config.json, __pycache__, .pytest_cache等
**依赖**: 无
**验证**: `git status` 不显示敏感文件

### 1.1.5 [P] 创建 `config.example.json`
**文件**: `config.example.json`
**内容**: LLM配置示例（豆包、千问等）
**依赖**: 无
**验证**: 配置项完整

### 1.1.6 [P] 创建 `tests/__init__.py`
**文件**: `tests/__init__.py`
**内容**: 空文件
**依赖**: 1.1.1
**验证**: pytest可识别tests目录

### 1.1.7 [P] 创建 `tests/conftest.py`
**文件**: `tests/conftest.py`
**内容**: pytest配置（asyncio, fixtures）
**依赖**: 1.1.6
**验证**: pytest可运行异步测试

---

## 1.2 数据库Schema实现

### 1.2.1 [TDD] 创建测试 `tests/integration/test_database.py`
**文件**: `tests/integration/test_database.py`
**内容**: 测试数据库初始化、表创建、索引创建
**依赖**: 1.1.7
**AC**: 无对应AC，基础设施测试

### 1.2.2 创建 `migrations/001_init_schema.sql`
**文件**: `migrations/001_init_schema.sql`
**内容**: meetings, transcript_segments, speaker_mappings, summaries, templates表
**依赖**: 1.2.1
**验证**: SQL语法正确，表结构符合plan.md

### 1.2.3 创建 `scripts/migrate.py`
**文件**: `scripts/migrate.py`
**内容**: apply_migrations()函数，应用迁移脚本
**依赖**: 1.2.2
**验证**: 可成功创建数据库和表

### 1.2.4 [TDD] 更新测试 `tests/integration/test_database.py`
**文件**: `tests/integration/test_database.py`
**内容**: 添加测试验证迁移脚本执行
**依赖**: 1.2.3
**验证**: 测试通过

### 1.2.5 [P] 创建 `internal/utils/error.py`
**文件**: `internal/utils/error.py`
**内容**: MeetingError, AudioUploadError, TranscriptionError等异常类
**依赖**: 无
**验证**: 异常类可正常导入使用

---

## 1.3 领域模型实现

### 1.3.1 [TDD] 创建测试 `tests/unit/domain/test_meeting.py`
**文件**: `tests/unit/domain/test_meeting.py`
**内容**: 测试Meeting实体创建、状态检查、业务方法
**依赖**: 1.1.7, 1.2.5
**AC**: AC2（状态流转）

### 1.3.2 创建 `internal/domain/meeting.py`
**文件**: `internal/domain/meeting.py`
**内容**: MeetingStatus枚举, Meeting dataclass
**依赖**: 1.3.1
**验证**: 通过1.3.1测试

### 1.3.3 [TDD] 创建测试 `tests/unit/domain/test_transcription.py`
**文件**: `tests/unit/domain/test_transcription.py`
**内容**: 测试TranscriptSegment, SpeakerMapping实体
**依赖**: 1.1.7
**AC**: AC3（说话人识别）

### 1.3.4 创建 `internal/domain/transcription.py`
**文件**: `internal/domain/transcription.py`
**内容**: TranscriptSegment, SpeakerMapping dataclass
**依赖**: 1.3.3
**验证**: 通过1.3.3测试

### 1.3.5 [TDD] 创建测试 `tests/unit/domain/test_summary.py`
**文件**: `tests/unit/domain/test_summary.py`
**内容**: 测试Summary实体
**依赖**: 1.1.7
**AC**: AC5（纪要版本管理）

### 1.3.6 创建 `internal/domain/summary.py`
**文件**: `internal/domain/summary.py`
**内容**: Summary dataclass
**依赖**: 1.3.5
**验证**: 通过1.3.5测试

### 1.3.7 [TDD] 创建测试 `tests/unit/domain/test_template.py`
**文件**: `tests/unit/domain/test_template.py`
**内容**: 测试Template实体
**依赖**: 1.1.7
**AC**: 无对应AC，基础设施

### 1.3.8 创建 `internal/domain/template.py`
**文件**: `internal/domain/template.py`
**内容**: Template dataclass
**依赖**: 1.3.7
**验证**: 通过1.3.7测试

### 1.3.9 [P] 创建 `internal/domain/__init__.py`
**文件**: `internal/domain/__init__.py`
**内容**: 导出所有领域模型
**依赖**: 1.3.2, 1.3.4, 1.3.6, 1.3.8
**验证**: 可from internal.domain import Meeting

---

## 1.4 Repository层实现

### 1.4.1 [TDD] 创建测试 `tests/unit/repositories/test_base.py`
**文件**: `tests/unit/repositories/test_base.py`
**内容**: 测试Repository基类
**依赖**: 1.1.7, 1.2.3
**AC**: 无对应AC，基础设施

### 1.4.2 创建 `internal/repositories/base.py`
**文件**: `internal/repositories/base.py`
**内容**: BaseRepository类（数据库连接、CRUD基础方法）
**依赖**: 1.4.1
**验证**: 通过1.4.1测试

### 1.4.3 [TDD] 创建测试 `tests/unit/repositories/test_meeting.py`
**文件**: `tests/unit/repositories/test_meeting.py`
**内容**: 测试MeetingRepository CRUD操作
**依赖**: 1.1.7, 1.3.2, 1.4.2
**AC**: AC2（状态流转）

### 1.4.4 创建 `internal/repositories/meeting.py`
**文件**: `internal/repositories/meeting.py`
**内容**: MeetingRepository类
**依赖**: 1.4.3
**验证**: 通过1.4.3测试

### 1.4.5 [TDD] 创建测试 `tests/unit/repositories/test_transcription.py`
**文件**: `tests/unit/repositories/test_transcription.py`
**内容**: 测试TranscriptionRepository CRUD操作
**依赖**: 1.1.7, 1.3.4, 1.4.2
**AC**: AC4（说话人重命名）

### 1.4.6 创建 `internal/repositories/transcription.py`
**文件**: `internal/repositories/transcription.py`
**内容**: TranscriptionRepository类
**依赖**: 1.4.5
**验证**: 通过1.4.5测试

### 1.4.7 [TDD] 创建测试 `tests/unit/repositories/test_summary.py`
**文件**: `tests/unit/repositories/test_summary.py`
**内容**: 测试SummaryRepository CRUD操作
**依赖**: 1.1.7, 1.3.6, 1.4.2
**AC**: AC5（纪要版本管理）

### 1.4.8 创建 `internal/repositories/summary.py`
**文件**: `internal/repositories/summary.py`
**内容**: SummaryRepository类
**依赖**: 1.4.7
**验证**: 通过1.4.7测试

### 1.4.9 [P] 创建 `internal/repositories/__init__.py`
**文件**: `internal/repositories/__init__.py`
**内容**: 导出所有Repository
**依赖**: 1.4.2, 1.4.4, 1.4.6, 1.4.8
**验证**: 可from internal.repositories import MeetingRepository

---

## 1.5 服务层实现 - 音频处理

### 1.5.1 [TDD] 创建测试 `tests/unit/services/test_audio_processor.py`
**文件**: `tests/unit/services/test_audio_processor.py`
**内容**: 测试音频文件验证（格式、大小）
**依赖**: 1.1.7, 1.2.5
**AC**: AC1（音频上传300MB限制）

### 1.5.2 创建 `internal/services/audio_processor.py`
**文件**: `internal/services/audio_processor.py`
**内容**: AudioProcessor类（validate_file, save_audio）
**依赖**: 1.5.1
**验证**: 通过1.5.1测试

### 1.5.3 [TDD] 创建测试 `tests/unit/services/test_state_machine.py`
**文件**: `tests/unit/services/test_state_machine.py`
**内容**: 测试状态机转换逻辑
**依赖**: 1.1.7, 1.3.2
**AC**: AC2（状态流转）, AC10（用户取消）

### 1.5.4 创建 `internal/services/state_machine.py`
**文件**: `internal/services/state_machine.py`
**内容**: MeetingStateMachine类
**依赖**: 1.5.3, 1.3.2
**验证**: 通过1.5.3测试

---

## 1.6 LLM抽象层实现

### 1.6.1 [TDD] 创建测试 `tests/unit/llm/test_base.py`
**文件**: `tests/unit/llm/test_base.py`
**内容**: 测试LLMService抽象类接口
**依赖**: 1.1.7
**AC**: AC7（API配置验证）

### 1.6.2 创建 `internal/llm/base.py`
**文件**: `internal/llm/base.py`
**内容**: LLMService抽象类（transcribe_audio, generate_summary, generate_title, validate_config）
**依赖**: 1.6.1
**验证**: 通过1.6.1测试

### 1.6.3 [TDD] 创建测试 `tests/unit/llm/test_doubao.py`
**文件**: `tests/unit/llm/test_doubao.py`
**内容**: 测试豆包LLM实现（Mock API调用）
**依赖**: 1.6.2
**AC**: AC2（转写）, AC9（中英混合）

### 1.6.4 创建 `internal/llm/doubao.py`
**文件**: `internal/llm/doubao.py`
**内容**: DoubaoLLM类（实现LLMService接口）
**依赖**: 1.6.3
**验证**: 通过1.6.3测试

### 1.6.5 [TDD] 创建测试 `tests/unit/llm/test_factory.py`
**文件**: `tests/unit/llm/test_factory.py`
**内容**: 测试LLM工厂（根据配置创建实例）
**依赖**: 1.6.2, 1.6.4
**AC**: AC7（API配置）

### 1.6.6 创建 `internal/llm/factory.py`
**文件**: `internal/llm/factory.py`
**内容**: create_llm_service()工厂函数
**依赖**: 1.6.5
**验证**: 通过1.6.5测试

### 1.6.7 [P] 创建 `internal/llm/__init__.py`
**文件**: `internal/llm/__init__.py`
**内容**: 导出LLMService, create_llm_service
**依赖**: 1.6.2, 1.6.6
**验证**: 可from internal.llm import LLMService

---

## 1.7 服务层实现 - 业务服务

### 1.7.1 [TDD] 创建测试 `tests/unit/services/test_llm_transcriber.py`
**文件**: `tests/unit/services/test_llm_transcriber.py`
**内容**: 测试转写服务（Mock LLM调用）
**依赖**: 1.1.7, 1.4.4, 1.6.6, 1.5.4
**AC**: AC2（转写状态流转）, AC3（说话人识别）

### 1.7.2 创建 `internal/services/llm_transcriber.py`
**文件**: `internal/services/llm_transcriber.py`
**内容**: LLMTranscriber类（调用LLM转写，更新状态和进度）
**依赖**: 1.7.1
**验证**: 通过1.7.1测试

### 1.7.3 [TDD] 创建测试 `tests/unit/services/test_llm_summarizer.py`
**文件**: `tests/unit/services/test_llm_summarizer.py`
**内容**: 测试纪要生成服务（Mock LLM调用）
**依赖**: 1.1.7, 1.4.8, 1.6.6
**AC**: AC5（纪要版本管理）

### 1.7.4 创建 `internal/services/llm_summarizer.py`
**文件**: `internal/services/llm_summarizer.py`
**内容**: LLMSummarizer类（调用LLM生成纪要）
**依赖**: 1.7.3
**验证**: 通过1.7.3测试

### 1.7.5 [P] 创建 `internal/services/__init__.py`
**文件**: `internal/services/__init__.py`
**内容**: 导出所有服务类
**依赖**: 1.5.2, 1.5.4, 1.7.2, 1.7.4
**验证**: 可from internal.services import AudioProcessor

---

## 1.8 API层实现

### 1.8.1 [TDD] 创建测试 `tests/unit/api/test_models.py`
**文件**: `tests/unit/api/test_models.py`
**内容**: 测试Pydantic模型验证
**依赖**: 1.1.7
**AC**: 无对应AC，基础设施

### 1.8.2 创建 `internal/api/models.py`
**文件**: `internal/api/models.py`
**内容**: MeetingResponse, SummaryCreateRequest等Pydantic模型
**依赖**: 1.8.1
**验证**: 通过1.8.1测试

### 1.8.3 [TDD] 创建测试 `tests/unit/api/test_dependencies.py`
**文件**: `tests/unit/api/test_dependencies.py`
**内容**: 测试依赖注入（get_db, get_llm等）
**依赖**: 1.1.7, 1.4.2, 1.6.6
**AC**: 无对应AC，基础设施

### 1.8.4 创建 `internal/api/dependencies.py`
**文件**: `internal/api/dependencies.py`
**内容**: FastAPI依赖注入函数
**依赖**: 1.8.3
**验证**: 通过1.8.3测试

### 1.8.5 [TDD] 创建测试 `tests/integration/test_meeting_endpoints.py`
**文件**: `tests/integration/test_meeting_endpoints.py`
**内容**: 测试会议API端点（POST /api/meetings, GET /api/meetings等）
**依赖**: 1.1.7, 1.4.4, 1.5.2, 1.7.2, 1.8.2, 1.8.4
**AC**: AC1（音频上传）, AC2（状态流转）

### 1.8.6 创建 `internal/api/routes.py`
**文件**: `internal/api/routes.py`
**内容**: FastAPI路由定义（会议管理端点）
**依赖**: 1.8.5
**验证**: 通过1.8.5测试

### 1.8.7 [P] 创建 `internal/api/__init__.py`
**文件**: `internal/api/__init__.py`
**内容**: 导出app（FastAPI实例）
**依赖**: 1.8.2, 1.8.4, 1.8.6
**验证**: 可from internal.api import app

---

## 1.9 应用入口和前端基础

### 1.9.1 创建 `main.py`
**文件**: `main.py`
**内容**: FastAPI应用初始化、CORS配置、静态文件挂载
**依赖**: 1.8.7
**验证**: `python main.py` 启动成功

### 1.9.2 [P] 创建 `static/index.html`
**文件**: `static/index.html`
**内容**: 主页HTML（音频上传入口）
**依赖**: 无
**验证**: 页面可访问

### 1.9.3 [P] 创建 `static/css/styles.css`
**文件**: `static/css/styles.css`
**内容**: 基础样式
**依赖**: 无
**验证**: 样式生效

### 1.9.4 [P] 创建 `static/js/app.js`
**文件**: `static/js/app.js`
**内容**: 前端JavaScript（音频上传、API调用）
**依赖**: 1.8.6
**验证**: 可上传音频

### 1.9.5 [TDD] 更新测试 `tests/integration/test_meeting_endpoints.py`
**文件**: `tests/integration/test_meeting_endpoints.py`
**内容**: 添加E2E测试（上传→转写→完成）
**依赖**: 1.9.1, 1.9.4
**AC**: AC2（状态流转）, AC3（说话人识别）

---

# Phase 2: P1增强功能（Week 3-4）

## 2.1 说话人自定义命名

### 2.1.1 [TDD] 创建测试 `tests/integration/test_speaker_endpoints.py`
**文件**: `tests/integration/test_speaker_endpoints.py`
**内容**: 测试说话人映射API（PUT /api/meetings/{id}/speakers）
**依赖**: 1.9.5, 1.4.6
**AC**: AC4（说话人重命名）

### 2.1.2 更新 `internal/api/routes.py`
**文件**: `internal/api/routes.py`
**内容**: 添加说话人映射端点
**依赖**: 2.1.1
**验证**: 通过2.1.1测试

### 2.1.3 更新 `static/js/app.js`
**文件**: `static/js/app.js`
**内容**: 添加说话人命名UI交互
**依赖**: 2.1.2
**验证**: UI可更新说话人名称

### 2.1.4 创建 `static/detail.html`
**文件**: `static/detail.html`
**内容**: 会议详情页（转写结果、说话人命名）
**依赖**: 2.1.3
**验证**: 详情页正常显示

---

## 2.2 提示词模板系统

### 2.2.1 [TDD] 创建测试 `tests/unit/repositories/test_template.py`
**文件**: `tests/unit/repositories/test_template.py`
**内容**: 测试TemplateRepository CRUD操作
**依赖**: 1.1.7, 1.3.8, 1.4.2
**AC**: 无对应AC，基础设施

### 2.2.2 创建 `internal/repositories/template.py`
**文件**: `internal/repositories/template.py`
**内容**: TemplateRepository类
**依赖**: 2.2.1
**验证**: 通过2.2.1测试

### 2.2.3 [TDD] 创建测试 `tests/integration/test_template_endpoints.py`
**文件**: `tests/integration/test_template_endpoints.py`
**内容**: 测试模板API（GET/POST/PUT/DELETE /api/templates）
**依赖**: 2.2.2
**AC**: 无对应AC，基础设施

### 2.2.4 更新 `internal/api/routes.py`
**文件**: `internal/api/routes.py`
**内容**: 添加模板管理端点
**依赖**: 2.2.3
**验证**: 通过2.2.3测试

### 2.2.5 更新 `static/detail.html`
**文件**: `static/detail.html`
**内容**: 添加提示词模板选择UI
**依赖**: 2.2.4
**验证**: 模板选择正常工作

---

## 2.3 多版本纪要管理

### 2.3.1 [TDD] 更新测试 `tests/integration/test_summary_endpoints.py`
**文件**: `tests/integration/test_summary_endpoints.py`
**内容**: 测试纪要API（POST/GET /api/meetings/{id}/summaries, DELETE /api/summaries/{id}）
**依赖**: 1.9.5, 1.4.8, 1.7.4
**AC**: AC5（纪要版本管理）

### 2.3.2 更新 `internal/api/routes.py`
**文件**: `internal/api/routes.py`
**内容**: 添加纪要管理端点
**依赖**: 2.3.1
**验证**: 通过2.3.1测试

### 2.3.3 更新 `static/detail.html`
**文件**: `static/detail.html`
**内容**: 添加纪要版本时间线UI
**依赖**: 2.3.2
**验证**: 版本时间线正常显示

---

## 2.4 导出功能

### 2.4.1 [TDD] 创建测试 `tests/unit/utils/test_export.py`
**文件**: `tests/unit/utils/test_export.py`
**内容**: 测试导出工具（Markdown、TXT格式）
**依赖**: 1.1.7
**AC**: AC8（导出格式）

### 2.4.2 创建 `internal/utils/export.py`
**文件**: `internal/utils/export.py`
**内容**: 导出函数（export_as_markdown, export_as_txt）
**依赖**: 2.4.1
**验证**: 通过2.4.1测试

### 2.4.3 [TDD] 更新测试 `tests/integration/test_export_endpoints.py`
**文件**: `tests/integration/test_export_endpoints.py`
**内容**: 测试导出API（GET /api/summaries/{id}/export）
**依赖**: 2.4.2
**AC**: AC8（导出格式）

### 2.4.4 更新 `internal/api/routes.py`
**文件**: `internal/api/routes.py`
**内容**: 添加导出端点
**依赖**: 2.4.3
**验证**: 通过2.4.3测试

### 2.4.5 更新 `static/detail.html`
**文件**: `static/detail.html`
**内容**: 添加导出按钮和功能
**依赖**: 2.4.4
**验证**: 导出功能正常工作

---

## 2.5 会议标题自动生成

### 2.5.1 [TDD] 创建测试 `tests/unit/services/test_title_generator.py`
**文件**: `tests/unit/services/test_title_generator.py`
**内容**: 测试标题生成服务（Mock LLM调用）
**依赖**: 1.1.7, 1.6.6
**AC**: AC11（标题自动生成）

### 2.5.2 创建 `internal/services/title_generator.py`
**文件**: `internal/services/title_generator.py`
**内容**: TitleGenerator类（调用LLM生成标题）
**依赖**: 2.5.1
**验证**: 通过2.5.1测试

### 2.5.3 [TDD] 更新测试 `tests/integration/test_meeting_endpoints.py`
**文件**: `tests/integration/test_meeting_endpoints.py`
**内容**: 添加标题自动生成测试
**依赖**: 2.5.2
**AC**: AC11（标题自动生成）, AC12（标题手动编辑）

### 2.5.4 更新 `internal/services/llm_summarizer.py`
**文件**: `internal/services/llm_summarizer.py`
**内容**: 集成TitleGenerator，纪要生成后自动更新标题
**依赖**: 2.5.2
**验证**: 通过2.5.3测试

### 2.5.5 更新 `internal/api/routes.py`
**文件**: `internal/api/routes.py`
**内容**: 添加标题编辑端点（PUT /api/meetings/{id}）
**依赖**: 2.5.4
**验证**: 通过2.5.3测试

### 2.5.6 更新 `static/detail.html`
**文件**: `static/detail.html`
**内容**: 添加标题编辑UI
**依赖**: 2.5.5
**验证**: 标题编辑正常工作

---

## 2.6 手动清理音频

### 2.6.1 [TDD] 创建测试 `tests/unit/services/test_audio_cleaner.py`
**文件**: `tests/unit/services/test_audio_cleaner.py`
**内容**: 测试音频清理服务
**依赖**: 1.1.7, 1.4.4
**AC**: AC13（手动清理音频）

### 2.6.2 创建 `internal/services/audio_cleaner.py`
**文件**: `internal/services/audio_cleaner.py`
**内容**: AudioCleaner类（删除音频文件、更新数据库）
**依赖**: 2.6.1
**验证**: 通过2.6.1测试

### 2.6.3 [TDD] 更新测试 `tests/integration/test_meeting_endpoints.py`
**文件**: `tests/integration/test_meeting_endpoints.py`
**内容**: 添加音频删除端点测试
**依赖**: 2.6.2
**AC**: AC13（手动清理音频）

### 2.6.4 更新 `internal/api/routes.py`
**文件**: `internal/api/routes.py`
**内容**: 添加音频删除端点（DELETE /api/meetings/{id}/audio）
**依赖**: 2.6.3
**验证**: 通过2.6.3测试

### 2.6.5 更新 `static/detail.html`
**文件**: `static/detail.html`
**内容**: 添加手动清理音频按钮
**依赖**: 2.6.4
**验证**: 清理功能正常工作

---

## 2.7 历史记录列表

### 2.7.1 创建 `static/history.html`
**文件**: `static/history.html`
**内容**: 历史记录列表页
**依赖**: 1.9.2
**验证**: 页面可访问

### 2.7.2 更新 `static/js/app.js`
**文件**: `static/js/app.js`
**内容**: 添加历史记录加载和显示逻辑
**依赖**: 2.7.1
**验证**: 历史记录正常显示

---

# Phase 3: P2完善功能（Week 5）

## 3.1 API配置Web界面

### 3.1.1 [TDD] 创建测试 `tests/integration/test_config_endpoints.py`
**文件**: `tests/integration/test_config_endpoints.py`
**内容**: 测试配置API（GET/PUT /api/config/llm, POST /api/config/llm/validate）
**依赖**: 1.9.5, 1.6.6
**AC**: AC7（API配置验证）

### 3.1.2 更新 `internal/api/routes.py`
**文件**: `internal/api/routes.py`
**内容**: 添加配置管理端点
**依赖**: 3.1.1
**验证**: 通过3.1.1测试

### 3.1.3 创建 `static/settings.html`
**文件**: `static/settings.html`
**内容**: API设置页（LLM配置、验证）
**依赖**: 3.1.2
**验证**: 设置页正常工作

### 3.1.4 更新 `static/js/app.js`
**文件**: `static/js/app.js`
**内容**: 添加配置管理逻辑
**依赖**: 3.1.3
**验证**: 配置保存和验证正常

---

## 3.2 进度百分比显示

### 3.2.1 更新 `internal/services/llm_transcriber.py`
**文件**: `internal/services/llm_transcriber.py`
**内容**: 增强进度回调（实时更新百分比）
**依赖**: 1.7.2
**AC**: AC2（转写状态流转）- 进度显示部分

### 3.2.2 更新 `internal/api/routes.py`
**文件**: `internal/api/routes.py`
**内容**: 添加SSE/WebSocket进度推送端点
**依赖**: 3.2.1
**AC**: AC2（转写状态流转）- 进度显示部分

### 3.2.3 更新 `static/js/app.js`
**文件**: `static/js/app.js`
**内容**: 添加进度条实时更新逻辑
**依赖**: 3.2.2
**验证**: 进度条实时更新

---

## 3.3 音频自动清理

### 3.3.1 [TDD] 创建测试 `tests/unit/services/test_audio_cleaner_auto.py`
**文件**: `tests/unit/services/test_audio_cleaner_auto.py`
**内容**: 测试自动清理服务（7天过期音频）
**依赖**: 1.1.7, 1.4.4, 2.6.2
**AC**: AC6（音频自动清理）

### 3.3.2 更新 `internal/services/audio_cleaner.py`
**文件**: `internal/services/audio_cleaner.py`
**内容**: 添加自动清理方法（cleanup_expired_audios）
**依赖**: 3.3.1
**验证**: 通过3.3.1测试

### 3.3.3 创建 `scripts/scheduler.py`
**文件**: `scripts/scheduler.py`
**内容**: 定时任务脚本（每日执行清理）
**依赖**: 3.3.2
**验证**: 可手动执行清理

### 3.3.4 更新 `main.py`
**文件**: `main.py`
**内容**: 应用启动时执行一次清理检查
**依赖**: 3.3.3
**验证**: 启动时自动清理过期音频

---

## 3.4 前端完善

### 3.4.1 [P] 更新 `static/css/styles.css`
**文件**: `static/css/styles.css`
**内容**: 完善样式，美化UI
**依赖**: 2.7.2
**验证**: UI美观度提升

### 3.4.2 [P] 更新 `static/js/app.js`
**文件**: `static/js/app.js`
**内容**: 添加错误处理、加载状态提示
**依赖**: 3.2.3
**验证**: 用户体验改善

---

# 总结

**任务总数**: 约120个原子化任务
**Phase 1任务**: 约60个（P0核心功能）
**Phase 2任务**: 约40个（P1增强功能）
**Phase 3任务**: 约20个（P2完善功能）

**关键原则**:
1. ✅ **TDD强制**: 每个实现前先写测试
2. ✅ **原子化**: 每个任务一个文件
3. ✅ **依赖清晰**: 任务编号表示执行顺序
4. ✅ **并行标记**: [P]任务可并行执行

**下一步行动**:
1. 从Phase 1.1.1开始执行
2. 确保每个测试先失败（Red）
3. 实现代码使测试通过（Green）
4. 重构保持测试通过（Refactor）
