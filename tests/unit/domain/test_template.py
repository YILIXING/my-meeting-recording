"""Tests for Template domain model."""

import pytest
from internal.domain.template import Template


def test_template_creation():
    """Test template can be created with all fields."""
    template = Template(
        id="test-id",
        name="技术讨论",
        content="请讨论技术决策、架构设计和实施计划",
        is_default=True,
        is_preset=True
    )
    assert template.id == "test-id"
    assert template.name == "技术讨论"
    assert template.content == "请讨论技术决策、架构设计和实施计划"
    assert template.is_default is True
    assert template.is_preset is True


def test_custom_template():
    """Test custom user template."""
    template = Template(
        id="custom-id",
        name="我的模板",
        content="自定义提示词内容",
        is_default=False,
        is_preset=False
    )
    assert template.is_default is False
    assert template.is_preset is False


@pytest.mark.parametrize("is_preset", [True, False])
def test_template_preset_flag(is_preset: bool):
    """Test preset template flag."""
    template = Template(
        id="test-id",
        name="Test Template",
        content="Test content",
        is_preset=is_preset
    )
    assert template.is_preset == is_preset


@pytest.mark.parametrize("is_default", [True, False])
def test_template_default_flag(is_default: bool):
    """Test default template flag."""
    template = Template(
        id="test-id",
        name="Test Template",
        content="Test content",
        is_default=is_default
    )
    assert template.is_default == is_default
