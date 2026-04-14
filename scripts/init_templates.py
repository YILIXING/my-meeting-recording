"""Initialize preset templates."""

import sqlite3
import uuid
from pathlib import Path


def init_preset_templates(db_path: str = "data/meetings.db"):
    """Initialize preset templates in database."""
    # Ensure database directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create templates table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS templates (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            content TEXT NOT NULL,
            is_default BOOLEAN DEFAULT 0,
            is_preset BOOLEAN DEFAULT 0
        )
    """)

    # Preset templates
    preset_templates = [
        {
            "name": "客户需求讨论",
            "content": """请根据会议转写内容，整理出以下信息：
1. 客户业务描述
2. 需求背景
3. 痛点和期望
4. 项目计划（如有）""",
            "is_default": True,
            "is_preset": True
        },
        {
            "name": "技术讨论纪要",
            "content": """请根据会议转写内容，整理出：
1. 技术讨论要点
2. 技术决策和理由
3. 行动项和负责人
4. 待解决的问题""",
            "is_default": False,
            "is_preset": True
        },
        {
            "name": "通用会议纪要",
            "content": """请根据会议转写内容，整理出：
1. 会议决议
2. 行动项（Action Items）
3. 讨论要点
4. 待办事项（TODO）""",
            "is_default": False,
            "is_preset": True
        }
    ]

    # Insert preset templates
    for template in preset_templates:
        try:
            cursor.execute(
                """
                INSERT INTO templates (id, name, content, is_default, is_preset)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    template["name"],
                    template["content"],
                    int(template["is_default"]),
                    int(template["is_preset"])
                )
            )
        except sqlite3.IntegrityError:
            # Template already exists, skip
            pass

    conn.commit()
    conn.close()

    print("Preset templates initialized successfully")


if __name__ == "__main__":
    init_preset_templates()
