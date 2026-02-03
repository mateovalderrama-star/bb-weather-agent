# Weather Data Agent 🌤️

A Langchain-based AI agent for querying weather data from Google BigQuery using natural language. This agent implements the architecture shown in your diagram with real-time query flow through Copilot orchestration, Langchain agent processing, and BigQuery data access.

## Architecture

The system follows this flow:
1. **User** → Sends weather query via chat interface
2. **Copilot** → Orchestrates the request and manages conversation
3. **Langchain Agent** → Processes natural language and generates SQL
4. **Schema Manager** → Provides BigQuery table schema context
5. **BigQuery** → Executes queries on weather data
6. **FuelIX LLM (OpenAI)** → Powers natural language understanding
7. **Response Synthesis** → Formats and returns the answer

## Features

- 🤖 Natural language queries for weather data
- 📊 Automatic SQL query generation
- 🔍 Schema-aware query processing
- 💬 Interactive chat interface
- 📈 Support for aggregations and analytics
- 🛡️ Query validation and safety checks
- 📝 Conversation history tracking
- 🎨 Rich terminal UI with syntax highlighting

## Prerequisites

- Python 3.9+
- Google Cloud Platform account with BigQuery access
- OpenAI API key
- Google Cloud credentials file

## Installation

1. **Clone or navigate to the weather-agent directory:**
   ```bash
   cd weather-agent
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and configure:
   ```env
   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key_here
   
   # GCP Configuration
   GOOGLE_APPLICATION_CREDENTIALS=C:/Users/YourUsername/AppData/Roaming/gcloud/application_default_credentials.json
   GCP_PROJECT_ID=cio-datahub-enterprise-pr-183a
   BIGQUERY_DATASET=ent_common_location
   BIGQUERY_TABLE=bq_weather_current
   
   # Proxy Configuration (if needed)
   HTTP_PROXY=
   HTTPS_PROXY=
   NO_PROXY=localhost,127.0.0.1
   
   # Agent Configuration
   OPENAI_MODEL=gpt-5
   TEMPERATURE=0.0
   MAX_QUERY_RESULTS=1000
   ```

## Usage

### Starting the Agent

Run the main application:
```bash
streamlit run streamlit_ui.py
```

### Example Queries

Once the chat interface starts, you can ask questions like:

**Current Weather:**
- "What's the current weather in Toronto?"
- "Show me the latest weather data for Vancouver"

**Historical Data:**
- "What was the weather like in Montreal yesterday?"
- "Show me weather data from last week"

**Analytics:**
- "Which locations had the highest temperature today?"
- "Give me average precipitation for all locations"
- "Show me temperature trends for the past 7 days"

**Aggregations:**
- "What's the average temperature across all locations?"
- "Which city has the most rainfall?"
- "Compare temperatures between Toronto and Vancouver"

### Available Commands

- `/help` - Show available commands and examples
- `/schema` - Display the BigQuery table schema
- `/status` - Check system status and connection
- `/history` - View conversation history
- `/clear` - Clear conversation history
- `/exit` or `/quit` - Exit the application

## Project Structure

```
bb-weather-agent/
├── src/
│   ├── __init__.py
│   ├── agent.py              # Langchain SQL agent
│   ├── copilot.py            # Orchestration layer
│   ├── schema_manager.py     # BigQuery schema management
│   ├── chat_interface.py     # CLI chat interface
│   └── utils/
│       ├── __init__.py
│       ├── config.py         # Configuration management
│       └── bigquery_helper.py # BigQuery utilities
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
└── README.md                # This file
```

## How It Works

### 1. Query Processing Flow

```
User Input → Copilot → Langchain Agent → SQL Generation → BigQuery Execution → Response Synthesis
```

### 2. Components

**Copilot (`copilot.py`)**
- Manages conversation flow
- Handles special commands
- Maintains conversation history
- Synthesizes final responses

**Langchain Agent (`agent.py`)**
- Processes natural language queries
- Generates SQL queries using LLM
- Executes queries against BigQuery
- Validates and formats results

**Schema Manager (`schema_manager.py`)**
- Fetches BigQuery table schema
- Provides context to the LLM
- Generates field descriptions
- Supplies example queries

**Chat Interface (`chat_interface.py`)**
- Rich terminal UI
- User input handling
- Response formatting
- Command processing

### 3. Safety Features

- **Read-only queries**: Only SELECT statements allowed
- **Query validation**: Dry-run validation before execution
- **Result limits**: Configurable maximum result size
- **Error handling**: Comprehensive error catching and reporting
- **Cost estimation**: BigQuery query cost calculation

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to GCP credentials | Required |
| `GCP_PROJECT_ID` | GCP project ID | `cio-datahub-enterprise-pr-183a` |
| `BIGQUERY_DATASET` | BigQuery dataset | `ent_common_location` |
| `BIGQUERY_TABLE` | BigQuery table | `bq_weather_current` |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-5` |
| `TEMPERATURE` | LLM temperature | `0.0` |
| `MAX_QUERY_RESULTS` | Max rows to return | `1000` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Future Enhancements

### Infrastructure Outage Integration

The architecture is designed to support cross-referencing with Telus infrastructure outage data:

1. **Multi-table queries**: Query both weather and outage tables
2. **Correlation analysis**: Link weather conditions to outages
3. **Advanced analytics**: Identify patterns between weather and infrastructure issues

Example future queries:
- "What type of weather caused the outage in location X?"
- "Show me all outages that occurred during severe weather"
- "Correlate temperature extremes with network outages"

### Planned Features

- [ ] Streamlit web interface
- [ ] Query result visualization
- [ ] Export results to CSV/Excel
- [ ] Scheduled query execution
- [ ] Alert system for weather conditions
- [ ] Integration with infrastructure outage data
- [ ] Advanced analytics and ML predictions

## Troubleshooting

### Common Issues

**1. Authentication Error**
```
Error: Google credentials file not found
```
Solution: Ensure `GOOGLE_APPLICATION_CREDENTIALS` points to a valid credentials file.

**2. BigQuery Connection Error**
```
Error: Table not found
```
Solution: Verify the project ID, dataset, and table name in `.env`.

**3. OpenAI API Error**
```
Error: Invalid API key
```
Solution: Check that `OPENAI_API_KEY` is set correctly in `.env`.

**4. Proxy Issues**
```
Error: Connection timeout
```
Solution: Configure proxy settings in `.env` if behind a corporate firewall.

## Development

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# With coverage
pytest --cov=src tests/
```

### Code Style

The project follows PEP 8 style guidelines. Format code with:
```bash
black src/
isort src/
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Add tests if applicable
4. Submit a pull request

## License

Internal use only - Telus Corporation

## Support

For issues or questions, contact the AIA Special Projects or Bumblebee Team.

## Acknowledgments

- Built with [Langchain](https://python.langchain.com/)
- Powered by [OpenAI](https://openai.com/)
- Data from [Google BigQuery](https://cloud.google.com/bigquery)
- UI with [Streamlit](https://docs.streamlit.io/)
