import requests

from src.config import *
from src.utils.logger import logger

def event_data(event):
    channel_id = event["channel"]
    user_id = event["user"]
    text = event["text"]
    return channel_id, user_id, text

def handle_tools(event, say, channel_tools):
    channel_id, _, text = event_data(event)
    
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
        return
    
    # Check for $get_tools command
    if "$get_tools" in text.lower():
        if channel_id in channel_tools and channel_tools[channel_id]:
            tools_list = "\n- ".join(channel_tools[channel_id])
            say(f"Currently selected tools for this channel:\n- {tools_list}")
        else:
            say("No tools are currently set for this channel.")
        return
    
    # Check for $set_tools command
    if "$set_tools" in text.lower():
        tools_input = text.split("$set_tools", 1)[1].strip()
        if tools_input:
            tools_list = [tool.strip() for tool in tools_input.split(",")]
            channel_tools[channel_id] = tools_list  # Store the tools for this channel
            formatted_tools = "\n- ".join(tools_list)
            logger.info(f"Tools set for channel {channel_id}: {formatted_tools}")
            say(f"Tools set for this channel:\n- {formatted_tools}")
        else:
            say("Please provide tools separated by commas. Example: $settools tool1, tool2, tool3")
        return
    
    # Check for $cleartools command
    if "$clear_tools" in text.lower():
        if channel_id in channel_tools:
            del channel_tools[channel_id]
            logger.info(f"Tools cleared for channel {channel_id}")
            say("Tools have been cleared for this channel.")
        else:
            say("No tools were set for this channel.")
        return
    
def handle_system(event, say, channel_system_messages):
    channel_id, _, text = event_data(event)
    
    # Check for $set_system command
    if "$set_system" in text.lower():
        system_message = text.split("$set_system", 1)[1].strip()
        if system_message:
            channel_system_messages[channel_id] = system_message
            logger.info(f"System message set for channel {channel_id}: {system_message}")
            say(f"System message set for this channel:\n```\n{system_message}\n```")
        else:
            say("Please provide a system message. Example: $set_system You are a helpful assistant.")
        return

    # Check for $get_system command
    if "$get_system" in text.lower():
        if channel_id in channel_system_messages:
            say(f"Current system message for this channel:\n```\n{channel_system_messages[channel_id]}\n```")
        else:
            say(f"Using default system message:\n```\n{SYSTEM_PROMPT}\n```")
        return

    # Check for $clear_system command
    if "$clear_system" in text.lower():
        if channel_id in channel_system_messages:
            del channel_system_messages[channel_id]
            logger.info(f"System message cleared for channel {channel_id}")
            say("System message has been cleared for this channel. Using default message.")
        else:
            say("No custom system message was set for this channel.")
        return
    
def handle_thread(event, say, conversation_threads):
    channel_id, _, text = event_data(event)
    
    # Check if the user wants to reset the thread
    if "$reset" in text.lower():
        if channel_id in conversation_threads:
            del conversation_threads[channel_id]
        logger.info(f"Thread reset for channel: {channel_id}")
        say(f"Thread context has been reset for channel <#{channel_id}>.")
        return

def handle_command(event, say, channel_tools, channel_system_messages, conversation_threads):
    handle_thread(event, say, conversation_threads)
    handle_tools(event, say, channel_tools)
    handle_system(event, say, channel_system_messages)
    