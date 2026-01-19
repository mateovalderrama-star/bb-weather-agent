"""Test script to verify configuration setup."""

from src.utils.config import Config

def test_configuration():
    """Test if configuration is properly set up."""
    print("=" * 60)
    print("Testing Weather Agent Configuration")
    print("=" * 60)

    # Test validation
    if Config.validate():
        print("✓ Configuration is valid!")
        print()
        print("Configuration Details:")
        print(f"  ✓ GCP Project ID: {Config.GCP_PROJECT_ID}")
        print(f"  ✓ BQ Table Project: {Config.BQ_TABLE_PROJECT_ID}")
        print(f"  ✓ Dataset: {Config.BIGQUERY_DATASET}")
        print(f"  ✓ Table: {Config.BIGQUERY_TABLE}")
        print(f"  ✓ Full Table Name: {Config.get_full_table_name()}")
        print(f"  ✓ OpenAI Model: {Config.OPENAI_MODEL}")
        print(f"  ✓ Temperature: {Config.TEMPERATURE}")
        print(f"  ✓ Max Results: {Config.MAX_QUERY_RESULTS}")
        print()

        # Check optional settings
        if Config.HTTP_PROXY:
            print(f"  ✓ HTTP Proxy: {Config.HTTP_PROXY}")
        if Config.HTTPS_PROXY:
            print(f"  ✓ HTTPS Proxy: {Config.HTTPS_PROXY}")

        print()
        print("✓ All configuration checks passed!")
        return True
    else:
        print("✗ Configuration validation failed")
        print()
        print("Please check:")
        print("  1. .env file exists and is properly configured")
        print("  2. OPENAI_API_KEY is set")
        print("  3. GOOGLE_APPLICATION_CREDENTIALS points to valid JSON file")
        print("  4. GCP credentials file exists at the specified path")
        return False

if __name__ == "__main__":
    import sys
    success = test_configuration()
    sys.exit(0 if success else 1)
