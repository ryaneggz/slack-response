from sqlalchemy import Column, String, JSON
from src.infra.database import Base

class ChannelSettings(Base):
    __tablename__ = "channel_settings"

    channel_id = Column(String, primary_key=True, index=True)
    system_message = Column(String, nullable=True)
    tools = Column(JSON, nullable=True)
    thread_id = Column(String, nullable=True) 