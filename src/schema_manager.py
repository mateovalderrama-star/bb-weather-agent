"""Schema manager for BigQuery weather data table."""

import logging
from typing import Dict, List, Any
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
        Generate a human-readable schema description for the LLM.
        
        Returns:
            Formatted schema description
        """
        schema = self.get_schema()
        table_info = self.get_table_info()
        
        description = f"""
# Weather Data Table Schema

**Table**: `{table_info['full_table_id']}`
**Description**: {table_info.get('description', 'Current weather data from various locations')}
**Total Rows**: {table_info['num_rows']:,}
**Last Modified**: {table_info['modified']}

## Available Fields:

"""
        
        for field in schema:
            field_desc = f"- **{field['name']}** ({field['type']})"
            if field['description']:
                field_desc += f": {field['description']}"
            else:
                # Add common weather field descriptions
                field_desc += f": {self._get_field_description(field['name'])}"
            
            if field['mode'] == 'REPEATED':
                field_desc += " [ARRAY]"
            elif field['mode'] == 'REQUIRED':
                field_desc += " [REQUIRED]"
            
            description += field_desc + "\n"
        
        return description
    
    def _get_field_description(self, field_name: str) -> str:
        """
        Get a description for common weather fields.
        
        Args:
            field_name: Name of the field
            
        Returns:
            Field description
        """
        # Common weather field descriptions
        descriptions = {
            'location': 'Geographic location name',
            'city': 'City name',
            'province': 'Province or state',
            'country': 'Country name',
            'latitude': 'Latitude coordinate',
            'longitude': 'Longitude coordinate',
            'temperature': 'Temperature reading',
            'temp': 'Temperature reading',
            'feels_like': 'Perceived temperature',
            'humidity': 'Humidity percentage',
            'pressure': 'Atmospheric pressure',
            'wind_speed': 'Wind speed',
            'wind_direction': 'Wind direction',
            'weather_condition': 'Weather condition description',
            'condition': 'Weather condition',
            'precipitation': 'Precipitation amount',
            'visibility': 'Visibility distance',
            'timestamp': 'Data timestamp',
            'date': 'Date of observation',
            'time': 'Time of observation',
            'updated_at': 'Last update timestamp',
            'created_at': 'Record creation timestamp'
        }
        
        # Try exact match first
        if field_name.lower() in descriptions:
            return descriptions[field_name.lower()]
        
        # Try partial match
        for key, desc in descriptions.items():
            if key in field_name.lower():
                return desc
        
        return 'Data field'
    
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
2. Use appropriate WHERE clauses to filter data
3. Consider using LIMIT to restrict result size
4. Use aggregation functions (AVG, MAX, MIN, COUNT) for analytics
5. Format timestamps appropriately for time-based queries
6. Use LIKE for partial text matching on location fields

## Example Queries:

```sql
-- Get current weather for a specific location
SELECT * FROM `{full_table}` 
WHERE location = 'Toronto' 
LIMIT 10;

-- Get average temperature by location
SELECT location, AVG(temperature) as avg_temp 
FROM `{full_table}` 
GROUP BY location;

-- Get recent weather data
SELECT * FROM `{full_table}` 
WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
ORDER BY timestamp DESC;
```
""".format(full_table=Config.get_full_table_name())
        
        return context
