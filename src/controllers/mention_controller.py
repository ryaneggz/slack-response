import traceback
from src.infra.db import get_db
from src.services.db_service import DatabaseService
from src.commands import event_data, handle_command
from src.utils.api import query_endpoint
from src.utils.logger import logger
from src.utils.process import process_images

class MentionController:
    """Controller for handling bot mentions and managing channel settings."""

    def __init__(self):
        """Initialize the controller with database connection."""
        logger.info("Initializing MentionController with database connection")
        self.db = next(get_db())
        self.db_service = DatabaseService(self.db)

    def handle_mention(self, event, say):
        try:
            # Extract data from the event
            channel_id, user_id, text = event_data(event)
            logger.info(f"Handling mention in channel {channel_id} from user {user_id}")

            # Get channel settings
            settings = self.db_service.get_channel_settings(channel_id)
            logger.debug(f"Retrieved settings for channel {channel_id}: {settings}")

            # Extract images from the event
            images = process_images(event)
            if images:
                logger.debug(f"Processed {len(images)} images from the message")
            
            # Handle commands first
            handled = handle_command(
                event, 
                say, 
                self.db_service
            )
                            
            if not handled:
                logger.debug("No command detected, processing as regular message")
                # Extract the query
                question = text.split(maxsplit=1)[-1] if len(text.split()) > 1 else "What can I help you with?"

                # Check if there's an existing thread for this channel
                thread_id = settings.thread_id if settings else None
                logger.debug(f"Using thread_id: {thread_id}")

                logger.info(f"Received question from USER <@{user_id}> in CHANNEL <#{channel_id}>: {question} (Thread ID: {thread_id})")
                if images:
                    logger.info(f"Received {len(images)} images with the query")

                # Query the API with images
                new_thread_id, response = query_endpoint(
                    question, 
                    thread_id,
                    images, 
                    settings.system_message if settings else None,
                    settings.tools if settings else None
                )

                # Update thread context
                if new_thread_id:
                    if thread_id != new_thread_id:
                        logger.info(f"Thread ID changed for channel {channel_id} from {thread_id} to {new_thread_id}")
                    else:
                        logger.debug(f"Thread ID unchanged for channel {channel_id}: {new_thread_id}")
                    self.db_service.update_channel_settings(
                        channel_id,
                        thread_id=new_thread_id
                    )

                # Log the query and response for tracking
                logger.info(f"Channel: {channel_id}, User: {user_id}, Query: {question}, Thread ID: {new_thread_id}, Response: {response}")
                say(response)
        
        except Exception as e:
            logger.error(f"Error handling mention: {e}\n{traceback.format_exc()}")
            raise