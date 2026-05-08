"""
Pydantic models for API requests and responses
"""

from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================================
# PHASE 1: Basic API Models
# ============================================================================


class ChatRequest(BaseModel):
    """Request model for /chat endpoint"""

    query: str = Field(..., description="User query to route and process")
    user_id: str = Field(..., description="Unique identifier for the user")
    context: Optional[str] = Field(None, description="Optional conversation context")
    user_tier: Optional[str] = Field(
        default="free", description="User tier: free, pro, enterprise"
    )


class ChatResponse(BaseModel):
    """Response model for /chat endpoint"""

    response: str = Field(..., description="LLM generated response")
    model_used: str = Field(..., description="Model that generated the response")
    latency_ms: float = Field(..., description="Request latency in milliseconds")
    routing_metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Routing decision metadata"
    )


# ============================================================================
# PHASE 2: Feature Extraction Models
# ============================================================================


class QueryFeatures(BaseModel):
    """Extracted features from a query"""

    # Basic metrics
    token_count: int
    query_length: int
    word_count: int
    sentence_count: int

    # Domain flags
    is_coding: bool
    is_analytical: bool
    is_creative: bool
    has_code_block: bool

    # Embeddings (stored separately for efficiency)
    embedding_id: Optional[str] = None


# ============================================================================
# PHASE 3: Routing Models
# ============================================================================


class RoutingDecision(BaseModel):
    """Production-grade routing decision with full observability"""

    # Core decision
    model_selected: str = Field(..., description="Selected model name")
    routing_method: str = Field(
        ..., description="Routing method: rule_based, ml_scoring, rag_based, fallback"
    )
    complexity_tier: str = Field(
        ..., description="Query complexity tier: low, medium, high"
    )
    complexity_score: float = Field(..., ge=0.0, le=1.0)
    
    # Explanation
    routing_reason: str = Field(
        ..., description="Human-readable reason for selection"
    )
    cost_estimate_usd: float = Field(..., ge=0.0)
    
    # Fallback tracking
    fallback_used: bool = False
    fallback_reason: Optional[str] = None
    
    # Candidate analysis for explainability
    candidates_scored: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="All candidates considered with scores"
    )
    
    # Performance metadata
    routing_overhead_ms: float = Field(default=0.0)
    
    # Legacy fields for backward compatibility
    selected_model: Optional[str] = None
    reason: Optional[str] = None
    confidence: Optional[float] = None
    alternatives: Optional[List[Dict[str, Any]]] = None
    fallback: Optional[bool] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        # Map new fields to legacy fields for backward compatibility
        if self.selected_model is None:
            self.selected_model = self.model_selected
        if self.reason is None:
            self.reason = self.routing_reason
        if self.confidence is None:
            self.confidence = self.complexity_score
        if self.fallback is None:
            self.fallback = self.fallback_used


# ============================================================================
# PHASE 4: Data Collection Models
# ============================================================================


class RoutingLog(BaseModel):
    """Log entry for a routing decision"""

    id: Optional[int] = None
    query: str
    user_id: str
    features: Dict[str, Any]
    model_used: str
    latency_ms: float
    cost_estimate: float
    success: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class FeedbackRequest(BaseModel):
    """User feedback on a response"""

    request_id: str
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None


# ============================================================================
# PHASE 5: ML Models
# ============================================================================


class ComplexityPrediction(BaseModel):
    """ML prediction for query complexity"""

    complexity: str  # simple, medium, complex
    domain: str  # code, analysis, creative, chat
    confidence: float


# ============================================================================
# PHASE 6: RAG Models
# ============================================================================


class SimilarQuery(BaseModel):
    """Similar historical query"""

    query: str
    model_used: str
    success_rate: float
    avg_latency_ms: float
    similarity_score: float


# ============================================================================
# PHASE 7: Decision Engine Models
# ============================================================================


class ModelCandidate(BaseModel):
    """A candidate model for routing"""

    model_name: str
    quality_score: float
    cost_score: float
    latency_score: float
    overall_score: float
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# PHASE 8: Cache Models
# ============================================================================


class CacheEntry(BaseModel):
    """Cached response entry"""

    query_hash: str
    response: str
    model_used: str
    timestamp: datetime
    hit_count: int = 0


# ============================================================================
# PHASE 9: Metrics Models
# ============================================================================


class HealthCheck(BaseModel):
    """Health check response"""

    status: str
    version: str
    timestamp: datetime
    services: Dict[str, str]


class MetricsResponse(BaseModel):
    """Metrics endpoint response"""

    total_requests: int
    cache_hit_rate: float
    avg_latency_ms: float
    model_distribution: Dict[str, int]
    error_rate: float
