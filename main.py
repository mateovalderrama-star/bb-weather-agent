"""Main entry point for the Weather Agent application."""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from streamlit_ui import main

if __name__ == "__main__":
    main()
