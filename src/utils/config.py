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
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-5")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.1"))
    
    # GCP Configuration
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS",
        ""
    )
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "wb-aaaie-wthr-ing-np-pr-aac977")
    BQ_TABLE_PROJECT_ID: str = os.getenv("BQ_TABLE_PROJECT_ID", "cio-datahub-enterprise-pr-183a")
    BIGQUERY_DATASET: str = os.getenv("BIGQUERY_DATASET", "ent_common_location")
    BIGQUERY_TABLE: str = os.getenv("BIGQUERY_TABLE", "bq_weather_current")
    
    # Proxy Configuration
    HTTP_PROXY: Optional[str] = os.getenv("HTTP_PROXY", 'http://198.161.14.25:8080')
    HTTPS_PROXY: Optional[str] = os.getenv("HTTPS_PROXY", 'http://198.161.14.25:8080')
    NO_PROXY: Optional[str] = os.getenv("NO_PROXY", 'localhost,127.0.0.1')
    
    # Agent Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    MAX_QUERY_RESULTS: int = int(os.getenv("MAX_QUERY_RESULTS", "1000"))
    
    @classmethod
    def get_bigquery_uri(cls) -> str:
        """Get the BigQuery connection URI."""
        return f"bigquery://{cls.GCP_PROJECT_ID}/{cls.BIGQUERY_DATASET}"
    
    @classmethod
    def get_full_table_name(cls) -> str:
        """Get the full BigQuery table name."""
        return f"{cls.BQ_TABLE_PROJECT_ID}.{cls.BIGQUERY_DATASET}.{cls.BIGQUERY_TABLE}"
    
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
        
        if not os.path.exists(cls.GOOGLE_APPLICATION_CREDENTIALS):
            logging.error(f"Google credentials file not found: {cls.GOOGLE_APPLICATION_CREDENTIALS}")
            return False
        
        # Set credentials environment variable
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = cls.GOOGLE_APPLICATION_CREDENTIALS
        
        return True
