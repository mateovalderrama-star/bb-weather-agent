"""Schema manager for Cloud SQL (MySQL) weather database."""

import logging
from typing import Dict, List, Any, Optional

from src.utils.cloudsql_helper import CloudSQLHelper
from src.utils.config import Config

logger = logging.getLogger(__name__)


class SchemaManager:
    """Manages Cloud SQL schema discovery and provides context for the LLM."""

    def __init__(self, cloud_sql_helper: CloudSQLHelper):
        """Initialize schema manager with a shared helper instance."""
        self.helper = cloud_sql_helper
        self._schema_cache: Optional[Dict[str, List[Dict[str, Any]]]] = None
        self._relationships_cache: Optional[List[Dict[str, str]]] = None

    def get_schema(self) -> Dict[str, List[Dict[str, Any]]]:
        """Return {table_name: [column_dicts]} for all tables."""
        if self._schema_cache is None:
            self._schema_cache = self.helper.get_all_tables_schema()
        return self._schema_cache

    def get_relationships(self) -> List[Dict[str, str]]:
        """Return list of FK relationship dicts."""
        if self._relationships_cache is None:
            self._relationships_cache = self.helper.get_relationships()
        return self._relationships_cache

    def get_schema_description(self) -> str:
        """Build a human-readable schema description from information_schema."""
        schema = self.get_schema()
        lines = ["## Available Tables\n"]
        for table, columns in schema.items():
            col_summaries = ", ".join(
                f"{c['column']} ({c['type']}{'  PK' if c['key'] == 'PRI' else ''})"
                for c in columns
            )
            lines.append(f"**{table}**: {col_summaries}\n")
        return "\n".join(lines)

    def get_table_info(self) -> str:
        """Return a multi-table summary (names and column counts)."""
        schema = self.get_schema()
        lines = ["## Table Summary\n"]
        for table, columns in schema.items():
            lines.append(f"- `{table}` — {len(columns)} columns")
        return "\n".join(lines)

    def get_sample_data_description(self, num_samples: int = 3) -> str:
        """Get sample data from all tables as a formatted string."""
        schema = self.get_schema()
        sections = ["\n## Sample Data\n"]
        for table in schema:
            try:
                df = self.helper.get_sample_data(table, limit=num_samples)
                sections.append(f"### `{table}`\n{df.to_string(index=False)}\n")
            except Exception as e:
                logger.warning(f"Could not retrieve sample data for {table}: {e}")
                sections.append(f"### `{table}`\nSample data not available.\n")
        return "\n".join(sections)

    def get_full_context(self, include_samples: bool = True) -> str:
        """Get complete schema context for the LLM."""
        context = self.get_schema_description()

        # FK relationships
        relationships = self.get_relationships()
        if relationships:
            context += "\n## Table Relationships (Foreign Keys)\n\n"
            for rel in relationships:
                context += (
                    f"- `{rel['table']}.{rel['column']}` → "
                    f"`{rel['ref_table']}.{rel['ref_column']}`\n"
                )
        else:
            context += "\n## Table Relationships\nNo foreign key relationships detected.\n"

        if include_samples:
            context += self.get_sample_data_description()

        context += """
## Query Guidelines (MySQL)

1. Use backtick-quoted table and column names when they contain special characters.
2. Always include a LIMIT clause to restrict results (max {max_results} rows).
3. For geographic distance queries: ST_Distance_Sphere(POINT(lon, lat), POINT(lon, lat)).
4. For geographic point creation: ST_GeomFromText('POINT(lon lat)').
5. Use JOINs to correlate data across tables when the question involves multiple data types.
6. Use aggregation functions (AVG, MAX, MIN, COUNT) for analytics.
7. Format timestamps with DATE_FORMAT() or DATE() for time-based grouping.
8. Only perform SELECT queries — no INSERT, UPDATE, DELETE, or DDL statements.
9. Use information_schema to discover tables or columns when unsure.

## Example Queries

```sql
-- List all available tables
SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE();

-- Sample from a table with a row limit
SELECT * FROM `weather_current` LIMIT 10;

-- Join two tables (example)
SELECT w.location_id, w.temperature, l.city_name
FROM `weather_current` w
JOIN `locations` l ON w.location_id = l.id
WHERE l.province = 'ON'
LIMIT 100;

-- Geographic distance (within 5 km of a point)
SELECT *, ST_Distance_Sphere(POINT(longitude, latitude), POINT(-79.39, 43.67)) AS dist_m
FROM `weather_current`
HAVING dist_m < 5000
ORDER BY dist_m
LIMIT 50;
```
""".format(max_results=Config.MAX_QUERY_RESULTS)

        return context
