from src.infra.database import get_db
from src.services.db_service import DatabaseService
from src.utils.logger import logger
from src.commands import event_data, handle_command
from src.utils.process import process_images
from src.utils.api import query_endpoint

class MentionController:
    """Controller for handling bot mentions and managing channel settings."""
    
    def __init__(self):
        """Initialize the controller with database connection."""
        logger.info("Initializing MentionController with database connection")
        self.db = next(get_db())
        self.db_service = DatabaseService(self.db)

    def handle_mention(self, event, say):
        """
        Handle mentions of the bot in Slack channels.
        
        Args:
            event: Slack event object
            say: Slack say function for responding
        """
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
            question = text.split(maxsplit=1)[-1] if len(text.split()) > 1 else "What can I help you with?"
            
            thread_id = settings.thread_id if settings else None
            logger.debug(f"Using thread_id: {thread_id}")
            
            new_thread_id, response = query_endpoint(
                question, 
                thread_id, 
                channel_id, 
                images,
                settings.system_message if settings else None,
                settings.tools if settings else None
            )
            
            if new_thread_id:
                logger.debug(f"Updating thread_id to: {new_thread_id}")
                self.db_service.update_channel_settings(
                    channel_id,
                    thread_id=new_thread_id
                )
            
            say(response)