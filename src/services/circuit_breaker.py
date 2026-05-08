"""
Circuit breaker for model endpoints - resilience pattern
Tracks model failures and temporarily blocks requests to failing models
"""

import time
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"          # normal operation
    OPEN = "open"              # failing, reject requests
    HALF_OPEN = "half_open"    # testing recovery


class CircuitBreaker:
    """
    Circuit breaker pattern implementation per model
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests are rejected
    - HALF_OPEN: Testing if service recovered, allow one attempt
    """

    def __init__(
        self,
        model_name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        success_threshold: int = 2,
    ):
        """
        Initialize circuit breaker
        
        Args:
            model_name: Name of the model this breaker protects
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before trying recovery
            success_threshold: Consecutive successes needed to close circuit
        """
        self.model_name = model_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: float = 0
        self.state = CircuitState.CLOSED

    def record_success(self):
        """Record a successful model call"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self._transition(CircuitState.CLOSED)
                return
        
        # Reset failure count on success
        self.failure_count = 0
        
        logger.debug(
            "circuit_breaker.success_recorded",
            model=self.model_name,
            state=self.state.value,
            failure_count=self.failure_count,
        )

    def record_failure(self):
        """Record a failed model call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        logger.debug(
            "circuit_breaker.failure_recorded",
            model=self.model_name,
            failure_count=self.failure_count,
            threshold=self.failure_threshold,
        )
        
        if self.failure_count >= self.failure_threshold:
            self._transition(CircuitState.OPEN)

    def can_attempt(self) -> bool:
        """
        Check if a request can attempt to use this model
        
        Returns:
            True if request should be attempted, False if circuit is open
        """
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has elapsed
            elapsed = time.time() - self.last_failure_time
            if elapsed > self.recovery_timeout:
                logger.info(
                    "circuit_breaker.attempting_recovery",
                    model=self.model_name,
                    elapsed_seconds=int(elapsed),
                )
                self._transition(CircuitState.HALF_OPEN)
                return True
            return False
        
        # HALF_OPEN: allow attempt
        return True

    def _transition(self, new_state: CircuitState):
        """Transition to a new state and log it"""
        old_state = self.state
        self.state = new_state
        self.success_count = 0
        
        logger.warning(
            "circuit_breaker.state_change",
            model=self.model_name,
            old_state=old_state.value,
            new_state=new_state.value,
            failure_count=self.failure_count,
        )

    def get_state(self) -> str:
        """Get current circuit state"""
        return self.state.value

    def reset(self):
        """Manually reset the circuit breaker (for testing)"""
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        self.state = CircuitState.CLOSED


class CircuitBreakerRegistry:
    """Registry of circuit breakers for all models"""

    def __init__(self):
        self._breakers: dict[str, CircuitBreaker] = {}

    def get_breaker(
        self,
        model_name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
    ) -> CircuitBreaker:
        """Get or create a circuit breaker for a model"""
        if model_name not in self._breakers:
            self._breakers[model_name] = CircuitBreaker(
                model_name=model_name,
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
            )
        return self._breakers[model_name]

    def get_all_states(self) -> dict[str, str]:
        """Get state of all circuit breakers"""
        return {
            name: breaker.get_state() for name, breaker in self._breakers.items()
        }


# Global registry
circuit_breaker_registry = CircuitBreakerRegistry()
