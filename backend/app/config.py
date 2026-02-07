# Task: T-002 - Implement Configuration Management
# Spec: specs/task-crud/spec.md
# Plan: specs/task-crud/plan.md
"""
Application configuration management.

Uses Pydantic Settings to load configuration from environment variables.
All settings are validated on application startup.
"""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        DATABASE_URL: Neon PostgreSQL connection string
        BETTER_AUTH_SECRET: Shared secret for JWT verification (min 32 chars)
        JWT_ALGORITHM: Algorithm for JWT signing/verification
        CORS_ORIGINS: List of allowed CORS origins
        DEBUG: Enable debug mode
        API_HOST: Host to bind the API server
        API_PORT: Port to bind the API server
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Database Configuration
    DATABASE_URL: str = Field(
        ...,
        description="Neon PostgreSQL connection string",
        examples=["postgresql://user:pass@ep-xxx.neon.tech/dbname?sslmode=require"],
    )

    # Authentication Configuration
    BETTER_AUTH_SECRET: str = Field(
        ...,
        min_length=32,
        description="Shared secret with Better Auth frontend for JWT verification",
    )
    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="JWT signing algorithm",
    )

    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000"],
        description="List of allowed CORS origins",
    )

    # Application Settings
    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode",
    )
    API_HOST: str = Field(
        default="0.0.0.0",
        description="Host to bind the API server",
    )
    API_PORT: int = Field(
        default=8000,
        description="Port to bind the API server",
    )

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate that DATABASE_URL is a valid PostgreSQL connection string."""
        if not v:
            raise ValueError("DATABASE_URL cannot be empty")
        if not any(v.startswith(prefix) for prefix in ["postgresql://", "postgres://"]):
            raise ValueError("DATABASE_URL must be a PostgreSQL connection string")
        return v

    @field_validator("BETTER_AUTH_SECRET")
    @classmethod
    def validate_auth_secret(cls, v: str) -> str:
        """Validate that BETTER_AUTH_SECRET meets minimum security requirements."""
        if len(v) < 32:
            raise ValueError("BETTER_AUTH_SECRET must be at least 32 characters long")
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from string or list."""
        if isinstance(v, str):
            # Handle JSON-like string: ["http://localhost:3000"]
            if v.startswith("["):
                import json
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            # Handle comma-separated string
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @property
    def async_database_url(self) -> str:
        """
        Convert DATABASE_URL to async-compatible format.

        Converts postgres:// or postgresql:// to postgresql+asyncpg://
        for use with SQLAlchemy async engine.
        Removes asyncpg-incompatible parameters (sslmode, channel_binding).
        """
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

        # Remove asyncpg-incompatible parameters
        # sslmode and channel_binding should be handled via connect_args in engine
        if "?" in url:
            base_url, params = url.split("?", 1)
            # Filter out incompatible parameters
            param_pairs = params.split("&")
            filtered_params = [
                p for p in param_pairs
                if not p.startswith("sslmode=") and not p.startswith("channel_binding=")
            ]
            if filtered_params:
                url = f"{base_url}?{'&'.join(filtered_params)}"
            else:
                url = base_url

        return url


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.

    Uses lru_cache to ensure settings are loaded only once
    and the same instance is returned for all calls.

    Returns:
        Settings: Application settings instance

    Raises:
        ValidationError: If required environment variables are missing or invalid
    """
    return Settings()


# Convenience export for direct import
settings = get_settings()
