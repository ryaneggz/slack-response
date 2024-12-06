import os
import logging
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
import base64

load_dotenv()

# Initialize the app with your bot token
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("conversation_threads.log"),  # Save logs to a file
        logging.StreamHandler()  # Also log to console
    ]
)


# Endpoint configuration
APP_USERNAME = os.getenv("APP_USERNAME", "admin")
APP_PASSWORD = os.getenv("APP_PASSWORD", "test1234")
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
channel_system_messages = {}  # New dictionary to store system messages per channel

SYSTEM_PROMPT = ("You are a helpful Slack assistant. Be concise and to the point.")
# Function to send a query to the API
def query_endpoint(question, thread_id=None, channel_id=None, images=None):
    endpoint = f"{CHAT_ENDPOINT}/{thread_id}" if thread_id else CHAT_ENDPOINT
    payload = {
        "system": channel_system_messages.get(channel_id, SYSTEM_PROMPT),  # Get channel-specific system message or default
        "query": question,
        "stream": False,
        "tools": channel_tools.get(channel_id, []),  # Get tools for this channel
        "images": images or []  # Add images list to payload
    }

    response = requests.post(endpoint, json=payload, headers=HEADERS, auth=(APP_USERNAME, APP_PASSWORD))
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
    
    # Extract images from the event
    images = []
    if "files" in event:
        for file in event["files"]:
            if file["mimetype"].startswith("image/"):
                # Get the file URL - prefer private URL if available
                image_url = file.get("url_private") or file.get("url_private_download") or file.get("url")
                if image_url:
                    # Add authorization header for private files
                    headers = {"Authorization": f"Bearer {os.environ.get('SLACK_BOT_TOKEN')}"}
                    # Download the image and convert to base64
                    response = requests.get(image_url, headers=headers)
                    if response.status_code == 200:
                        image_base64 = base64.b64encode(response.content).decode('utf-8')
                        images.append(f"data:{file['mimetype']};base64,{image_base64}")

    # Check for $get_tools command
    if "$get_tools" in text.lower():
        if channel_id in channel_tools and channel_tools[channel_id]:
            tools_list = "\n- ".join(channel_tools[channel_id])
            say(f"Currently selected tools for this channel:\n- {tools_list}")
        else:
            say("No tools are currently set for this channel.")
        return

    # Check for $set_tools command
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

    # Check for $set_system command
    if "$set_system" in text.lower():
        system_message = text.split("$set_system", 1)[1].strip()
        if system_message:
            channel_system_messages[channel_id] = system_message
            say(f"System message set for this channel:\n```\n{system_message}\n```")
        else:
            say("Please provide a system message. Example: $set_system You are a helpful assistant.")
        return

    # Check for $get_system command
    if "$get_system" in text.lower():
        if channel_id in channel_system_messages:
            say(f"Current system message for this channel:\n```\n{channel_system_messages[channel_id]}\n```")
        else:
            say(f"Using default system message:\n```\n{SYSTEM_PROMPT}\n```")
        return

    # Check for $clear_system command
    if "$clear_system" in text.lower():
        if channel_id in channel_system_messages:
            del channel_system_messages[channel_id]
            say("System message has been cleared for this channel. Using default message.")
        else:
            say("No custom system message was set for this channel.")
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
        response = requests.get(TOOLS_ENDPOINT, headers=HEADERS, auth=(APP_USERNAME, APP_PASSWORD))
        if response.status_code == 200:
            tools = response.json().get("tools", [])
            # Extract tool names from the dictionary objects
            tool_names = [tool.get("id", str(tool)) for tool in tools]
            tools_list = "\n- ".join(tool_names)
            say(f"Available tools:\n- {tools_list}")
        else:
            say(f"Error fetching tools: {response.status_code}")
        return

    # Extract the query
    question = text.split(maxsplit=1)[-1] if len(text.split()) > 1 else "What can I help you with?"

    # Check if there's an existing thread for this channel
    thread_id = conversation_threads.get(channel_id)

    print(f"Received question from USER <@{user_id}> in CHANNEL <#{channel_id}>: {question} (Thread ID: {thread_id})")
    if images:
        print(f"Received {len(images)} images with the query")

    # Query the API with images
    new_thread_id, response = query_endpoint(question, thread_id, channel_id, images)

    # Update thread context
    if new_thread_id:
        conversation_threads[channel_id] = new_thread_id
        logging.info(f"New thread ID for channel {channel_id}: {new_thread_id}")

    # Log the query and response for tracking
    logging.info(f"Channel: {channel_id}, User: {user_id}, Query: {question}, Thread ID: {thread_id}, Response: {response}")

    say(response)

# Add a general message event handler
@app.event("message")
def handle_message_events(body, logger):
    # Skip messages that are from bots or app mentions (which are already handled)
    if body["event"].get("subtype") or "bot_id" in body["event"]:
        return
    
    # Log the message for debugging
    logger.info(f"Received message event: {body}")

# Listens to incoming messages that contain "hello"
@app.message("hello")
def message_hello(message, say):
    say(f"Hey there <@{message['user']}>! How can I help you today?")

# Start the app
if __name__ == "__main__":
    logging.info(f"Starting Slack bot with client at {BASE_API_URL}")
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()
