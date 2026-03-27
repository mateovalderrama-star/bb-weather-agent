"""Langchain SQL agent for querying Cloud SQL (MySQL) weather data."""
import logging
from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from src.utils.config import Config
from src.utils.cloudsql_helper import CloudSQLHelper
from src.schema_manager import SchemaManager

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a MySQL expert generating queries against a Cloud SQL database.

Rules:
- Use LIMIT to restrict results (max {max_results} rows).
- For geographic distance: ST_Distance_Sphere(POINT(lon, lat), POINT(lon, lat)).
- Use information_schema to discover tables when unsure.
- Always check query syntax with sql_db_query_checker before executing.
- Use JOINs to correlate data across tables when the question involves multiple data types.
- Do NOT run DROP, DELETE, UPDATE, INSERT, or DDL statements.
- Use backtick-quoted identifiers for table/column names with special characters.
""".format(max_results=Config.MAX_QUERY_RESULTS)


class WeatherAgent:
    """Langchain-based SQL agent for weather data queries."""

    def __init__(self):
        """Initialize the weather agent."""
        self.config = Config
        self.cloud_sql_helper = CloudSQLHelper()
        self.schema_manager = SchemaManager(self.cloud_sql_helper)
        self.llm = None
        self.db = None
        self.agent = None

        self._initialize_agent()

    def _initialize_agent(self) -> None:
        """Initialize the LLM, database connection, and agent."""
        try:
            logger.info(f"Initializing LLM: {self.config.OPENAI_MODEL}")
            self.llm = ChatOpenAI(
                model=self.config.OPENAI_MODEL,
                temperature=self.config.TEMPERATURE,
                openai_api_key=self.config.OPENAI_API_KEY,
                base_url='https://api.fuelix.ai/v1'
            )

            # SQLDatabase wraps the engine for the LangChain toolkit
            self.db = SQLDatabase(
                self.cloud_sql_helper.get_engine(),
                schema=self.config.CLOUD_SQL_DATABASE,
                view_support=True,
                max_string_length=500,
            )

            toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
            tools = toolkit.get_tools()  # list_tables, get_schema, query_checker, query

            logger.info("Creating Langchain tool-calling agent")
            self.agent = create_agent(
                model=self.llm,
                tools=tools,
                system_prompt=SYSTEM_PROMPT,
            )

            logger.info("Weather agent initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing agent: {e}")
            raise

    def query(self, question: str) -> Dict[str, Any]:
        """
        Process a natural language query about weather data.

        Args:
            question: Natural language question

        Returns:
            Dictionary containing the answer and metadata
        """
        try:
            logger.info(f"Processing query: {question}")

            enhanced_question = self._enhance_question(question)

            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": enhanced_question}]}
            )

            answer = "No answer generated"
            if 'messages' in result and len(result['messages']) > 0:
                last_message = result['messages'][-1]
                if hasattr(last_message, 'content'):
                    answer = last_message.content
                elif isinstance(last_message, dict) and 'content' in last_message:
                    answer = last_message['content']

            logger.info("Query processed successfully")
            return {
                'question': question,
                'answer': answer,
                'success': True,
            }

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                'question': question,
                'answer': f"Error processing query: {str(e)}",
                'success': False,
                'error': str(e),
            }

    def _enhance_question(self, question: str) -> str:
        """Enhance the question with schema context."""
        schema_context = self.schema_manager.get_full_context(include_samples=False)
        return f"""You are a helpful assistant that answers questions about weather data stored in a Cloud SQL (MySQL) database.

{schema_context}

Important Instructions:
1. Generate MySQL SQL queries to answer the user's question.
2. Format your final answer in a clear, human-readable way.
3. Do not include the SQL query in your final answer unless explicitly requested.
4. If you need to make assumptions, state them clearly.
5. Only perform SELECT queries - no INSERT, UPDATE, DELETE, or DDL operations.

User Question: {question}
"""

    def get_schema_info(self, include_samples: bool = True) -> str:
        """Get schema information for display."""
        return self.schema_manager.get_full_context(include_samples=include_samples)
