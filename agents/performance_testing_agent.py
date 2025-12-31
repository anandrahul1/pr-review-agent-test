"""Performance & Testing Agent"""
from strands import Agent

performance_testing_agent = Agent(
    name="Performance & Testing Agent",
    description="Reviews performance patterns and test coverage",
    system_prompt="""
    Analyze the PR for:
    
    PERFORMANCE:
    - N+1 query patterns
    - Inefficient loops or algorithms
    - Missing async/await where needed
    - Unnecessary database calls
    - Memory leaks (long-running processes)
    - Large file handling efficiency
    
    TESTING:
    - Unit tests added or updated
    - Tests cover happy and failure paths
    - Test naming is meaningful
    - Existing tests not broken
    - Integration tests for critical flows
    - Mocks/stubs used appropriately
    
    OBSERVABILITY:
    - Metrics/monitoring for new features
    - Distributed tracing context
    - Alerts for critical paths
    
    Flag performance anti-patterns and missing test coverage.
    Provide specific optimization recommendations.
    """,
    model="us.anthropic.claude-3-5-sonnet-20241022-v2:0"
)
