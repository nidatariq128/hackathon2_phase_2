# Task: T-002 - Implement Configuration Management
# Spec: specs/task-crud/spec.md
"""
Tests for configuration management.
"""

import pytest
from pydantic import ValidationError


class TestSettings:
    """Tests for Settings class."""

    def test_settings_loads_from_env(self, monkeypatch):
        """Test that settings loads from environment variables."""
        # Clear the lru_cache to get fresh settings
        from app.config import get_settings
        get_settings.cache_clear()

        # Set required environment variables
        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/testdb")
        monkeypatch.setenv("BETTER_AUTH_SECRET", "a" * 32)  # 32 character secret

        settings = get_settings()

        assert settings.DATABASE_URL == "postgresql://user:pass@localhost/testdb"
        assert settings.BETTER_AUTH_SECRET == "a" * 32
        assert settings.JWT_ALGORITHM == "HS256"
        assert settings.DEBUG is False

        # Clean up
        get_settings.cache_clear()

    def test_missing_database_url_raises_error(self, monkeypatch):
        """Test that missing DATABASE_URL raises validation error."""
        from app.config import get_settings, Settings
        get_settings.cache_clear()

        # Remove DATABASE_URL if exists
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.setenv("BETTER_AUTH_SECRET", "a" * 32)

        with pytest.raises(ValidationError):
            Settings()

        get_settings.cache_clear()

    def test_missing_auth_secret_raises_error(self, monkeypatch):
        """Test that missing BETTER_AUTH_SECRET raises validation error."""
        from app.config import get_settings, Settings
        get_settings.cache_clear()

        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/testdb")
        monkeypatch.delenv("BETTER_AUTH_SECRET", raising=False)

        with pytest.raises(ValidationError):
            Settings()

        get_settings.cache_clear()

    def test_short_auth_secret_raises_error(self, monkeypatch):
        """Test that BETTER_AUTH_SECRET shorter than 32 chars raises error."""
        from app.config import get_settings, Settings
        get_settings.cache_clear()

        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/testdb")
        monkeypatch.setenv("BETTER_AUTH_SECRET", "short")  # Less than 32 chars

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        assert "32 characters" in str(exc_info.value)

        get_settings.cache_clear()

    def test_invalid_database_url_raises_error(self, monkeypatch):
        """Test that non-PostgreSQL DATABASE_URL raises error."""
        from app.config import get_settings, Settings
        get_settings.cache_clear()

        monkeypatch.setenv("DATABASE_URL", "mysql://user:pass@localhost/testdb")
        monkeypatch.setenv("BETTER_AUTH_SECRET", "a" * 32)

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        assert "PostgreSQL" in str(exc_info.value)

        get_settings.cache_clear()

    def test_async_database_url_conversion(self, monkeypatch):
        """Test that async_database_url converts URL correctly."""
        from app.config import get_settings, Settings
        get_settings.cache_clear()

        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/testdb")
        monkeypatch.setenv("BETTER_AUTH_SECRET", "a" * 32)

        settings = Settings()

        assert settings.async_database_url == "postgresql+asyncpg://user:pass@localhost/testdb"

        get_settings.cache_clear()

    def test_async_database_url_postgres_prefix(self, monkeypatch):
        """Test async_database_url with postgres:// prefix."""
        from app.config import get_settings, Settings
        get_settings.cache_clear()

        monkeypatch.setenv("DATABASE_URL", "postgres://user:pass@localhost/testdb")
        monkeypatch.setenv("BETTER_AUTH_SECRET", "a" * 32)

        settings = Settings()

        assert settings.async_database_url == "postgresql+asyncpg://user:pass@localhost/testdb"

        get_settings.cache_clear()

    def test_cors_origins_from_json_string(self, monkeypatch):
        """Test parsing CORS_ORIGINS from JSON string."""
        from app.config import get_settings, Settings
        get_settings.cache_clear()

        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/testdb")
        monkeypatch.setenv("BETTER_AUTH_SECRET", "a" * 32)
        monkeypatch.setenv("CORS_ORIGINS", '["http://localhost:3000", "https://example.com"]')

        settings = Settings()

        assert settings.CORS_ORIGINS == ["http://localhost:3000", "https://example.com"]

        get_settings.cache_clear()

    def test_cors_origins_from_comma_separated(self, monkeypatch):
        """Test parsing CORS_ORIGINS from comma-separated string."""
        from app.config import get_settings, Settings
        get_settings.cache_clear()

        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/testdb")
        monkeypatch.setenv("BETTER_AUTH_SECRET", "a" * 32)
        monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000, https://example.com")

        settings = Settings()

        assert settings.CORS_ORIGINS == ["http://localhost:3000", "https://example.com"]

        get_settings.cache_clear()

    def test_default_cors_origins(self, monkeypatch):
        """Test default CORS_ORIGINS value."""
        from app.config import get_settings, Settings
        get_settings.cache_clear()

        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/testdb")
        monkeypatch.setenv("BETTER_AUTH_SECRET", "a" * 32)
        monkeypatch.delenv("CORS_ORIGINS", raising=False)

        settings = Settings()

        assert settings.CORS_ORIGINS == ["http://localhost:3000"]

        get_settings.cache_clear()

    def test_debug_mode_default_false(self, monkeypatch):
        """Test that DEBUG defaults to False."""
        from app.config import get_settings, Settings
        get_settings.cache_clear()

        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/testdb")
        monkeypatch.setenv("BETTER_AUTH_SECRET", "a" * 32)
        monkeypatch.delenv("DEBUG", raising=False)

        settings = Settings()

        assert settings.DEBUG is False

        get_settings.cache_clear()

    def test_debug_mode_enabled(self, monkeypatch):
        """Test that DEBUG can be enabled."""
        from app.config import get_settings, Settings
        get_settings.cache_clear()

        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/testdb")
        monkeypatch.setenv("BETTER_AUTH_SECRET", "a" * 32)
        monkeypatch.setenv("DEBUG", "true")

        settings = Settings()

        assert settings.DEBUG is True

        get_settings.cache_clear()

    def test_get_settings_cached(self, monkeypatch):
        """Test that get_settings returns cached instance."""
        from app.config import get_settings
        get_settings.cache_clear()

        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/testdb")
        monkeypatch.setenv("BETTER_AUTH_SECRET", "a" * 32)

        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2  # Same instance

        get_settings.cache_clear()
