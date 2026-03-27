"""Configuration management for the weather agent."""

import os
from typing import Optional
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class Config:
    """Configuration class for managing environment variables and settings."""

    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "claude-sonnet-4-6")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.3"))

    # GCP Configuration
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

    # Cloud SQL Configuration — env var names match GKE ConfigMap/Secret and config.js.
    # The Cloud SQL Auth Proxy sidecar handles GCP auth and exposes the instance at
    # CLOUD_SQL_HOST:CLOUD_SQL_PORT (typically localhost:3306 in GKE).
    # For local dev, run: cloud-sql-proxy <instance-connection-name> --port=3306
    CLOUD_SQL_HOST: str = (
        os.getenv("INSTANCE_HOST_NAC_NP") or
        os.getenv("INSTANCE_HOST_NAC_PR") or
        os.getenv("INSTANCE_HOST_NAC", "localhost")
    )
    CLOUD_SQL_PORT: int = int(os.getenv("DB_PORT_WD") or os.getenv("DB_PORT_NAC", "3306"))
    CLOUD_SQL_DATABASE: str = (
        os.getenv("DB_NAME_WD_NP") or
        os.getenv("DB_NAME_WD_PR") or
        os.getenv("DB_NAME_WD", "weatherdata")
    )
    CLOUD_SQL_USER: str = (
        os.getenv("DB_USER_WD_NP") or
        os.getenv("DB_USER_WD_PR") or
        os.getenv("DB_USER_WD", "")
    )
    CLOUD_SQL_PASSWORD: str = (
        os.getenv("DB_PASS_WD_NP") or
        os.getenv("DB_PASS_WD_PR") or
        os.getenv("DB_PASS_WD", "")
    )

    # Proxy Configuration
    # Defaults to empty — set in .env for local dev behind Telus corporate proxy.
    # In GKE, leave unset so GCP API calls (Cloud SQL connector, metadata server) are not proxied.
    HTTP_PROXY: Optional[str] = os.getenv("HTTP_PROXY", "")
    HTTPS_PROXY: Optional[str] = os.getenv("HTTPS_PROXY", "")
    NO_PROXY: Optional[str] = os.getenv("NO_PROXY", "127.0.0.1,::1,localhost,.svc.cluster.local,.telus.com,metadata.google.internal,169.254.169.254")

    # Agent Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    MAX_QUERY_RESULTS: int = int(os.getenv("MAX_QUERY_RESULTS", "1000"))

    @classmethod
    def setup_proxy(cls) -> None:
        """Set up proxy configuration if provided."""
        if cls.HTTP_PROXY:
            os.environ['HTTP_PROXY'] = cls.HTTP_PROXY
        if cls.HTTPS_PROXY:
            os.environ['HTTPS_PROXY'] = cls.HTTPS_PROXY
        if cls.NO_PROXY:
            os.environ['NO_PROXY'] = cls.NO_PROXY

    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        if not cls.OPENAI_API_KEY:
            logging.error("OPENAI_API_KEY is not set")
            return False

        # Credentials file is only needed for local dev.
        # In GKE, Workload Identity provides ADC automatically — leave this unset.
        if cls.GOOGLE_APPLICATION_CREDENTIALS:
            if not os.path.exists(cls.GOOGLE_APPLICATION_CREDENTIALS):
                logging.error(f"Google credentials file not found: {cls.GOOGLE_APPLICATION_CREDENTIALS}")
                return False
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = cls.GOOGLE_APPLICATION_CREDENTIALS
        else:
            logging.info("GOOGLE_APPLICATION_CREDENTIALS not set — using Workload Identity / ADC")

        if not cls.CLOUD_SQL_USER:
            logging.error("DB_USER_WD (or DB_USER_WD_NP/PR) is not set")
            return False

        if not cls.CLOUD_SQL_DATABASE:
            logging.error("DB_NAME_WD (or DB_NAME_WD_NP/PR) is not set")
            return False

        return True
