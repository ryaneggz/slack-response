from src.commands import event_data
from src.utils.logger import logger

#####################################################################
## Thread command handler
#####################################################################
def handle_thread(event, say, conversation_threads):
    channel_id, _, text = event_data(event)
    
    handled = False
    
    # Check if the user wants to reset the thread
    if "$reset" in text.lower():
        if channel_id in conversation_threads:
            del conversation_threads[channel_id]
            logger.info(f"Thread reset for channel: {channel_id}")
            say(f"Thread context has been reset for channel <#{channel_id}>.")
            handled = True
        else:
            say(f"No thread context was set for channel <#{channel_id}>.")
            handled = True
    return handled