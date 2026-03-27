"""Test script to verify Cloud SQL configuration and connectivity."""

from src.utils.config import Config


def test_configuration():
    """Test if configuration is properly set up."""
    print("=" * 60)
    print("Testing Weather Agent Configuration (Cloud SQL)")
    print("=" * 60)

    if not Config.validate():
        print("✗ Configuration validation failed")
        print()
        print("Please check:")
        print("  1. .env file exists and is properly configured")
        print("  2. OPENAI_API_KEY is set")
        print("  3. GOOGLE_APPLICATION_CREDENTIALS points to valid JSON file")
        print("  4. CLOUD_SQL_INSTANCE_CONNECTION_NAME is set (format: project:region:instance)")
        print("  5. CLOUD_SQL_DATABASE is set")
        return False

    print("✓ Configuration is valid!")
    print()
    print("Configuration Details:")
    print(f"  ✓ GCP Project ID:           {Config.GCP_PROJECT_ID}")
    print(f"  ✓ Cloud SQL Instance:        {Config.CLOUD_SQL_INSTANCE_CONNECTION_NAME}")
    print(f"  ✓ Database:                  {Config.CLOUD_SQL_DATABASE}")
    print(f"  ✓ IAM Auth:                  {Config.CLOUD_SQL_USE_IAM_AUTH}")
    print(f"  ✓ OpenAI Model:              {Config.OPENAI_MODEL}")
    print(f"  ✓ Temperature:               {Config.TEMPERATURE}")
    print(f"  ✓ Max Results:               {Config.MAX_QUERY_RESULTS}")
    if Config.HTTP_PROXY:
        print(f"  ✓ HTTP Proxy:                {Config.HTTP_PROXY}")
    print()

    # Test Cloud SQL connectivity
    print("Testing Cloud SQL connection...")
    try:
        from src.utils.cloudsql_helper import CloudSQLHelper
        helper = CloudSQLHelper()
        engine = helper.get_engine()
        print("✓ Engine created successfully")

        # Discover tables
        print("\nDiscovering tables...")
        schema = helper.get_all_tables_schema()
        if schema:
            print(f"✓ Discovered {len(schema)} table(s):")
            for table, columns in schema.items():
                print(f"    - {table} ({len(columns)} columns)")
        else:
            print("⚠ No tables found in database. Check CLOUD_SQL_DATABASE value.")

        # FK relationships
        relationships = helper.get_relationships()
        if relationships:
            print(f"\n✓ Discovered {len(relationships)} foreign key relationship(s):")
            for rel in relationships:
                print(f"    - {rel['table']}.{rel['column']} → {rel['ref_table']}.{rel['ref_column']}")
        else:
            print("\n  (No foreign key relationships detected)")

        helper.close()
        print()
        print("✓ All configuration and connectivity checks passed!")
        return True

    except Exception as e:
        print(f"✗ Cloud SQL connection failed: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Ensure GOOGLE_APPLICATION_CREDENTIALS points to a valid service account JSON")
        print("  2. The service account needs 'Cloud SQL Client' IAM role")
        print("  3. Verify CLOUD_SQL_INSTANCE_CONNECTION_NAME format: project:region:instance")
        print("  4. If using IAM auth, the SA email must match CLOUD_SQL_USER")
        print("  5. If behind a corporate proxy, ensure proxy settings are configured")
        return False


if __name__ == "__main__":
    import sys
    success = test_configuration()
    sys.exit(0 if success else 1)
