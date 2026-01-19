"""Copilot orchestration layer for the weather agent."""

import logging
from typing import Dict, Any, List, Optional
from src.agent import WeatherAgent
from src.utils.config import Config

logger = logging.getLogger(__name__)


class WeatherCopilot:
    """
    Orchestration layer that manages the conversation flow and coordinates
    between the user, the Langchain agent, and the BigQuery data source.
    """
    
    def __init__(self):
        """Initialize the copilot."""
        self.agent = WeatherAgent()
        self.conversation_history: List[Dict[str, str]] = []
        self.config = Config
        
        logger.info("Weather Copilot initialized")
    
    def process_query(self, user_input: str) -> Dict[str, Any]:
        """
        Process a user query through the complete pipeline.
        
        This is the main entry point that:
        1. Parses user intent
        2. Routes to the appropriate agent
        3. Processes the query
        4. Synthesizes the final answer
        
        Args:
            user_input: User's natural language query
            
        Returns:
            Dictionary containing the response and metadata
        """
        try:
            logger.info(f"Copilot processing query: {user_input}")
            
            # Add to conversation history
            self.conversation_history.append({
                'role': 'user',
                'content': user_input
            })
            
            # Check for special commands
            if user_input.lower().startswith('/'):
                return self._handle_command(user_input)
            
            # Process through the agent
            result = self.agent.query(user_input)
            
            # Add response to conversation history
            if result['success']:
                self.conversation_history.append({
                    'role': 'assistant',
                    'content': result['answer']
                })
            
            # Synthesize final response
            response = self._synthesize_response(result)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in copilot processing: {e}")
            return {
                'success': False,
                'answer': f"I encountered an error processing your query: {str(e)}",
                'error': str(e)
            }
    
    def _handle_command(self, command: str) -> Dict[str, Any]:
        """
        Handle special commands.
        
        Args:
            command: Command string starting with /
            
        Returns:
            Command response
        """
        cmd = command.lower().strip()
        
        if cmd == '/help':
            return {
                'success': True,
                'answer': self._get_help_text(),
                'is_command': True
            }
        
        elif cmd == '/schema':
            return {
                'success': True,
                'answer': self.agent.get_schema_info(include_samples=False),
                'is_command': True
            }
        
        elif cmd == '/history':
            return {
                'success': True,
                'answer': self._format_history(),
                'is_command': True
            }
        
        elif cmd == '/clear':
            self.conversation_history = []
            return {
                'success': True,
                'answer': 'Conversation history cleared.',
                'is_command': True
            }
        
        elif cmd == '/status':
            return {
                'success': True,
                'answer': self._get_status(),
                'is_command': True
            }
        
        else:
            return {
                'success': False,
                'answer': f"Unknown command: {command}. Type /help for available commands.",
                'is_command': True
            }
    
    def _synthesize_response(self, agent_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize the final response from agent results.
        
        Args:
            agent_result: Result from the agent
            
        Returns:
            Synthesized response
        """
        response = {
            'success': agent_result['success'],
            'answer': agent_result['answer'],
            'question': agent_result['question']
        }
        # uncomment below to include sql queries in the response

        # Add metadata if available 
        # if 'intermediate_steps' in agent_result and agent_result['intermediate_steps']:
        #     # Extract SQL queries from intermediate steps
        #     sql_queries = []
        #     for step in agent_result['intermediate_steps']:
        #         if len(step) >= 2:
        #             action = step[0]
        #             if hasattr(action, 'tool_input'):
        #                 sql_queries.append(action.tool_input)
            
        #     if sql_queries:
        #         response['sql_queries'] = sql_queries
        
        return response
    
    def _get_help_text(self) -> str:
        """Get help text for available commands."""
        return """
Weather Agent - Available Commands:

- /help       - Show this help message
- /schema     - Display the weather data table schema
- /history    - Show conversation history
- /clear      - Clear conversation history
- /status     - Show system status

Example Queries:
- "What's the current weather in Toronto?"
- "Show me temperature trends for Vancouver"
- "What was the weather like in Montreal yesterday?"
- "Which locations had the highest temperature?"
- "Give me average precipitation for all locations"

You can ask questions in natural language, and I'll query the weather database for you!
"""
    
    def _format_history(self) -> str:
        """Format conversation history for display."""
        if not self.conversation_history:
            return "No conversation history yet."
        
        formatted = "Conversation History:\n\n"
        for i, entry in enumerate(self.conversation_history, 1):
            role = entry['role'].capitalize()
            content = entry['content'][:200] + "..." if len(entry['content']) > 200 else entry['content']
            formatted += f"{i}. {role}: {content}\n\n"
        
        return formatted
    
    def _get_status(self) -> str:
        """Get system status information."""
        status = f"""
System Status:

✓ Weather Agent: Active
✓ Database: {self.config.get_full_table_name()}
✓ LLM Model: {self.config.OPENAI_MODEL}
✓ Conversation History: {len(self.conversation_history)} messages
✓ Max Query Results: {self.config.MAX_QUERY_RESULTS}

Connection: {'Valid' if self.agent.validate_connection() else 'Invalid'}
"""
        return status
    
    def get_conversation_context(self) -> str:
        """
        Get conversation context for maintaining state.
        
        Returns:
            Formatted conversation context
        """
        if not self.conversation_history:
            return ""
        
        context = "Previous conversation:\n"
        for entry in self.conversation_history[-5:]:  # Last 5 exchanges
            context += f"{entry['role']}: {entry['content']}\n"
        
        return context
    
    def reset(self) -> None:
        """Reset the copilot state."""
        self.conversation_history = []
        logger.info("Copilot reset")
