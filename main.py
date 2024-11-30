import os
import logging
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

load_dotenv()

# Initialize the app with your bot token
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("./logs/conversation_threads.log"),  # Save logs to a file
        logging.StreamHandler()  # Also log to console
    ]
)


# Endpoint configuration
BASE_API_URL = os.environ.get("BASE_API_URL", "https://graphchat.promptengineers.ai")
CHAT_ENDPOINT = f"{BASE_API_URL}/llm"
TOOLS_ENDPOINT = f"{BASE_API_URL}/tools"
HEADERS = {
    "accept": "application/json",
    "Content-Type": "application/json",
}

# In-memory storage for thread IDs and tools
conversation_threads = {}
channel_tools = {}  # New dictionary to store tools per channel

SYSTEM_PROMPT = ("You are a helpful Slack assistant. Be concise and to the point.")
# Function to send a query to the API
def query_endpoint(question, thread_id=None, channel_id=None):
    endpoint = f"{CHAT_ENDPOINT}/{thread_id}" if thread_id else CHAT_ENDPOINT
    payload = {
        "system": SYSTEM_PROMPT,
        "query": question,
        "stream": False,
        "tools": channel_tools.get(channel_id, []),  # Get tools for this channel
        "username": os.getenv("APP_USERNAME"),
        "password": os.getenv("APP_PASSWORD")
    }
    response = requests.post(endpoint, json=payload, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        return data.get("thread_id"), data.get("answer", {}).get("content", "I could not find an answer.")
    else:
        return None, f"Error: {response.status_code}"

# Listener for messages where the bot is tagged
@app.event("app_mention")
def handle_app_mention(event, say):
    channel_id = event["channel"]
    user_id = event["user"]
    text = event["text"]

    # Check for $get_tools command
    if "$get_tools" in text.lower():
        if channel_id in channel_tools and channel_tools[channel_id]:
            tools_list = "\n- ".join(channel_tools[channel_id])
            say(f"Currently selected tools for this channel:\n- {tools_list}")
        else:
            say("No tools are currently set for this channel.")
        return

    # Check for $settools command
    if "$set_tools" in text.lower():
        tools_input = text.split("$set_tools", 1)[1].strip()
        if tools_input:
            tools_list = [tool.strip() for tool in tools_input.split(",")]
            channel_tools[channel_id] = tools_list  # Store the tools for this channel
            formatted_tools = "\n- ".join(tools_list)
            say(f"Tools set for this channel:\n- {formatted_tools}")
        else:
            say("Please provide tools separated by commas. Example: $settools tool1, tool2, tool3")
        return

    # Check for $cleartools command
    if "$clear_tools" in text.lower():
        if channel_id in channel_tools:
            del channel_tools[channel_id]
            say("Tools have been cleared for this channel.")
        else:
            say("No tools were set for this channel.")
        return

    # Check if the user wants to reset the thread
    if "$reset" in text.lower():
        if channel_id in conversation_threads:
            del conversation_threads[channel_id]
        logging.info(f"Thread reset for channel: {channel_id}")
        say(f"Thread context has been reset for channel <#{channel_id}>.")
        return

    # Check if user wants to see available tools
    if "$list_tools" in text.lower():
        response = requests.get(TOOLS_ENDPOINT, headers=HEADERS)
        if response.status_code == 200:
            tools = response.json().get("tools", [])
            tools_list = "\n- ".join(tools)  # Create the string separately
            say(f"Available tools:\n- {tools_list}")  # Use the formatted string
        else:
            say(f"Error fetching tools: {response.status_code}")
        return

    # Extract the query, assuming it's the text after the mention
    question = text.split(maxsplit=1)[-1] if len(text.split()) > 1 else "What can I help you with?"

    # Check if there's an existing thread for this channel
    thread_id = conversation_threads.get(channel_id)

    print(f"Received question from USER <@{user_id}> in CHANNEL <#{channel_id}>: {question} (Thread ID: {thread_id})")

    # Query the API
    new_thread_id, response = query_endpoint(question, thread_id, channel_id)

    # Update thread context
    if new_thread_id:
        conversation_threads[channel_id] = new_thread_id
        logging.info(f"New thread ID for channel {channel_id}: {new_thread_id}")

    # Log the query and response for tracking
    logging.info(f"Channel: {channel_id}, User: {user_id}, Query: {question}, Thread ID: {thread_id}, Response: {response}")

    say(response)

# # Listener for a reset command
# @app.message("$reset")
# def reset_thread_context(message, say):
#     channel_id = message["channel"]

#     if channel_id in conversation_threads:
#         del conversation_threads[channel_id]
#         logging.info(f"Thread reset for channel: {channel_id}")
#         say(f"Thread context has been reset for channel <#{channel_id}>.")
#     else:
#         say(f"No active thread to reset for channel <#{channel_id}>.")

# Listens to incoming messages that contain "hello"
@app.message("hello")
def message_hello(message, say):
    say(f"Hey there <@{message['user']}>! How can I help you today?")

# Start the app
if __name__ == "__main__":
    logging.info(f"Starting Slack bot with client at {BASE_API_URL}")
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()
