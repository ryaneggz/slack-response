from src.utils.logger import logger
from src.commands.thread import handle_thread
from src.commands.tool import handle_tools
from src.commands.system import handle_system
from src.commands.help import handle_help
from src.commands.document import handle_documents

#####################################################################
## Event data
#####################################################################
def event_data(event):
    channel_id = event["channel"]
    user_id = event["user"]
    text = event["text"]
    return channel_id, user_id, text

#####################################################################
## Command handlers
#####################################################################
def handle_command(event, say, channel_tools, channel_system_messages, conversation_threads):
    handled = False
    try:
        # Check help command first
        handled = handle_help(event, say)
        if handled:
            return handled
            
        handled = handle_thread(event, say, conversation_threads)
        if handled:
            return handled
        
        handled = handle_tools(event, say, channel_tools)
        if handled:
            return handled
        
        handled = handle_system(event, say, channel_system_messages)
        if handled:
            return handled
            
        handled = handle_documents(event, say)
        if handled:
            return handled
            
    except Exception as e:
        logger.error(f"Error handling command: {e}")
        say(f"An error occurred while processing your command. {e}")
        handled = True
    return handled