"""Langchain SQL agent for querying weather data."""
import logging
from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_classic.agents.agent import AgentExecutor
from src.utils.config import Config
from src.schema_manager import SchemaManager
from src.utils.bigquery_helper import BigQueryHelper

logger = logging.getLogger(__name__)

class WeatherAgent:
    """Langchain-based tool agent for weather data queries."""
    
    def __init__(self):
        """Initialize the weather agent."""
        self.config = Config
        self.schema_manager = SchemaManager()
        self.bq_helper = BigQueryHelper(self.config.GCP_PROJECT_ID)
        self.llm = None
        self.db = None
        self.agent = None
        
        self._initialize_agent()

    def _initialize_agent(self) -> None:
        """Initialize the LLM, database connection, and agent."""
        try:
            # Initialize OpenAI LLM
            logger.info(f"Initializing LLM: {self.config.OPENAI_MODEL}")
            self.llm = ChatOpenAI(
                model=self.config.OPENAI_MODEL,
                temperature=self.config.TEMPERATURE,
                openai_api_key=self.config.OPENAI_API_KEY,
                base_url='https://api.fuelix.ai/v1' # Custom base URL
            )
            
            # Create tool wrapper for execute_query
            @tool
            def execute_bigquery(query: str) -> str:
                """Execute a BigQuery SQL query and return results.
                
                Args:
                    query: SQL query to execute
                    
                Returns:
                    Query results as a string
                """
                df = self.bq_helper.execute_query(query)
                return df.to_string()
            
            @tool
            def validate_query(query: str) -> bool:
                """
                Validate a SQL query without executing it using bigquery helper.
                
                Args:
                    query: SQL query to validate
                    
                Returns:
                    True if query is valid, False otherwise
                """
                try:
                    return self.bq_helper.validate_query(query)
                except Exception as e:
                    logger.error(f"Query validation failed: {e}")
                    return False

            
            # Create SQL agent
            logger.info("Creating Langchain tool-calling agent") # TODO: Dynamic Model
            self.agent = create_agent(                           # TODO: Include a cache mechanism, for common locations (cities) by polygons in a txt file, have the agent refer to it first
                model=self.llm,
                tools=[execute_bigquery, validate_query],
                system_prompt= """You are a helpful weather data expert. You have access to BigQuery tools. 
                Make sure that the query does not include any destructive methods before executing.
                Always validate the query before execution. If the query is invalid, read the error message and write a corrected query."""
            )
            # TODO: Vectorize fire data, and use metadata based filtering
            logger.info("Weather agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing agent: {e}")
            raise
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Process a natural language query about weather data.
        
        Args:
            question: Natural language question about weather
            
        Returns:
            Dictionary containing the answer and metadata
        """
        try:
            logger.info(f"Processing query: {question}")
            
            # Add schema context to the question
            enhanced_question = self._enhance_question(question)
            
            # Execute the agent
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": enhanced_question}]}
            )
            
            # Extract answer from messages
            answer = "No answer generated"
            if 'messages' in result and len(result['messages']) > 0:
                # Get the last message (assistant's response)
                last_message = result['messages'][-1]
                if hasattr(last_message, 'content'):
                    answer = last_message.content
                elif isinstance(last_message, dict) and 'content' in last_message:
                    answer = last_message['content']
            
            response = {
                'question': question,
                'answer': answer,
                'success': True
            }
            
            logger.info("Query processed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                'question': question,
                'answer': f"Error processing query: {str(e)}",
                'success': False,
                'error': str(e)
            }
    
    def _enhance_question(self, question: str) -> str:
        """
        Enhance the question with schema context.
        
        Args:
            question: Original question
            
        Returns:
            Enhanced question with context
        """
        # Get schema context
        schema_context = self.schema_manager.get_full_context(include_samples=True)
        #TODO: Optimize SQL generation in step 2 for faster performance
        enhanced = f"""
You are a helpful assistant that answers questions about weather data stored in BigQuery.

{schema_context}

Important Instructions:
1. Generate SQL queries to answer the user's question 
2. Format your final answer in a clear, human-readable way
3. Do not include the SQL query in your final answer unless explicitly requested
4. If you need to make assumptions, state them clearly
5. Only perform SELECT queries - no INSERT, UPDATE, or DELETE operations

User Question: {question}
"""
        
        return enhanced #TODO: Can add javascript within the SQL for more complex processing
    
    def get_schema_info(self) -> str:
        """
        Get schema information for display.
        
        Returns:
            Formatted schema information
        """
        return self.schema_manager.get_full_context(include_samples=True)
    
    