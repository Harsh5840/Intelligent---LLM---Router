"""
Load testing for LLM Router with Locust
Tests routing decisions, latency, and observability under load
"""

import random
from locust import HttpUser, task, between


SAMPLE_PROMPTS = [
    # Low complexity — should route to cheap model
    ("What is 2+2?", "low"),
    ("Define recursion", "low"),
    ("What is REST?", "low"),
    ("Explain what JSON is", "low"),
    ("How many days are in a week?", "low"),
    
    # Medium complexity
    ("Compare SQL and NoSQL databases", "medium"),
    ("Explain microservices architecture", "medium"),
    ("What is Docker?", "medium"),
    
    # High complexity — should route to expensive model  
    ("Write a Python implementation of a distributed rate limiter using Redis with sliding window algorithm", "high"),
    ("Explain the CAP theorem and design a system that prioritizes AP over CP", "high"),
    ("Design a fault-tolerant distributed consensus algorithm", "high"),
    
    # Coding — should trigger coding-intent routing
    ("Debug this code: def fib(n): return fib(n-1) + fib(n-2)", "coding"),
    ("Optimize this SQL query", "coding"),
    ("Write a binary search implementation", "coding"),
]


class RouterUser(HttpUser):
    """Simulated user accessing the LLM router"""
    
    wait_time = between(0.5, 2.0)
    
    @task(5)
    def send_simple_prompt(self):
        """Send low-complexity prompts (most common)"""
        prompt, tier = random.choice(
            [(p, t) for p, t in SAMPLE_PROMPTS if t == "low"]
        )
        
        with self.client.post(
            "/api/v1/chat",
            json={
                "query": prompt,
                "user_id": f"user_{random.randint(1, 1000)}",
                "user_tier": "free",
            },
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                data = response.json()
                # Verify routing metadata exists
                if "routing_metadata" not in data:
                    response.failure("Missing routing_metadata")
                elif data["routing_metadata"] is None:
                    response.failure("routing_metadata is null")
                else:
                    response.success()
            elif response.status_code == 503:
                response.failure("Service unavailable")
            else:
                response.failure(f"Unexpected status: {response.status_code}")
    
    @task(2)
    def send_medium_prompt(self):
        """Send medium-complexity prompts"""
        prompt, tier = random.choice(
            [(p, t) for p, t in SAMPLE_PROMPTS if t == "medium"]
        )
        
        self.client.post(
            "/api/v1/chat",
            json={
                "query": prompt,
                "user_id": f"user_{random.randint(1, 1000)}",
                "user_tier": "standard",
            },
        )
    
    @task(1)
    def send_complex_prompt(self):
        """Send high-complexity prompts (premium routing)"""
        prompt, _ = random.choice(
            [(p, t) for p, t in SAMPLE_PROMPTS if t == "high"]
        )
        
        self.client.post(
            "/api/v1/chat",
            json={
                "query": prompt,
                "user_id": f"user_{random.randint(1, 1000)}",
                "user_tier": "premium",
            },
        )
    
    @task(1)
    def send_coding_prompt(self):
        """Send coding-related prompts"""
        prompt, _ = random.choice(
            [(p, t) for p, t in SAMPLE_PROMPTS if t == "coding"]
        )
        
        self.client.post(
            "/api/v1/chat",
            json={
                "query": prompt,
                "user_id": f"user_{random.randint(1, 1000)}",
                "user_tier": "pro",
            },
        )
    
    @task(1)
    def check_health(self):
        """Check health endpoint"""
        self.client.get("/api/v1/health")
    
    @task(1)  
    def check_metrics(self):
        """Check Prometheus metrics endpoint"""
        response = self.client.get("/metrics", name="/metrics")
        if response.status_code == 200:
            # Verify it's Prometheus format
            if "llm_routing_decisions_total" not in response.text:
                response.failure("Missing LLM routing metrics")


class AdminUser(HttpUser):
    """Admin user checking observability"""
    
    wait_time = between(2.0, 5.0)
    
    @task
    def check_stats(self):
        """Check aggregated stats endpoint"""
        self.client.get("/api/v1/stats")
    
    @task
    def check_metrics(self):
        """Check Prometheus metrics"""
        self.client.get("/metrics")
