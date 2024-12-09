from src.utils.logger import logger
from src.services.db_service import DatabaseService
#####################################################################
## Thread command handler
#####################################################################
def handle_thread(event, say, db_service= DatabaseService):
    from src.commands import event_data
    channel_id, _, text = event_data(event)
    
    handled = False
    
    # Check if the user wants to reset the thread
    if "$reset" in text.lower():
        if db_service.get_channel_settings(channel_id):
            db_service.update_channel_settings(channel_id, thread_id=None)
            logger.info(f"Thread reset for channel: {channel_id}")
            say(f"Thread context has been reset for channel <#{channel_id}>.")
            handled = True
        else:
            say(f"No thread context was set for channel <#{channel_id}>.")
            handled = True
    return handled