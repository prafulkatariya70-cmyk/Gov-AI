from datetime import datetime
import uuid
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
class NotificationQueueItem(Base):
    __tablename__="notification_queue"
    id: Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4)
    source_registry_id: Mapped[uuid.UUID]=mapped_column(ForeignKey("job_source_registry.id",ondelete="CASCADE"),index=True)
    pdf_url: Mapped[str]=mapped_column(Text,unique=True)
    source_page_url: Mapped[str]=mapped_column(Text)
    label: Mapped[str]=mapped_column(String(500))
    status: Mapped[str]=mapped_column(String(30),default="PENDING",index=True)
    attempts: Mapped[int]=mapped_column(Integer,default=0)
    next_attempt_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True,index=True)
    last_error: Mapped[str|None]=mapped_column(Text,nullable=True)
    processed_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=datetime.utcnow)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=datetime.utcnow,onupdate=datetime.utcnow)
