"""
Configuration management for the customer support agent system.

This module handles loading and validating environment variables,
providing a centralized configuration interface for the entire application.
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """
    Configuration class that manages all application settings.

    This class uses Pydantic for automatic validation and type conversion
    of environment variables. It provides a clean interface for accessing
    configuration values throughout the application.
    """

    # Google AI API Configuration
    google_api_key: str = Field(..., env="GOOGLE_API_KEY")
    agent_model: str = Field(default="gemini-pro", env="AGENT_MODEL")
    max_tokens: int = Field(default=4096, env="MAX_TOKENS")
    temperature: float = Field(default=0.7, env="TEMPERATURE")

    # WebSocket Server Configuration
    websocket_host: str = Field(default="localhost", env="WEBSOCKET_HOST")
    websocket_port: int = Field(default=8765, env="WEBSOCKET_PORT")

    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/customer_support.log", env="LOG_FILE")

    # Database Configuration (Development Database)
    database_url: str = Field(
        default="postgresql://username:password@localhost:5432/dev_orders_db",
        env="DATABASE_URL",
    )
    database_host: str = Field(default="localhost", env="DATABASE_HOST")
    database_port: int = Field(default=5432, env="DATABASE_PORT")
    database_name: str = Field(default="dev_orders_db", env="DATABASE_NAME")
    database_user: str = Field(default="username", env="DATABASE_USER")
    database_password: str = Field(default="password", env="DATABASE_PASSWORD")

    class Config:
        """Pydantic configuration for environment variable loading."""

        env_file = "config.env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def validate_config(self) -> bool:
        """
        Validates the configuration and returns True if valid.

        This method checks that all required configuration values are present
        and within acceptable ranges.

        Returns:
            bool: True if configuration is valid, False otherwise
        """
        try:
            # Validate API key
            if not self.google_api_key or len(self.google_api_key) < 10:
                raise ValueError("Invalid Google API key")

            # Validate port range
            if not (1024 <= self.websocket_port <= 65535):
                raise ValueError(f"Invalid port number: {self.websocket_port}")

            # Validate temperature range
            if not (0.0 <= self.temperature <= 1.0):
                raise ValueError(f"Invalid temperature: {self.temperature}")

            # Validate max tokens
            if self.max_tokens <= 0:
                raise ValueError(f"Invalid max_tokens: {self.max_tokens}")

            return True

        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False

    def get_websocket_url(self) -> str:
        """
        Returns the WebSocket server URL.

        Returns:
            str: The WebSocket server URL in the format ws://host:port
        """
        return f"ws://{self.websocket_host}:{self.websocket_port}"

    def get_http_url(self) -> str:
        """
        Returns the HTTP server URL.

        Returns:
            str: The HTTP server URL in the format http://host:port
        """
        return f"http://{self.websocket_host}:{self.websocket_port}"
