from sqlalchemy.orm import Session
from src.models.channel_settings import ChannelSettings
from src.utils.logger import logger

class DatabaseService:
    """Service class for handling database operations related to channel settings."""
    
    def __init__(self, db: Session):
        """
        Initialize the database service.
        
        Args:
            db (Session): SQLAlchemy database session
        """
        self.db = db

    def get_channel_settings(self, channel_id: str) -> ChannelSettings:
        """
        Retrieve settings for a specific channel.
        
        Args:
            channel_id (str): Slack channel identifier
            
        Returns:
            ChannelSettings: Channel settings object or None if not found
        """
        logger.debug(f"Retrieving settings for channel: {channel_id}")
        return self.db.query(ChannelSettings).filter(ChannelSettings.channel_id == channel_id).first()

    def update_channel_settings(self, channel_id: str, **kwargs):
        """
        Update or create channel settings.
        
        Args:
            channel_id (str): Slack channel identifier
            **kwargs: Key-value pairs of settings to update
            
        Returns:
            ChannelSettings: Updated channel settings object
        """
        settings = self.get_channel_settings(channel_id)
        if not settings:
            logger.info(f"Creating new settings for channel: {channel_id}")
            settings = ChannelSettings(channel_id=channel_id)
            self.db.add(settings)
        else:
            logger.debug(f"Updating existing settings for channel: {channel_id}")
        
        for key, value in kwargs.items():
            logger.debug(f"Setting {key}={value} for channel: {channel_id}")
            setattr(settings, key, value)
        
        self.db.commit()
        return settings

    def delete_channel_settings(self, channel_id: str):
        """
        Delete settings for a specific channel.
        
        Args:
            channel_id (str): Slack channel identifier
        """
        settings = self.get_channel_settings(channel_id)
        if settings:
            logger.info(f"Deleting settings for channel: {channel_id}")
            self.db.delete(settings)
            self.db.commit()
        else:
            logger.debug(f"No settings found to delete for channel: {channel_id}") 