"""Streamlit UI for the weather agent."""

import streamlit as st
from src.copilot import WeatherCopilot

def main():
    """Main entry point for the Streamlit UI."""

    # Initialize the copilot
    copilot = WeatherCopilot()

    # Set page title and icon
    st.set_page_config(
        page_title="Weather Agent",
        page_icon=":sunny:",
        layout="wide"
    )

    # Display welcome message
    st.title("🌤️ Weather Data Agent")
    st.write("Welcome! I'm your AI assistant for querying weather data from BigQuery.")
    st.write("""**What I can do:**
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
""")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What would you like to know about the weather?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Process the query
        with st.spinner("Processing your query..."):
            result = copilot.process_query(prompt)

        # Display the response
        with st.chat_message("assistant"):
            if result.get('success'):
                # Display the answer
                answer = result.get('answer', 'No answer provided')

                # Check if it's a command response
                if result.get('is_command'):
                    st.markdown(f"**Command Response:** {answer}")
                else:
                    # Regular query response
                    st.markdown(f"**🤖 Assistant:** {answer}")

                    # Display notes/follow-up suggestions if available
                    if 'notes' in result:
                        st.markdown(f"**📝 Notes:** {result['notes']}")
            else:
                # Display error
                error_msg = result.get('answer', 'An error occurred')
                st.markdown(f"**❌ Error:** {error_msg}")

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": answer})

if __name__ == "__main__":
    main()
