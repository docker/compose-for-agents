import streamlit as st
import requests
import json
import os
import uuid
import time
import sseclient

st.set_page_config(
    page_title="Vendor Portal",
    page_icon="🧦",
    layout="wide"
)

API_BASE_URL = os.environ.get('API_BASE_URL', "http://adk:8000")
APP_NAME = "agents"

if "user_id" not in st.session_state:
    st.session_state.user_id = f"vendor-{uuid.uuid4()}"

if "session_id" not in st.session_state:
    st.session_state.session_id = None
    
if "messages" not in st.session_state:
    st.session_state.messages = []

def create_adk_session():
    try:
        session_id = f"session={int(time.time())}"
        response = requests.post(
            f"{API_BASE_URL}/apps/{APP_NAME}/users/{st.session_state.user_id}/sessions/{session_id}",
            headers={"Content-Type": "application/json"},
            data=json.dumps({})
        )
        if response.status_code == 200:
            st.session_state.session_id = session_id
            st.session_state.messages = []
            st.rerun()
            return True
        else:
            st.error(f"Failed to create session: {response.text}")
            return False
    except Exception as e:
        return False


def summarize(part):
    """
    parts can be Dictionaries with keys like functionCall, functionResponse, or text.
    we will summarize each message differently depending on whether it contains a functionCall,
    a functionResponse, text, or none of these.
    If there is a functionCall key, then value will be a dictionary with the key name.
    If there is a functionResponse key, then the value will be a dictionary that has a name key
    If there is a text key, then the value will be a string.
    """
    if isinstance(part, dict):
        if "functionCall" in part:
            function_name = part["functionCall"].get("name", "Unknown Function")
            return f"🔧 **Function Call**: {function_name}"
        elif "functionResponse" in part:
            function_name = part["functionResponse"].get("name", "Unknown Function")
            return f"📋 **Function Response**: {function_name}"
        elif "text" in part:
            text_content = part["text"]
            # Truncate long text for summary
            if len(text_content) > 100:
                return f"💬 **Text**: {text_content[:100]}..."
            else:
                return f"💬 **Text**: {text_content}"
        else:
            return f"📄 **Unknown Content**: {list(part.keys())}"
    else:
        return f"📄 **Raw Content**: {str(part)}"

def summarize_content(parts):
    return "\n".join([summarize(part) for part in parts])


def display_messages(container):
    """Display messages in the provided container"""
    with container.container():
        for message in st.session_state.messages:
            if message["role"] == "event":
                # Display SSE events in a bordered container
                with st.container(border=True):
                    # Title with content message
                    author = message['content'].get("author", "Unknown")
                    role = message["content"]["content"].get("role", "Unknown") if isinstance(message["content"], dict) else "Unknown"
                    st.markdown(f"<h5 style='text-decoration: underline;'>{author}</h4>", unsafe_allow_html=True)
                    
                    # Additional markdown section
                    st.markdown(summarize_content(message['content']['content']['parts']))
                    
                    # Expander with JSON content
                    with st.expander("View Details"):
                        st.json(message["content"]["content"]["parts"])
            else:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

def send_message(message, messages_container):
    """
    Send a message to the speaker agent and process the SSE response stream.
    
    This function:
    1. Adds the user message to the chat history
    2. Sends the message to the ADK SSE API
    3. Processes the SSE event stream
    4. Updates only the messages container for each event
    
    Args:
        message (str): The user's message to send to the agent
        messages_container: Streamlit container for messages
        
    Returns:
        bool: True if message was sent and processed successfully, False otherwise
    
    API Endpoint:
        POST /run_sse
        
    Response Processing:
        - Streams SSE events from the ADK API
        - Updates only the messages container for each event
    """
    if not st.session_state.session_id:
        st.error("No active session. Please create a session first.")
        return False
    
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": message})
    
    # Update messages display immediately
    display_messages(messages_container)
    
    try:
        # Send message to SSE API
        response = requests.post(
            f"{API_BASE_URL}/run_sse",
            headers={"Content-Type": "application/json"},
            data=json.dumps({
                "app_name": APP_NAME,
                "user_id": st.session_state.user_id,
                "session_id": st.session_state.session_id,
                "new_message": {
                    "role": "user",
                    "parts": [{"text": message}]
                }
            }),
            stream=True
        )
        
        if response.status_code != 200:
            st.error(f"Error: {response.text}")
            return False
        
        # Process SSE events with real-time updates
        client = sseclient.SSEClient(response)
        for event in client.events():
            if event.data:
                try:
                    event_data = json.loads(event.data)
                    # Add each SSE event to messages
                    st.session_state.messages.append({"role": "event", "content": event_data})
                    # Update only the messages container
                    display_messages(messages_container)
                except json.JSONDecodeError:
                    # Handle non-JSON events
                    st.session_state.messages.append({"role": "event", "content": event.data})
                    display_messages(messages_container)
        
        return True
        
    except Exception as e:
        st.error(f"Error processing SSE stream: {str(e)}")
        return False

st.title("🧦 Sock Shop Vendor Portal")

with st.sidebar:
    st.header("Session Info")

    if st.session_state.session_id:
        st.success(f"Active session: {st.session_state.session_id}")
        if st.button("➕ New Session"):
            create_adk_session()
    else:
        st.warning("No active session")
        if st.button("➕ Create Session"):
            create_adk_session()

st.subheader("Conversation")
st.markdown("Welcome! Chat with our agent to learn how to add your socks to our store.")

# Create a container for messages that can be updated
messages_container = st.empty()

# Initial display of messages
display_messages(messages_container)

if st.session_state.session_id:  # Only show input if session exists
    user_input = st.chat_input("Type your message...")
    if user_input:
        send_message(user_input, messages_container)
else:
    st.info("👈 Create a session to start chatting")

