from src.commands import event_data, handle_command
from src.utils.api import query_endpoint
from src.utils.logger import logger
from src.utils.process import process_images

class MentionController:
    def __init__(self):
        self.conversation_threads = {}
        self.channel_tools = {}
        self.channel_system_messages = {}

    def handle_mention(self, event, say):
        # Extract data from the event
        channel_id, user_id, text = event_data(event)

        # Extract images from the event
        images = process_images(event)
        
        # Handle commands first
        handled = handle_command(
            event, 
            say, 
            self.channel_tools, 
            self.channel_system_messages, 
            self.conversation_threads
        )
                          
        if not handled:
            # Extract the query
            question = text.split(maxsplit=1)[-1] if len(text.split()) > 1 else "What can I help you with?"

            # Check if there's an existing thread for this channel
            thread_id = self.conversation_threads.get(channel_id)

            logger.info(f"Received question from USER <@{user_id}> in CHANNEL <#{channel_id}>: {question} (Thread ID: {thread_id})")
            if images:
                logger.info(f"Received {len(images)} images with the query")

            # Query the API with images
            new_thread_id, response = query_endpoint(
                question, 
                thread_id, 
                channel_id, 
                images, 
                self.channel_system_messages, 
                self.channel_tools
            )

            # Update thread context
            if new_thread_id:
                self.conversation_threads[channel_id] = new_thread_id
                logger.info(f"New thread ID for channel {channel_id}: {new_thread_id}")

            # Log the query and response for tracking
            logger.info(f"Channel: {channel_id}, User: {user_id}, Query: {question}, Thread ID: {thread_id}, Response: {response}")

            say(response)