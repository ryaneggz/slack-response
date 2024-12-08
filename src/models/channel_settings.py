from sqlalchemy import Column, String, JSON
from src.infra.database import Base

class ChannelSettings(Base):
    """
    Database model for storing channel-specific settings.
    
    Attributes:
        channel_id (str): Slack channel identifier (primary key)
        system_message (str): Custom system message for the channel
        tools (JSON): List of enabled tools for the channel
        thread_id (str): Current conversation thread ID
    """
    __tablename__ = "channel_settings"

    channel_id = Column(String, primary_key=True, index=True)
    system_message = Column(String, nullable=True)
    tools = Column(JSON, nullable=True)
    thread_id = Column(String, nullable=True) 