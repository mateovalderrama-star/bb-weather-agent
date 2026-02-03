"""Schema manager for BigQuery weather data table."""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from src.utils.bigquery_helper import BigQueryHelper
from src.utils.config import Config

logger = logging.getLogger(__name__)


class SchemaManager:
    """Manages BigQuery table schema and provides context for the LLM."""
    
    def __init__(self):
        """Initialize schema manager."""
        self.bq_helper = BigQueryHelper(Config.GCP_PROJECT_ID)
        self.dataset_id = Config.BIGQUERY_DATASET
        self.table_id = Config.BIGQUERY_TABLE
        self._schema_cache = None
        self._table_info_cache = None
        self._schema_description_cache: Optional[str] = None
    
    def get_schema(self) -> List[Dict[str, Any]]:
        """
        Get the table schema.
        
        Returns:
            List of field dictionaries
        """
        if self._schema_cache is None:
            self._schema_cache = self.bq_helper.get_table_schema(
                self.dataset_id, 
                self.table_id
            )
        return self._schema_cache
    
    def get_table_info(self) -> Dict[str, Any]:
        """
        Get comprehensive table information.
        
        Returns:
            Dictionary with table details
        """
        if self._table_info_cache is None:
            self._table_info_cache = self.bq_helper.get_table_info(
                self.dataset_id,
                self.table_id
            )
        return self._table_info_cache
    
    def get_schema_description(self) -> str:
        """
        Generate a human-readable schema description for the LLM by reading from a local file
        rather than querying BigQuery.
        
        Returns:
            Formatted schema description read from weather_table_schema.txt
        """
        # Use cached content if available
        if self._schema_description_cache is not None:
            return self._schema_description_cache
        
        try:
            # weather_table_schema.txt is located one directory above this file (project root)
            schema_path = Path(__file__).resolve().parents[1] / "weather_table_schema.txt"
            content = schema_path.read_text(encoding="utf-8")
            # Cache the content for subsequent calls
            self._schema_description_cache = content
            return content
        except Exception as e:
            logger.error(f"Error reading schema description from file: {e}")
            # Provide a minimal fallback so the application can continue
            return "# Weather Data Table Schema\n\nSchema description file not available."
    
    
    def get_sample_data_description(self, num_samples: int = 3) -> str:
        """
        Get sample data as a formatted string.
        
        Args:
            num_samples: Number of sample rows to retrieve
            
        Returns:
            Formatted sample data
        """
        try:
            df = self.bq_helper.get_sample_data(
                self.dataset_id,
                self.table_id,
                limit=num_samples
            )
            
            description = f"\n## Sample Data ({num_samples} rows):\n\n"
            description += df.to_string(index=False)
            
            return description
            
        except Exception as e:
            logger.error(f"Error getting sample data: {e}")
            return "\n## Sample Data: Not available\n"
    
    def get_full_context(self, include_samples: bool = True) -> str:
        """
        Get complete schema context for the LLM.
        
        Args:
            include_samples: Whether to include sample data
            
        Returns:
            Complete schema description with optional samples
        """
        context = self.get_schema_description()
        
        if include_samples:
            context += self.get_sample_data_description()
        
        context += """

## Query Guidelines:

1. Always use the full table name in queries: `{full_table}`
2. Partitioning by expressions of type FLOAT64 is not allowed in this BigQuery table.
3. When creating a lat/long buffer in the query try and use ST_DWITHIN for better performance
    2a. Always convert rqst_lat_num and rqst_long_num from FLOAT64 to GEOGRAPHY type using ST_GEOGPOINT
4. Use appropriate WHERE clauses to filter data
5. Consider using LIMIT to restrict result size
6. Use aggregation functions (AVG, MAX, MIN, COUNT) for analytics
7. Format timestamps appropriately for time-based queries

## Example Queries:

```sql
-- Get current weather for a specific location (e.x. TORONTO)
SELECT tmprtr_amt, ST_BUFFER(ST_GEOGPOINT(-79.39, 43.67), 1000) AS buffer_polygon 
FROM `{full_table}` 
LIMIT 25;

-- Find all locations within 5km of a point
SELECT * 
FROM `{full_table}` 
WHERE ST_DWITHIN(ST_GEOGPOINT(rqst_long_num, rqst_lat_num), ST_GEOGPOINT(-79.39, 43.67), 5000);

-- Get recent weather data
SELECT * FROM `{full_table}` 
WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
ORDER BY timestamp DESC;
```
""".format(full_table=Config.get_full_table_name())
        
        return context
