import os
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, create_engine, Text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./appointments.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)
    reason = Column(String, default="General consultation")
    status = Column(String, default="confirmed")  # confirmed | cancelled
    created_at = Column(DateTime, default=datetime.utcnow)


class CallSummary(Base):
    __tablename__ = "call_summaries"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(String, index=True, nullable=False)
    summary = Column(Text, nullable=False)
    appointments = Column(Text, default="[]")
    preferences = Column(Text, default="")
    phone_number = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


def create_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
