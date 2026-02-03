# Weather Agent - Quick Start Guide

Get your Weather Data Agent up and running in minutes!

## Prerequisites

Before you begin, ensure you have:

- **Python 3.9 or higher** ([Download here](https://www.python.org/downloads/))
- **Git** (to clone the repository)
- **Google Cloud Platform account** with BigQuery access
- **OpenAI API key** (FuelIX API access)
- **GCP Service Account credentials** (JSON file)

## Quick Setup (5 Minutes)

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd bb-weather-agent
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy the example environment file:

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_fuelix_api_key_here

# GCP Configuration
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/credentials.json
GCP_PROJECT_ID=your-gcp-project-id
BQ_TABLE_PROJECT_ID=cio-datahub-enterprise-pr-183a
BIGQUERY_DATASET=ent_common_location
BIGQUERY_TABLE=bq_weather_current

# Proxy Configuration (if behind corporate firewall)
HTTP_PROXY=
HTTPS_PROXY=
NO_PROXY=localhost,127.0.0.1

# Agent Configuration
LOG_LEVEL=INFO
MAX_QUERY_RESULTS=1000
OPENAI_MODEL=claude-sonnet-4-5
TEMPERATURE=0.1
```

### 5. Run the Application

```bash
python streamlit_ui.py
```

The Streamlit app will open in your browser at `http://localhost:8501`

## Detailed Setup Guide

### Getting GCP Credentials

1. **Install the Google SDK:** https://docs.cloud.google.com/sdk/docs/install-sdk 

2. **Authorize your ADC credentials:**
   - Open up a new terminal window and run the following command
   ```bash
   gcloud auth application-default login
   ```

3. **Copy the file path of the ADC credentials:**
   - Once you run the above command, you should see a file path
   - e.g., `C:/Users/YourUsername/AppData/Roaming/gcloud/application_default_credentials.json`
   - Update `GOOGLE_APPLICATION_CREDENTIALS` in `.env` with this path

### Getting FuelIX API Key

Copy your FueliX Key from https://dev.fuelix.ai/en 

### Environment Variable Details

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your FuelIX API key | `sk-...` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Full path to GCP credentials JSON | `C:\Users\You\creds.json` |
| `GCP_PROJECT_ID` | Your GCP project for authentication | `your-project-123` |
| `BQ_TABLE_PROJECT_ID` | Project containing the weather table | `cio-datahub-enterprise-pr-183a` |
| `BIGQUERY_DATASET` | BigQuery dataset name | `ent_common_location` |
| `BIGQUERY_TABLE` | BigQuery table name | `bq_weather_current` |
| `HTTP_PROXY` | Corporate proxy (if needed) | `http://198.161.14.25:8080` |
| `HTTPS_PROXY` | Corporate HTTPS proxy (if needed) | `http://198.161.14.25:8080` |
| `OPENAI_MODEL` | LLM model to use | `gpt-5` |
| `TEMPERATURE` | LLM temperature (0.0-1.0) | `0.1` |
| `MAX_QUERY_RESULTS` | Maximum rows returned | `1000` |

## Testing Your Installation

### Test 1: Verify Python Installation

```bash
python --version
# Should show Python 3.9 or higher
```

### Test 2: Verify Dependencies

```bash
pip list | grep -E "langchain|streamlit|google-cloud-bigquery"
```

### Test 3: Test Configuration

Create a simple test script:

```python
# test_config.py
from src.utils.config import Config

if Config.validate():
    print("✓ Configuration is valid!")
    print(f"✓ GCP Project: {Config.GCP_PROJECT_ID}")
    print(f"✓ Table: {Config.get_full_table_name()}")
else:
    print("✗ Configuration validation failed")
```

Run it:
```bash
python test_config.py
```

## Running the Application

### Development Mode

```bash
streamlit run streamlit_ui.py
```

### Custom Port

```bash
streamlit run streamlit_ui.py --server.port 8080
```

### Accessible on Network

```bash
streamlit run streamlit_ui.py --server.address 0.0.0.0
```

## Using the Application

### Example Queries

Once the app is running, try these queries:

**Current Weather:**
- "What's the current weather in Toronto?"
- "Show me the latest temperature in Vancouver"

**Location Queries:**
- "Find all weather data within 5km of Toronto"
- "What locations are currently being monitored?"

**Analytics:**
- "Which location has the highest temperature right now?"
- "Show me average humidity across all locations"

**Time-Based:**
- "Show me weather data from the last 24 hours"
- "What was the temperature in Montreal yesterday?"

### Special Commands

Type these in the chat:

- `/help` - Show available commands
- `/schema` - Display the BigQuery table schema
- `/status` - Check system status and connection
- `/history` - View conversation history
- `/clear` - Clear conversation history

## Troubleshooting

### Common Issues

#### 1. "Module not found" errors

**Problem:** Python can't find installed packages

**Solution:**
```bash
# Ensure virtual environment is activated
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 2. "Google credentials file not found"

**Problem:** `GOOGLE_APPLICATION_CREDENTIALS` path is incorrect

**Solution:**
- Verify the path in `.env` is absolute (full path)
- Use forward slashes `/` or double backslashes `\\` on Windows
- Example: `C:/Users/YourName/credentials.json`

#### 3. "Table not found" error

**Problem:** Can't access BigQuery table

**Solutions:**
- Verify `GCP_PROJECT_ID` and `BQ_TABLE_PROJECT_ID` are correct
- Check service account has "BigQuery Data Viewer" role
- Confirm dataset and table names are correct

#### 4. "Connection timeout" or "Proxy error"

**Problem:** Corporate firewall blocking requests

**Solution:**
```env
# Add to .env
HTTP_PROXY=http://your-proxy:8080
HTTPS_PROXY=http://your-proxy:8080
NO_PROXY=localhost,127.0.0.1
```

#### 5. "Invalid API key" (OpenAI/FuelIX)

**Problem:** API key is incorrect or expired

**Solution:**
- Verify `OPENAI_API_KEY` in `.env`
- Ensure no extra spaces or quotes
- Create a new key on the FueliX Dev page

#### 6. Streamlit won't start

**Problem:** Port already in use

**Solution:**
```bash
# Use different port
streamlit run streamlit_ui.py --server.port 8502
```

### Enable Debug Logging

For more detailed error messages:

```env
# In .env
LOG_LEVEL=DEBUG
```

### Check Logs

View detailed logs while running:
```bash
python streamlit_ui.py 2>&1 | tee app.log
```

## Deployment Options

### Deploy on Streamlit Cloud

1. Push your code to GitHub (without `.env` file!)
2. Go to https://share.streamlit.io/
3. Connect your GitHub repository
4. Add secrets in Streamlit Cloud dashboard (Settings > Secrets):
   ```toml
   OPENAI_API_KEY = "your-key"
   GCP_PROJECT_ID = "your-project"
   # ... add all other env vars
   ```

**Note:** For GCP credentials, you'll need to either:
- Use Streamlit secrets for the entire JSON content
- Set up GCP authentication via service account in the cloud environment

## Next Steps

- Read the full [README.md](README.md) for detailed architecture
- Explore the codebase in the `src/` directory
- Check TODO comments in the code for enhancement opportunities

## Getting Help

- Check the [Troubleshooting](#troubleshooting) section above
- Review error logs with `LOG_LEVEL=DEBUG`
- Contact the AIA Special Projects or Bumblebee Team

## Security Notes

**Never commit your `.env` file to version control!**

The `.gitignore` file already excludes it, but always verify:
- API keys and credentials are in `.env` only
- `.env` is listed in `.gitignore`
- Use `.env.example` as a template for others

---

