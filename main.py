import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Initialize the app with your bot token
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Listener for messages where the bot is tagged
@app.event("app_mention")
def handle_app_mention(event, say):
    user_id = event['user']
    text = event['text']
    print(f"Hello <@{user_id}>, you mentioned me with: {text}")
    say(f"Hello <@{user_id}>, you mentioned me with: {text}")
    
# Listens to incoming messages that contain "hello"
# To learn available listener arguments,
# https://tools.slack.dev/bolt-python/getting-started/
# visit https://tools.slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html
@app.message("hello")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    say(f"Hey there <@{message['user']}>!")

# Start the app
if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()

