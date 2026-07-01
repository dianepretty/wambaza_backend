from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, default="publisher")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    hashed_password = Column(String, nullable=False)
    must_change_password = Column(Boolean, default=True)
    reset_otp_hash = Column(String, nullable=True)
    reset_otp_expires_at = Column(DateTime, nullable=True)

    articles = relationship("Article", back_populates="publisher")


class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True)
    title_en = Column(String, nullable=False)
    title_kin = Column(String, nullable=True)
    title_lug = Column(String, nullable=True)
    title_sw = Column(String, nullable=True)
    content_en = Column(Text, nullable=False)
    content_kin = Column(Text, nullable=True)
    content_lug = Column(Text, nullable=True)
    content_sw = Column(Text, nullable=True)
    cover_image_url = Column(String, nullable=True)
    status = Column(String, default="draft")
    publisher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    publisher = relationship("User", back_populates="articles")
