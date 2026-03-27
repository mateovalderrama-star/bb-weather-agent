"""Cloud SQL helper utilities for the weather agent."""

import logging
import re
from typing import Dict, List, Any
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, text, URL

from src.utils.config import Config

logger = logging.getLogger(__name__)


class CloudSQLHelper:
    """Helper class for Cloud SQL (MySQL) operations.

    Connects via plain TCP to the Cloud SQL Auth Proxy (localhost:3306 in GKE,
    or a locally-running proxy for development).

    Local dev setup:
        cloud-sql-proxy <project>:<region>:<instance> --port=3306
    Then set DB_USER_WD, DB_PASS_WD, DB_NAME_WD in .env.
    """

    def __init__(self):
        self._engine = None

    def get_engine(self) -> sqlalchemy.Engine:
        """Lazy-init SQLAlchemy engine via TCP connection to the Cloud SQL proxy."""
        if self._engine is None:
            url = URL.create(
                "mysql+pymysql",
                username=Config.CLOUD_SQL_USER,
                password=Config.CLOUD_SQL_PASSWORD,
                host=Config.CLOUD_SQL_HOST,
                port=Config.CLOUD_SQL_PORT,
                database=Config.CLOUD_SQL_DATABASE,
            )
            self._engine = create_engine(url, pool_pre_ping=True)
            logger.info(
                f"Initialized Cloud SQL engine for: "
                f"{Config.CLOUD_SQL_HOST}:{Config.CLOUD_SQL_PORT}/{Config.CLOUD_SQL_DATABASE}"
            )
        return self._engine

    def execute_query(self, sql: str, limit: int = None) -> pd.DataFrame:
        """Execute SQL and enforce MAX_QUERY_RESULTS row limit."""
        effective_limit = limit or Config.MAX_QUERY_RESULTS

        stripped = sql.rstrip().rstrip(";")
        if not re.search(r'\bLIMIT\b', stripped, re.IGNORECASE):
            stripped = f"{stripped} LIMIT {effective_limit}"

        logger.info(f"Executing query: {stripped[:200]}...")
        df = pd.read_sql(stripped, self.get_engine())
        logger.info(f"Query returned {len(df)} rows")
        return df

    def get_all_tables_schema(self) -> Dict[str, List[Dict[str, Any]]]:
        """Query information_schema to discover all tables and their columns."""
        sql = text("""
            SELECT
                TABLE_NAME,
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                COLUMN_KEY,
                COLUMN_DEFAULT,
                EXTRA
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = :db
            ORDER BY TABLE_NAME, ORDINAL_POSITION
        """)
        with self.get_engine().connect() as conn:
            rows = conn.execute(sql, {"db": Config.CLOUD_SQL_DATABASE}).fetchall()

        tables: Dict[str, List[Dict[str, Any]]] = {}
        for row in rows:
            tname = row[0]
            tables.setdefault(tname, []).append({
                "column": row[1],
                "type": row[2],
                "nullable": row[3],
                "key": row[4],
                "default": row[5],
                "extra": row[6],
            })

        logger.info(f"Discovered {len(tables)} tables in {Config.CLOUD_SQL_DATABASE}")
        return tables

    def get_relationships(self) -> List[Dict[str, str]]:
        """Query information_schema.KEY_COLUMN_USAGE for FK relationships."""
        sql = text("""
            SELECT
                TABLE_NAME,
                COLUMN_NAME,
                REFERENCED_TABLE_NAME,
                REFERENCED_COLUMN_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = :db
              AND REFERENCED_TABLE_NAME IS NOT NULL
        """)
        with self.get_engine().connect() as conn:
            rows = conn.execute(sql, {"db": Config.CLOUD_SQL_DATABASE}).fetchall()

        return [
            {
                "table": row[0],
                "column": row[1],
                "ref_table": row[2],
                "ref_column": row[3],
            }
            for row in rows
        ]

    def get_sample_data(self, table_name: str, limit: int = 3) -> pd.DataFrame:
        """Get sample rows from a table."""
        return pd.read_sql(
            f"SELECT * FROM `{table_name}` LIMIT {limit}",
            self.get_engine(),
        )

    def close(self) -> None:
        """Dispose the connection pool."""
        if self._engine:
            self._engine.dispose()
            self._engine = None
