from loguru import logger


def handle_help(event, say):
    from src.commands import event_data
    _, _, text = event_data(event)
    
    logger.info(f"Help command received from {event['user']} in {event['channel']}")
    
    if "$help" in text.lower():
        help_text = """
*Available Commands:*

*Thread Management:*
• `$reset` - Reset the conversation thread for the current channel

*Tool Management:*
• `$list_tools` - Show all available tools
• `$get_tools` - Show currently selected tools for this channel
• `$set_tools tool1,tool2` - Set specific tools for this channel
• `$clear_tools` - Clear all tools for this channel

*System Message Management:*
• `$get_system` - Show current system message for this channel
• `$set_system <message>` - Set a custom system message for this channel
• `$clear_system` - Reset to default system message

*Document Management:*
• `$add_doc <text>` - Add a new document with the provided text
• `$upload_doc` - Upload one or more files as documents (attach files with command)
• `$list_docs` - Show all available documents
• `$get_doc <id>` - Get a specific document by ID
• `$delete_doc <id1,id2,...>` - Delete one or more documents by ID

*Help:*
• `$help` - Show this help message

For more detailed information about a specific command, type `$help <command>` (e.g., `$help set_tools`)
"""
        say(help_text)
        return True
        
    return False 