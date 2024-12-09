from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
load_dotenv()

from src.config import *
from src.utils.logger import logger
from src.utils.migrations import run_migrations
from src.controllers.mention_controller import MentionController

# Initialize the app with your bot token
app = App(token=SLACK_BOT_TOKEN, name="SlackAgent")

# Initialize controllers
mention_controller = MentionController()

#####################################################################
## Listeners
#####################################################################
# Listener for messages where the bot is tagged
@app.event("app_mention")
def handle_app_mention(event, say):
    # Handle the mention
    mention_controller.handle_mention(event, say)

# Add a general message event handler
@app.event("message")
def handle_message_events(body, logger):
    # Skip messages that are from bots or app mentions (which are already handled)
    if body["event"].get("subtype") or "bot_id" in body["event"]:
        return
    
    # Log the message for debugging
    logger.info(f"Received message event: {body}")


#####################################################################
## Start the bot
#####################################################################
if __name__ == "__main__":
    try:
        # Run database migrations
        run_migrations()

        # Start the bot
        logger.info(f"Starting Slack bot with client at {BASE_API_URL}")
        handler = SocketModeHandler(app, SLACK_APP_TOKEN)
        handler.start()
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise 