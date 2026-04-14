"""Template repository."""

import sqlite3
import uuid
from typing import List, Optional
from internal.repositories.base import BaseRepository
from internal.domain.template import Template


class TemplateRepository(BaseRepository):
    """Repository for Template entity."""

    def create(self, template: Template) -> None:
        """
        Create a new template.

        Args:
            template: Template entity to create
        """
        template_id = template.id or str(uuid.uuid4())

        self.execute(
            """
            INSERT INTO templates (id, name, content, is_default, is_preset)
            VALUES (?, ?, ?, ?, ?)
            """,
            (template_id, template.name, template.content,
             int(template.is_default), int(template.is_preset))
        )
        self.commit()

    def get_by_id(self, template_id: str) -> Optional[Template]:
        """
        Retrieve template by ID.

        Args:
            template_id: Template ID

        Returns:
            Template entity or None if not found
        """
        row = self.fetch_one(
            "SELECT * FROM templates WHERE id = ?",
            (template_id,)
        )

        if not row:
            return None

        return self._row_to_template(row)

    def get_by_name(self, name: str) -> Optional[Template]:
        """
        Retrieve template by name.

        Args:
            name: Template name

        Returns:
            Template entity or None if not found
        """
        row = self.fetch_one(
            "SELECT * FROM templates WHERE name = ?",
            (name,)
        )

        if not row:
            return None

        return self._row_to_template(row)

    def list_all(self) -> List[Template]:
        """
        List all templates.

        Returns:
            List of Template entities
        """
        rows = self.fetch_all("SELECT * FROM templates ORDER BY is_preset DESC, name")
        return [self._row_to_template(row) for row in rows]

    def get_default(self) -> Optional[Template]:
        """
        Get the default template.

        Returns:
            Default Template entity or None
        """
        row = self.fetch_one(
            "SELECT * FROM templates WHERE is_default = 1 LIMIT 1"
        )

        if not row:
            return None

        return self._row_to_template(row)

    def update(self, template: Template) -> None:
        """
        Update an existing template.

        Args:
            template: Template entity with updated fields
        """
        self.execute(
            """
            UPDATE templates SET
                name = ?, content = ?, is_default = ?
            WHERE id = ?
            """,
            (template.name, template.content, int(template.is_default), template.id)
        )
        self.commit()

    def delete(self, template_id: str) -> None:
        """
        Delete a template by ID.

        Args:
            template_id: Template ID to delete
        """
        self.execute("DELETE FROM templates WHERE id = ? AND is_preset = 0", (template_id,))
        self.commit()

    def _row_to_template(self, row: tuple) -> Template:
        """Convert database row to Template entity."""
        (id_, name, content, is_default, is_preset) = row

        return Template(
            id=id_,
            name=name,
            content=content,
            is_default=bool(is_default),
            is_preset=bool(is_preset)
        )
