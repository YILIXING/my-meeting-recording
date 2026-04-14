"""Export utilities for meeting summaries."""

from internal.domain.summary import Summary


def export_as_markdown(summary: Summary) -> str:
    """
    Export summary as Markdown format.

    Args:
        summary: Summary entity

    Returns:
        str: Markdown formatted content
    """
    # Parse the summary content and format as markdown
    # The summary.content is already in markdown format from LLM
    return summary.content


def export_as_txt(summary: Summary) -> str:
    """
    Export summary as numbered text format.

    Args:
        summary: Summary entity

    Returns:
        str: Numbered text format content
    """
    content = summary.content

    # Convert markdown headers to numbered format
    lines = content.split('\n')
    result = []
    section_numbers = [0]  # Track numbering depth

    for line in lines:
        stripped = line.strip()

        # Count header level
        if stripped.startswith('#'):
            level = 0
            while level < len(stripped) and stripped[level] == '#':
                level += 1

            title = stripped[level:].strip()

            # Update section numbers
            if level <= len(section_numbers):
                section_numbers[level - 1] += 1
                # Reset deeper levels
                for i in range(level, len(section_numbers)):
                    section_numbers[i] = 0
            else:
                # Add new level
                while len(section_numbers) < level:
                    section_numbers.append(0)
                section_numbers[level - 1] += 1

            # Format number
            if level == 1:
                number = str(section_numbers[0])
            elif level == 2:
                number = f"{section_numbers[0]}.{section_numbers[1]}"
            elif level == 3:
                number = f"{section_numbers[0]}.{section_numbers[1]}.{section_numbers[2]}"
            else:
                number = ".".join(str(n) for n in section_numbers[:level])

            result.append(f"{number} {title}")
        elif stripped.startswith('-'):
            # Convert bullet points
            result.append(f"- {stripped[1:].strip()}")
        else:
            result.append(line)

    return '\n'.join(result)
