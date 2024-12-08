from sqlalchemy.orm import Session
from src.models.channel_settings import ChannelSettings

class DatabaseService:
    def __init__(self, db: Session):
        self.db = db

    def get_channel_settings(self, channel_id: str) -> ChannelSettings:
        return self.db.query(ChannelSettings).filter(ChannelSettings.channel_id == channel_id).first()

    def update_channel_settings(self, channel_id: str, **kwargs):
        settings = self.get_channel_settings(channel_id)
        if not settings:
            settings = ChannelSettings(channel_id=channel_id)
            self.db.add(settings)
        
        for key, value in kwargs.items():
            setattr(settings, key, value)
        
        self.db.commit()
        return settings

    def delete_channel_settings(self, channel_id: str):
        settings = self.get_channel_settings(channel_id)
        if settings:
            self.db.delete(settings)
            self.db.commit() 