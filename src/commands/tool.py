import requests

from src.services.db_service import DatabaseService
from src.config import *
from src.utils.logger import logger

#####################################################################
## Tool command handler
#####################################################################
def handle_tools(event, say, db_service: DatabaseService):
    from src.commands import event_data
    channel_id, _, text = event_data(event)
    
    handled = False
    
    # Check if user wants to see available tools
    if "$list_tools" in text.lower():
        response = requests.get(TOOLS_ENDPOINT, headers=HEADERS, auth=(APP_USERNAME, APP_PASSWORD))
        if response.status_code == 200:
            tools = response.json().get("tools", [])
            # Extract tool names from the dictionary objects
            tool_names = [tool.get("id", str(tool)) for tool in tools]
            tools_list = "\n- ".join(tool_names)
            say(f"Available tools:\n- {tools_list}")
        else:
            say(f"Error fetching tools: {response.status_code}")
        handled = True
    
    # Check for $get_tools command
    if "$get_tools" in text.lower():
        if db_service.get_channel_settings(channel_id):
            tools_list = "\n- ".join(db_service.get_channel_settings(channel_id).tools)
            say(f"Currently selected tools for this channel:\n- {tools_list}")
        else:
            say("No tools are currently set for this channel.")
        handled = True
    
    # Check for $set_tools command
    if "$set_tools" in text.lower():
        tools_input = text.split("$set_tools", 1)[1].strip()
        if tools_input:
            tools_list = [tool.strip() for tool in tools_input.split(",")]
            db_service.update_channel_settings(channel_id, tools=tools_list)
            formatted_tools = "\n- ".join(tools_list)
            logger.info(f"Tools set for channel {channel_id}: {formatted_tools}")
            say(f"Tools set for this channel:\n- {formatted_tools}")
        else:
            say("Please provide tools separated by commas. Example: $settools tool1, tool2, tool3")
        handled = True
    
    # Check for $cleartools command
    if "$clear_tools" in text.lower():
        if db_service.get_channel_settings(channel_id):
            db_service.update_channel_settings(channel_id, tools=None)
            logger.info(f"Tools cleared for channel {channel_id}")
            say("Tools have been cleared for this channel.")
        else:
            say("No tools were set for this channel.")
        handled = True
    
    return handled