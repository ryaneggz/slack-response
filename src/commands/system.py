from src.utils.logger import logger
from src.config import *

#####################################################################
## System command handler
#####################################################################
def handle_system(event, say, channel_system_messages):
    from src.commands import event_data
    channel_id, _, text = event_data(event)
    
    handled = False
    
    # Check for $set_system command
    if "$set_system" in text.lower():
        system_message = text.split("$set_system", 1)[1].strip()
        if system_message:
            channel_system_messages[channel_id] = system_message
            logger.info(f"System message set for channel {channel_id}: {system_message}")
            say(f"System message set for this channel:\n```\n{system_message}\n```")
        else:
            say("Please provide a system message. Example: $set_system You are a helpful assistant.")
        handled = True

    # Check for $get_system command
    if "$get_system" in text.lower():
        if channel_id in channel_system_messages:
            say(f"Current system message for this channel:\n```\n{channel_system_messages[channel_id]}\n```")
        else:
            say(f"Using default system message:\n```\n{SYSTEM_PROMPT}\n```")
        handled = True

    # Check for $clear_system command
    if "$clear_system" in text.lower():
        if channel_id in channel_system_messages:
            del channel_system_messages[channel_id]
            logger.info(f"System message cleared for channel {channel_id}")
            say("System message has been cleared for this channel. Using default message.")
        else:
            say("No custom system message was set for this channel.")
        handled = True
    
    return handled