"""BigQuery helper utilities for the weather agent."""

import logging
from typing import Dict, List, Optional, Any
import google.oauth2.credentials
from google.cloud import bigquery
from google.api_core import exceptions
import pandas as pd
from langchain.tools import tool
from src.utils.config import Config

logger = logging.getLogger(__name__)


class BigQueryHelper:
    """Helper class for BigQuery operations."""
    
    def __init__(self, project_id: str):
        """
        Initialize BigQuery helper.
        
        Args:
            project_id: GCP project ID
        """
        self.project_id = project_id
        self.table_project_id = Config.BQ_TABLE_PROJECT_ID
        self.client = bigquery.Client(project=project_id)
        logging.info(f"Initialized BigQuery Client for project: {project_id}")
    
    def get_table_schema(self, dataset_id: str, table_id: str) -> List[Dict[str, Any]]:
        """
        Get the schema of a BigQuery table.
        
        Args:
            dataset_id: BigQuery dataset ID
            table_id: BigQuery table ID
            
        Returns:
            List of field dictionaries with name, type, mode, and description
        """
        try:
            table_ref = f"{self.table_project_id}.{dataset_id}.{table_id}"
            table = self.client.get_table(table_ref)
            
            schema_info = []
            for field in table.schema:
                schema_info.append({
                    'name': field.name,
                    'type': field.field_type,
                    'mode': field.mode,
                    'description': field.description or ''
                })
            
            logger.info(f"Retrieved schema for {table_ref}: {len(schema_info)} fields")
            return schema_info
            
        except exceptions.NotFound:
            logger.error(f"Table {dataset_id}.{table_id} not found")
            raise
        except Exception as e:
            logger.error(f"Error getting table schema: {e}")
            raise
    
    def get_sample_data(
        self, 
        dataset_id: str, 
        table_id: str, 
        limit: int = 5
    ) -> pd.DataFrame:
        """
        Get sample data from a BigQuery table.
        
        Args:
            dataset_id: BigQuery dataset ID
            table_id: BigQuery table ID
            limit: Number of rows to retrieve
            
        Returns:
            DataFrame with sample data
        """
        try:
            query = f"""
            SELECT * 
            FROM `{self.table_project_id}.{dataset_id}.{table_id}` 
            LIMIT {limit}
            """
            
            df = self.client.query(query).to_dataframe()
            logger.info(f"Retrieved {len(df)} sample rows from {dataset_id}.{table_id}")
            return df
            
        except Exception as e:
            logger.error(f"Error getting sample data: {e}")
            raise
    
    def execute_query(
        self, 
        query: str
    ) -> pd.DataFrame:
        """
        Execute a BigQuery SQL query.
        
        Args:
            query: SQL query to execute
            
        Returns:
            DataFrame with query results
        """
        try: #TODO: Can add javascript within the SQL for more complex processing
    
            logger.info(f"Executing query: {query[:200]}...")
            query_job = self.client.query(query)
            df = query_job.to_dataframe()
            
            logger.info(f"Query returned {len(df)} rows")
            return df
            
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise
    
    def get_table_info(self, dataset_id: str, table_id: str) -> Dict[str, Any]:
        """
        Get comprehensive information about a BigQuery table.
        
        Args:
            dataset_id: BigQuery dataset ID
            table_id: BigQuery table ID
            
        Returns:
            Dictionary with table information
        """
        try:
            table_ref = f"{self.table_project_id}.{dataset_id}.{table_id}"
            table = self.client.get_table(table_ref)
            
            info = {
                'project': self.table_project_id,
                'dataset': dataset_id,
                'table': table_id,
                'full_table_id': table_ref,
                'num_rows': table.num_rows,
                'num_bytes': table.num_bytes,
                'created': table.created,
                'modified': table.modified,
                'description': table.description or ''
            }
            
            logger.info(f"Retrieved table info for {table_ref}")
            return info
            
        except Exception as e:
            logger.error(f"Error getting table info: {e}")
            raise
    
    def validate_query(self, query: str) -> bool:
        """
        Validate a SQL query without executing it.
        
        Args:
            query: SQL query to validate
            
        Returns:
            True if query is valid, False otherwise
        """
        try:
            job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
            self.client.query(query, job_config=job_config)
            logger.info("Query validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Query validation failed: {e}")
            return False
    