import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
load_dotenv()

from src.config import *
from src.utils.api import query_endpoint
from src.utils.commands import event_data, handle_command
from src.utils.logger import logger
from src.utils.process import process_images


# Initialize the app with your bot token
app = App(token=SLACK_BOT_TOKEN)

# In-memory storage for thread IDs and tools
conversation_threads = {}
channel_tools = {}  # New dictionary to store tools per channel
channel_system_messages = {}  # New dictionary to store system messages per channel

# Listener for messages where the bot is tagged
@app.event("app_mention")
def handle_app_mention(event, say):
    # Extract data from the event
    channel_id, user_id, text = event_data(event)

    # Extract images from the event
    images = process_images(event)
                      
    # Handle commands
    handle_command(event, say, channel_tools, channel_system_messages, conversation_threads)

    # Extract the query
    question = text.split(maxsplit=1)[-1] if len(text.split()) > 1 else "What can I help you with?"

    # Check if there's an existing thread for this channel
    thread_id = conversation_threads.get(channel_id)

    logger.info(f"Received question from USER <@{user_id}> in CHANNEL <#{channel_id}>: {question} (Thread ID: {thread_id})")
    if images:
        logger.info(f"Received {len(images)} images with the query")

    # Query the API with images
    new_thread_id, response = query_endpoint(
        question, 
        thread_id, 
        channel_id, 
        images, 
        channel_system_messages, 
        channel_tools
    )

    # Update thread context
    if new_thread_id:
        conversation_threads[channel_id] = new_thread_id
        logger.info(f"New thread ID for channel {channel_id}: {new_thread_id}")

    # Log the query and response for tracking
    logger.info(f"Channel: {channel_id}, User: {user_id}, Query: {question}, Thread ID: {thread_id}, Response: {response}")

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
    logger.info(f"Starting Slack bot with client at {BASE_API_URL}")
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()
