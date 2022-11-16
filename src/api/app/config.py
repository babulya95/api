"""
    Configuration fields.
    Pydantic BaseSettings interface with reading from OS environment variables.
    Variables should passed by Docker.
"""

# Logs.
import logging

# Pydantic abstract class with data types.
from pydantic import BaseSettings, PostgresDsn, RedisDsn

# Libs.
import gatey_sdk

class Settings(BaseSettings):
    """
    All settings storage.
    """

    # Database.

    # Database connection string (DSN)
    # TODO 07.31.22: Allow to expose database connection as separate fields.
    database_dsn: PostgresDsn
    # If true, will create all metadata (Tables) at start of the server.
    database_create_all: bool = True
    # Pool recycle for ORM (Database).
    database_pool_recycle: int = 3600
    # Timeout for database pool.
    database_pool_timeout: int = 10
    # Max overflow for database pool.
    database_max_overflow: int = 0
    # Pool size for database pool.
    database_pool_size: int = 20

    # Gatey.
    gatey_is_enabled: bool = False
    gatey_project_id: int | None = None
    gatey_client_secret: str | None = None  # Not preferable.
    gatey_server_secret: str | None = None

    # CORS.

    # If true, will add CORS middleware.
    cors_enabled: bool = True
    # Will allow to send Authorization header.
    cors_allow_credentials: bool = True
    # Max age for CORS.
    cors_max_age: int = 600
    # Allowed CORS stuff.
    cors_allow_origins: list[str] = ["*"]
    cors_allow_methods: list[str] = ["GET", "HEAD"]
    cors_allow_headers: list[str] = ["*"]

    # Cache.

    # Redis connection string.
    cache_dsn: RedisDsn
    # Encoding for Redis.
    cache_encoding: str = "utf-8"

    # Requests limiter.

    # TODO 07.31.22: Allow to handle requests limiter disable better, and do not connect to Redis if not required.
    requests_limiter_enabled: bool = True

    # OpenAPI.

    # If false, will disable OpenAPI.
    openapi_enabled: bool = False
    openapi_url: str = "/openapi.json"
    openapi_docs_url: str = "/docs"
    openapi_redoc_url: str = "/redoc"
    openapi_prefix: str = ""
    openapi_title: str = "Kirill Zhosul API"
    openapi_version: str = "0.0.0"
    openapi_description: str = "Kirill Zhosul API"

    # FastAPI.

    # Should be false in production.
    fastapi_debug: bool = False
    fastapi_root_path: str = ""

    # Proxy (Server content with prefix or domain (Proxy server)).

    # Will be added to all methods.
    proxy_url_prefix: str = ""

    # Single-Sign-On (SSO)
    sso_api_url: str = "https://api.florgon.space"
    sso_api_oauth_exchange: str = "oauth.accessToken"
    sso_api_client_secret: str = ""
    sso_api_client_id: int = 0
    sso_api_redirect_uri: str = ""

    # Security.
    security_access_tokens_ttl: int = 7776000
    security_tokens_issuer: str = "localhost"
    security_tokens_secret_key: str =  "RANDOM_SECRET_KEY_TO_BE_SECURE"


def _init_gatey_client(settings: Settings) -> gatey_sdk.Client:
    """
    Initializes Gatey client.
    """

    if not settings.gatey_is_enabled:
        return
    
    def _void_transport(*args, **kwargs):
        """Void transport that does nothing if gatey is not configured."""
        ...
        
    # TODO: Use server secret.
    gatey_is_configured = (
        (settings.gatey_client_secret is not None or settings.gatey_server_secret is not None)
        and settings.gatey_project_id is not None
    )
    gatey_transport = None if gatey_is_configured else _void_transport
    gatey_client = gatey_sdk.Client(
        transport=gatey_transport,
        project_id=settings.gatey_project_id,
        client_secret=settings.gatey_client_secret,
        server_secret=settings.gatey_server_secret,
        check_api_auth_on_init=False,
        handle_global_exceptions=False,
        global_handler_skip_internal_exceptions=False,
        capture_vars=False,
    )
    gatey_client.capture_message(
        level="DEBUG",
        message="[Kirill Zhosul API] Server successfully initialized Gatey client (gatey-sdk-py)",
    )
    return gatey_client


def get_settings() -> Settings:
    """
    Returns Singleton settings object with all configuration settings.
    """
    return _settings


def get_gatey_client():
    """
    Returns Gatey client singleton (cached).
    """
    return _gatey


def get_logger():
    """
    Returns logger singleton (cached).
    """
    return _logger


# Static settings object with single instance.
_settings = Settings()

# Static Gatey error logger.
_gatey = _init_gatey_client(_settings)

# Static logger.
_logger = logging.getLogger("gunicorn.error")