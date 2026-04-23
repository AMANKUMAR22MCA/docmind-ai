
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"        # 👈 call it "documents"

    id          = Column(Integer, primary_key=True, index=True)
    filename    = Column(String, nullable=False)
    status      = Column(String, default="processing")   # 👈 default "processing"
    uploaded_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
