"""
Database models using SQLAlchemy
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# ============================================================================
# PHASE 4: Data Collection Tables
# ============================================================================


class RoutingLogDB(Base):
    """Database table for routing logs"""

    __tablename__ = "routing_logs"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, nullable=False)
    user_id = Column(String(255), nullable=False, index=True)
    features = Column(JSON, nullable=False)
    model_used = Column(String(100), nullable=False, index=True)
    latency_ms = Column(Float, nullable=False)
    cost_estimate = Column(Float, nullable=False)
    success = Column(Boolean, nullable=False, default=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    embedding = Column(JSON, nullable=True)  # Store embedding vector


class FeedbackDB(Base):
    """Database table for user feedback"""

    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(255), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class ModelPerformanceDB(Base):
    """Table tracking model performance metrics"""

    __tablename__ = "model_performance"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False, index=True)
    total_requests = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    total_latency_ms = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    avg_rating = Column(Float, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
