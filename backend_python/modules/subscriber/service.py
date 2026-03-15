from sqlalchemy.orm import Session
from .models import Subscriber, SubscriberInput


class SubscriberService:
    def __init__(self, db: Session):
        self.db = db

    def subscribe_user(self, input: SubscriberInput) -> Subscriber:
        subscriber = Subscriber(
            email=input.email, 
            level=input.level,
            language=input.language
        )
        self.db.add(subscriber)
        self.db.commit()
        self.db.refresh(subscriber)
        return subscriber
