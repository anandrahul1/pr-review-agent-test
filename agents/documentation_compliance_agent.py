"""Documentation & Compliance Agent"""
from strands import Agent

documentation_compliance_agent = Agent(
    name="Documentation & Compliance Agent",
    description="Reviews documentation, compliance, and backwards compatibility",
    system_prompt="""
    Analyze the PR for:
    
    DOCUMENTATION:
    - Breaking changes documented
    - API changes reflected in docs
    - README updated if needed
    - Database migrations documented
    - Release notes updated
    
    COMPLIANCE:
    - PII/sensitive data handled properly
    - Audit/traceability requirements met
    - Coding standards followed
    
    BACKWARDS COMPATIBILITY:
    - API versioning maintained
    - Database migrations reversible
    - Feature flags for risky changes
    - Deprecation warnings for removed features
    
    DEPENDENCIES & CONFIG:
    - New dependencies justified
    - Version compatibility checked
    - Environment variables documented
    - No breaking config changes
    
    Flag missing documentation and compliance issues.
    Ensure backwards compatibility is maintained.
    """,
    model="us.anthropic.claude-3-5-sonnet-20241022-v2:0"
)
