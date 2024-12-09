from src.services.db_service import DatabaseService
from src.utils.logger import logger
from src.config import *

#####################################################################
## System command handler
#####################################################################
def handle_system(event, say, db_service: DatabaseService):
    from src.commands import event_data
    channel_id, _, text = event_data(event)
    
    handled = False
    
    # Check for $set_system command
    if "$set_system" in text.lower():
        system_message = text.split("$set_system", 1)[1].strip()
        if system_message:
            db_service.update_channel_settings(channel_id, system_message=system_message)
            logger.info(f"System message set for channel {channel_id}: {system_message}")
            say(f"System message set for this channel:\n```\n{system_message}\n```")
        else:
            say("Please provide a system message. Example: $set_system You are a helpful assistant.")
        handled = True

    # Check for $get_system command
    if "$get_system" in text.lower():
        if db_service.get_channel_settings(channel_id):
            say(f"Current system message for this channel:\n```\n{db_service.get_channel_settings(channel_id).system_message}\n```")
        else:
            say(f"Using default system message:\n```\n{SYSTEM_PROMPT}\n```")
        handled = True

    # Check for $clear_system command
    if "$clear_system" in text.lower():
        if db_service.get_channel_settings(channel_id):
            db_service.update_channel_settings(channel_id, system_message=None)
            logger.info(f"System message cleared for channel {channel_id}")
            say("System message has been cleared for this channel. Using default message.")
        else:
            say("No custom system message was set for this channel.")
        handled = True
    
    return handled