"""Config management utilities."""

import json
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Manager for application configuration."""

    def __init__(self, config_path: str = "config.json"):
        """
        Initialize config manager.

        Args:
            config_path: Path to config file
        """
        self.config_path = Path(config_path)

    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file.

        Returns:
            Dict containing configuration

        Raises:
            FileNotFoundError: If config file doesn't exist
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, "r") as f:
            return json.load(f)

    def save(self, config: Dict[str, Any]) -> None:
        """
        Save configuration to file.

        Args:
            config: Configuration dictionary
        """
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def update_llm_service(
        self,
        service_name: str,
        api_key: Optional[str] = None,
        app_id: Optional[str] = None,
        model: Optional[str] = None
    ) -> None:
        """
        Update LLM service configuration.

        Args:
            service_name: Name of the service (e.g., "doubao")
            api_key: API key to set
            app_id: App ID for the service (if applicable)
            model: Model name
        """
        config = self.load()

        if "llm" not in config:
            config["llm"] = {"services": {}}

        if service_name not in config["llm"]["services"]:
            config["llm"]["services"][service_name] = {}

        if api_key is not None:
            config["llm"]["services"][service_name]["api_key"] = api_key

        if app_id is not None:
            config["llm"]["services"][service_name]["app_id"] = app_id

        if model is not None:
            config["llm"]["services"][service_name]["model"] = model

        self.save(config)

    def set_default_service(self, service_name: str) -> None:
        """
        Set default LLM service.

        Args:
            service_name: Name of the service to set as default
        """
        config = self.load()

        if "llm" not in config:
            config["llm"] = {}

        config["llm"]["default_service"] = service_name

        self.save(config)

    def get_service_config(self, service_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific service.

        Args:
            service_name: Name of the service

        Returns:
            Dict containing service configuration
        """
        config = self.load()
        return config.get("llm", {}).get("services", {}).get(service_name, {})

    def is_service_configured(self, service_name: str) -> bool:
        """
        Check if a service is properly configured.

        Args:
            service_name: Name of the service

        Returns:
            bool: True if service has required configuration
        """
        service_config = self.get_service_config(service_name)

        # Check if API key is set and not the placeholder
        api_key = service_config.get("api_key", "")
        return bool(api_key and not api_key.startswith("your_"))
