"""Template domain model."""

from dataclasses import dataclass


@dataclass
class Template:
    """
    Prompt template entity.

    Represents reusable prompt templates for meeting summary generation.
    """

    id: str                          # UUID
    name: str                        # Template name
    content: str                     # Prompt content
    is_default: bool = False         # Whether this is the default template
    is_preset: bool = False          # Whether this is a system preset template
