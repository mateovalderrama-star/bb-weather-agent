"""Chat interface for the weather agent."""

import logging
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich import box
from src.copilot import WeatherCopilot
from src.utils.config import Config

logger = logging.getLogger(__name__)


class ChatInterface:
    """Command-line chat interface for the weather agent."""
    
    def __init__(self):
        """Initialize the chat interface."""
        self.console = Console()
        self.copilot = WeatherCopilot()
        self.running = False
        
    def start(self) -> None:
        """Start the chat interface."""
        self.running = True
        
        # Display welcome message
        self._display_welcome()
        
        # Main chat loop
        while self.running:
            try:
                # Get user input
                user_input = self._get_user_input()
                
                if not user_input:
                    continue
                
                # Check for exit command
                if user_input.lower() in ['/exit', '/quit', 'exit', 'quit']:
                    self._display_goodbye()
                    break
                
                # Process the query
                self._process_and_display(user_input)
                
            except KeyboardInterrupt:
                self.console.print("\n\n[yellow]Interrupted by user[/yellow]")
                self._display_goodbye()
                break
            except Exception as e:
                logger.error(f"Error in chat loop: {e}")
                self.console.print(f"\n[red]Error: {e}[/red]\n")
    
    def _display_welcome(self) -> None:
        """Display welcome message."""
        welcome_text = """
# 🌤️  Weather Data Agent

Welcome! I'm your AI assistant for querying weather data from BigQuery.

**What I can do:**
- Answer questions about current and historical weather
- Provide weather statistics and trends
- Query weather data by location, time, and conditions

**Commands:**
- `/help` - Show available commands
- `/schema` - View database schema
- `/status` - Check system status
- `/exit` - Exit the application

**Example queries:**
- "What's the current weather in Toronto?"
- "Show me temperature trends for Vancouver"
- "Which locations had the highest temperature yesterday?"

Type your question or command below to get started!
"""
        
        self.console.print(Panel(
            Markdown(welcome_text),
            title="Weather Agent",
            border_style="blue",
            box=box.DOUBLE
        ))
        self.console.print()
    
    def _display_goodbye(self) -> None:
        """Display goodbye message."""
        self.console.print("\n")
        self.console.print(Panel(
            "[bold cyan]Thank you for using Weather Agent! Goodbye! 👋[/bold cyan]",
            border_style="blue"
        ))
    
    def _get_user_input(self) -> str:
        """
        Get input from the user.
        
        Returns:
            User input string
        """
        try:
            user_input = self.console.input("\n[bold cyan]You:[/bold cyan] ").strip()
            return user_input
        except EOFError:
            return "/exit"
    
    def _process_and_display(self, user_input: str) -> None:
        """
        Process user input and display the response.
        
        Args:
            user_input: User's input string
        """
        # Show processing indicator
        with self.console.status("[bold green]Processing your query...", spinner="dots"):
            result = self.copilot.process_query(user_input)
        
        # Display the response
        self._display_response(result)
    
    def _display_response(self, result: dict) -> None:
        """
        Display the agent's response.
        
        Args:
            result: Response dictionary from the copilot
        """
        self.console.print()
        
        if result.get('success'):
            # Display the answer
            answer = result.get('answer', 'No answer provided')
            
            # Check if it's a command response
            if result.get('is_command'):
                self.console.print(Panel(
                    answer,
                    title="Command Response",
                    border_style="green"
                ))
            else:
                # Regular query response
                self.console.print(Panel(
                    Markdown(answer),
                    title="🤖 Assistant",
                    border_style="green",
                    box=box.ROUNDED
                ))
                
                # Display SQL queries if available
                if 'sql_queries' in result and result['sql_queries']:
                    self._display_sql_queries(result['sql_queries'])
        else:
            # Display error
            error_msg = result.get('answer', 'An error occurred')
            self.console.print(Panel(
                f"[red]{error_msg}[/red]",
                title="❌ Error",
                border_style="red"
            ))
    
    def _display_sql_queries(self, queries: list) -> None:
        """
        Display SQL queries that were executed.
        
        Args:
            queries: List of SQL query strings
        """
        self.console.print("\n[dim]SQL Queries Executed:[/dim]")
        
        for i, query in enumerate(queries, 1):
            # Clean up the query string
            if isinstance(query, dict):
                query = query.get('query', str(query))
            
            query_str = str(query).strip()
            
            # Create a table for better formatting
            table = Table(
                show_header=False,
                box=box.SIMPLE,
                border_style="dim"
            )
            table.add_column("Query", style="cyan")
            table.add_row(query_str)
            
            self.console.print(f"\n[dim]Query {i}:[/dim]")
            self.console.print(table)


def main():
    """Main entry point for the chat interface."""
    # Setup configuration
    Config.setup_proxy()
    
    # Validate configuration
    if not Config.validate():
        print("Configuration validation failed. Please check your .env file.")
        return
    
    # Start the chat interface
    interface = ChatInterface()
    interface.start()


if __name__ == "__main__":
    main()
