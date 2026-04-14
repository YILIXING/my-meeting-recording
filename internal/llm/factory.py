"""LLM service factory."""

import json
from pathlib import Path
from typing import Optional
from internal.llm.base import LLMService
from internal.llm.universal import UniversalLLM
from internal.utils.error import LLMConfigError


def create_llm_service(
    config_path: Optional[str] = None,
    service_name: Optional[str] = None
) -> LLMService:
    """
    Create LLM service instance based on configuration.

    Args:
        config_path: Path to config.json file (default: "config.json")
        service_name: Specific service to use (default: use default from config)

    Returns:
        LLMService: Configured LLM service instance

    Raises:
        LLMConfigError: If configuration is invalid or service not found
    """
    if config_path is None:
        config_path = "config.json"

    # Load configuration
    config_file = Path(config_path)
    if not config_file.exists():
        raise LLMConfigError(f"Configuration file not found: {config_path}")

    with open(config_file, "r") as f:
        config = json.load(f)

    llm_config = config.get("llm", {})
    if service_name is None:
        service_name = llm_config.get("default_service", "doubao")

    # Get service configuration
    services = llm_config.get("services", {})
    if service_name not in services:
        available = ", ".join(services.keys())
        raise LLMConfigError(
            f"LLM service '{service_name}' not found. Available: {available}"
        )

    service_config = services[service_name]

    # Extract common parameters
    protocol = service_config.get("protocol", "openai")
    api_key = service_config.get("api_key", "")
    model = service_config.get("model", "")
    endpoint = service_config.get("endpoint")
    extra = service_config.get("extra", {})

    # Validate required fields
    if not api_key:
        raise LLMConfigError(f"API key is required for service '{service_name}'")

    if not model:
        raise LLMConfigError(f"Model ID is required for service '{service_name}'")

    # Create universal LLM client
    return UniversalLLM(
        api_key=api_key,
        protocol=protocol,
        model=model,
        endpoint=endpoint,
        extra=extra
    )


def validate_llm_config(config_path: Optional[str] = None) -> bool:
    """
    Validate LLM configuration.

    Args:
        config_path: Path to config.json file

    Returns:
        bool: True if configuration is valid

    Raises:
        LLMConfigError: If configuration is invalid
    """
    try:
        service = create_llm_service(config_path)
        # Import asyncio to run async validation
        import asyncio

        async def _validate():
            return await service.validate_config()

        return asyncio.run(_validate())
    except Exception as err:
        raise LLMConfigError(f"LLM configuration validation failed: {err}") from err

