import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import deque
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

Base = declarative_base()

class ConversationHistory(Base):
    __tablename__ = 'conversation_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), nullable=False)
    conversation_id = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    metadata_ = Column(JSON, nullable=True)

class UserProfile(Base):
    __tablename__ = 'user_profiles'
    user_id = Column(String(100), primary_key=True)
    preferences = Column(JSON, nullable=False, default=lambda: json.dumps({}))
    history_summary = Column(Text)
    rating = Column(Float, default=0.0)
    total_interactions = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String(100), nullable=False)
    user_id = Column(String(100), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    corrected_answer = Column(Text)
    reward = Column(Float)
    timestamp = Column(DateTime, default=datetime.now)

class DBMemorySystem:
    def __init__(self, db_url: str = "sqlite:///./memory.db", max_short_term: int = 10):
        self.max_short_term = max_short_term
        self.short_term_memory: Dict[str, deque] = {}
        
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def _get_session(self) -> Session:
        return self.Session()

    def add_short_term_memory(self, user_id: str, content: str, role: str = "user", metadata: Dict = None):
        if user_id not in self.short_term_memory:
            self.short_term_memory[user_id] = deque(maxlen=self.max_short_term)
        
        self.short_term_memory[user_id].append({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "content": content,
