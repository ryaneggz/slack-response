from src.commands import event_data, handle_command
from src.utils.api import query_endpoint
from src.utils.logger import logger
from src.utils.process import process_images
from src.infra.database import get_db
from src.services.db_service import DatabaseService

class MentionController:
    def __init__(self):
        self.db = next(get_db())
        self.db_service = DatabaseService(self.db)

    def handle_mention(self, event, say):
        channel_id, user_id, text = event_data(event)
        
        # Get channel settings
        settings = self.db_service.get_channel_settings(channel_id)
        
        # Extract images from the event
        images = process_images(event)
        
        # Handle commands first
        handled = handle_command(
            event, 
            say, 
            self.db_service
        )
        
        if not handled:
            question = text.split(maxsplit=1)[-1] if len(text.split()) > 1 else "What can I help you with?"
            
            thread_id = settings.thread_id if settings else None
            
            new_thread_id, response = query_endpoint(
                question, 
                thread_id, 
                channel_id, 
                images,
                settings.system_message if settings else None,
                settings.tools if settings else None
            )
            
            if new_thread_id:
                self.db_service.update_channel_settings(
                    channel_id,
                    thread_id=new_thread_id
                )
            
            say(response)