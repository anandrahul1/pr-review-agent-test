# PR Review Agentic Solution Architecture

## Executive Summary

Practical multi-agent PR review system using AWS Strands Agents deployed on Amazon Bedrock AgentCore Runtime. Focuses on fast, actionable feedback (2-3 minutes) with specialized domain agents and optional AWS Security Agent integration for static code analysis.

---

## Architecture Overview

### Pattern Selection: **Swarm Pattern**

**Rationale:**
- PR review requires **specialized expertise** across multiple domains
- **Autonomous handoffs** between domain experts mirror real-world code review
- **Shared context** enables agents to build upon each other's findings
- **Fast execution** - each agent completes in 15-45 seconds

### High-Level Flow

```
GitHub PR Commit → Orchestrator Agent → Domain Specialist Agents → Orchestrator → GitHub Comment
```

**Target Review Time:** 2-3 minutes total

---

## Agent Architecture

### 1. Orchestrator Agent (Swarm Coordinator)

**Role:** Entry point, task distribution, final decision aggregation

**Responsibilities:**
- Receives GitHub webhook on PR commit
- Analyzes PR scope and distributes to specialist agents
- Aggregates all agent findings
- Posts review comment to GitHub PR

**Tools:**
- GitHub MCP Server (read PR diff, files, metadata)
- AgentCore Memory (optional - for learning from past reviews)

**Implementation:**
```python
from strands import Agent
from strands.multiagent import Swarm

orchestrator = Agent(
    name="PR Review Orchestrator",
    description="Coordinates PR review across specialized agents",
    tools=[github_tools],
    instructions="""
    1. Fetch PR details from GitHub
    2. Hand off to specialist agents sequentially
    3. Aggregate findings with severity levels
    4. Post review comment to GitHub
    """
)
```

---

### 2. Domain Specialist Agents (4 Core Agents)

#### A. Code Quality & Architecture Agent
**Checklist Sections:** 3 (Code Quality), 4 (Architecture)

**Focus:**
- Code readability and naming
- Magic numbers and complexity
- Layer separation
- Design patterns

**Tools:**
- Basic AST parsing (no heavy analysis)
- Pattern matching for common issues

**Execution Time:** ~30 seconds

---

#### B. Security Agent (Static Analysis Only)
**Checklist Sections:** 6 (Security)

**Focus:**
- Hardcoded secrets/credentials
- SQL injection patterns
- XSS vulnerabilities
- Input validation patterns
- AuthN/AuthZ checks

**Tools:**
- Regex-based secret scanning
- Pattern matching for common vulnerabilities
- **Optional:** AWS Security Agent `CreateDocumentReview` API (static analysis only)

**Execution Time:** ~45 seconds

**AWS Security Agent Integration (Optional):**
```python
@tool
async def run_security_scan(code_diff: str) -> dict:
    # Static code review only - no pentesting
    review = await securityagent_client.create_document_review(
        AgentInstanceId=agent_instance_id,
        DocumentContent=code_diff,
        ReviewType="CODE_REVIEW"
    )
    
    findings = await securityagent_client.batch_get_findings(
        AgentInstanceId=agent_instance_id,
        FindingIds=review['FindingIds']
    )
    
    return {
        "critical": [f for f in findings if f['Severity'] == 'CRITICAL'],
        "high": [f for f in findings if f['Severity'] == 'HIGH']
    }
```

---

#### C. Performance & Testing Agent
**Checklist Sections:** 5 (Performance), 8 (Testing)

**Focus:**
- Obvious N+1 query patterns
- Missing async/await
- Test file presence
- Test naming conventions

**Tools:**
- Pattern matching for common anti-patterns
- File path analysis for test coverage

**Execution Time:** ~30 seconds

---

#### D. Documentation & Compliance Agent
**Checklist Sections:** 11 (Documentation), 14 (Compliance)

**Focus:**
- Breaking changes documented
- API changes reflected in docs
- PII handling patterns
- Migration scripts for DB changes

**Tools:**
- Diff analysis for breaking changes
- Pattern matching for PII

**Execution Time:** ~20 seconds

---

## GitHub Integration Strategy

### Approach: **GitHub Webhook + MCP Server**

**Why This Works:**
- Webhook triggers review on PR events
- MCP provides standardized GitHub API access
- No polling needed

### Implementation

#### 1. GitHub Webhook Configuration
```json
{
  "events": ["pull_request"],
  "config": {
    "url": "https://<agentcore-runtime-url>/webhook",
    "content_type": "json"
  }
}
```

#### 2. AgentCore Runtime Webhook Handler
```python
from fastapi import FastAPI, Request
from strands.multiagent import Swarm

app = FastAPI()

@app.post("/webhook")
async def github_webhook(request: Request):
    payload = await request.json()
    
    if payload['action'] in ['opened', 'synchronize']:
        pr_data = {
            "pr_number": payload['pull_request']['number'],
            "repo": payload['repository']['full_name'],
            "diff_url": payload['pull_request']['diff_url']
        }
        
        # Trigger swarm review
        result = await pr_review_swarm(
            f"Review PR #{pr_data['pr_number']}",
            invocation_state={"pr_data": pr_data}
        )
        
        # Post results to GitHub
        await post_review_comment(pr_data, result)
```

#### 3. GitHub MCP Tools (Minimal Set)
```python
github_tools = [
    "get_pr_diff",           # Fetch code changes
    "get_pr_files",          # List changed files
    "post_review_comment"    # Post findings
]
```

---

## AgentCore Runtime Deployment

### Deployment Architecture

```
┌─────────────────────────────────────────────────┐
│         Amazon Bedrock AgentCore Runtime        │
├─────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────┐   │
│  │   A2A Server (Port 9000)                 │   │
│  │   - Orchestrator Agent                   │   │
│  │   - 4 Specialist Agents (Swarm)          │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │   GitHub MCP Server                      │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
         │
         ▼
    GitHub API
```

### Memory Strategy (Optional)

**Use AgentCore Memory only if:**
- You want to learn from past reviews
- You need to track recurring issues per repository

**Skip Memory if:**
- Each PR review is independent
- You want to minimize costs
- You don't need historical context

**If using Memory:**
```python
# Store only high-value patterns
await memory.store_event({
    "repo": repo_name,
    "issue_type": "N+1 query",
    "frequency": "recurring"
})
```

---

## Deployment Steps

### 1. Project Structure
```
pr-review-agent/
├── agents/
│   ├── orchestrator.py
│   ├── code_quality_agent.py
│   ├── security_agent.py
│   ├── performance_testing_agent.py
│   └── documentation_agent.py
├── tools/
│   └── github_tools.py
├── main.py                    # A2A server entry point
└── requirements.txt
```

### 2. Install Dependencies
```bash
pip install strands-agents[a2a]
pip install bedrock-agentcore
pip install bedrock-agentcore-starter-toolkit
```

### 3. Configure AgentCore
```bash
agentcore configure -e main.py --protocol A2A
```

### 4. Deploy to AgentCore Runtime
```bash
agentcore deploy
```

### 5. Configure GitHub Webhook
Point webhook to AgentCore Runtime URL:
```
https://bedrock-agentcore.us-west-2.amazonaws.com/runtimes/<ARN>/invocations/webhook
```

---

## AWS Security Agent Integration (Optional)

### When to Use

**Use AWS Security Agent if:**
- You need deep static code analysis
- Security is critical (financial, healthcare, etc.)
- You can accept 30-45 second additional latency

**Skip if:**
- Basic pattern matching is sufficient
- Speed is priority (< 2 minute reviews)
- Cost is a concern

### API Operations Used

| Operation | Purpose | Latency |
|-----------|---------|---------|
| `CreateDocumentReview` | Static code security review | ~30-45s |
| `BatchGetFindings` | Retrieve vulnerabilities | ~5s |

### Integration Example

```python
@tool
async def security_scan(code_diff: str) -> dict:
    # Only static analysis - no pentesting
    review = await securityagent.create_document_review(
        AgentInstanceId=agent_instance_id,
        DocumentContent=code_diff,
        ReviewType="CODE_REVIEW"
    )
    
    findings = await securityagent.batch_get_findings(
        FindingIds=review['FindingIds']
    )
    
    return {
        "critical": [f for f in findings if f['Severity'] == 'CRITICAL'],
        "high": [f for f in findings if f['Severity'] == 'HIGH']
    }
```

---

## Response Format

### Agent Output Structure
```json
{
  "agent": "security_agent",
  "status": "FAIL",
  "findings": [
    {
      "severity": "HIGH",
      "category": "SQL Injection",
      "location": "src/api/users.py:45",
      "description": "Unsanitized user input in SQL query",
      "recommendation": "Use parameterized queries"
    }
  ]
}
```

### Final GitHub Comment
```markdown
## 🤖 PR Review Results

**Status:** ⚠️ Issues Found

### Summary
- ✅ Code Quality: PASS
- ❌ Security: FAIL (2 high issues)
- ✅ Performance: PASS
- ⚠️ Documentation: WARNINGS

### Critical Issues
1. **SQL Injection Risk** (src/api/users.py:45)
   - Unsanitized user input in SQL query
   - Fix: Use parameterized queries

2. **Hardcoded Secret** (src/config.py:12)
   - API key found in code
   - Fix: Move to environment variables

### Recommendations
- Add input validation for user endpoints
- Update API documentation for new endpoints

---
*Review completed in 2m 34s*
```

---

## What We Removed (Non-Realistic Items)

### ❌ Removed from Original Design

1. **Penetration Testing**
   - Too slow for PR review (minutes to hours)
   - Belongs in staging/pre-prod, not PR stage
   - Expensive to run on every commit

2. **CI/CD Pipeline Execution**
   - Already handled by GitHub Actions/Jenkins
   - Redundant with existing infrastructure
   - Not agent's responsibility

3. **Heavy Static Analysis Tools**
   - AST parsing, dependency graphs, memory profilers
   - Too slow and complex for PR review
   - Better suited for scheduled scans

4. **Complex Memory Patterns**
   - Made memory optional instead of required
   - Most PRs don't need historical context
   - Reduces cost and complexity

5. **Human-in-the-Loop Notifications**
   - Developers already get GitHub notifications
   - No need for separate Slack/email alerts
   - GitHub comment is sufficient

6. **6 Specialist Agents → 4 Agents**
   - Merged related concerns (Code Quality + Architecture)
   - Merged Performance + Testing
   - Faster execution, simpler orchestration

---

## Cost Optimization

### AgentCore Runtime
- **On-demand pricing:** Pay only for active reviews
- **No memory costs:** Skip AgentCore Memory unless needed
- **Fast execution:** 2-3 minutes = minimal compute cost

### AWS Security Agent (Optional)
- **Preview period:** Currently free
- **Post-preview:** Use only for critical repos
- **Alternative:** Use free open-source tools (Bandit, Semgrep)

**Estimated Cost per PR:**
- AgentCore Runtime: ~$0.05-0.10
- AWS Security Agent (if used): TBD (preview)
- Total: < $0.15 per PR review

---

## Monitoring (Simplified)

### Key Metrics Only
- PR review completion time
- Critical issues found per PR
- Agent failure rate

### Implementation
```python
# Simple CloudWatch metrics
metrics.put_metric_data(
    Namespace='PRReview',
    MetricData=[
        {
            'MetricName': 'ReviewDuration',
            'Value': duration_seconds,
            'Unit': 'Seconds'
        }
    ]
)
```

---

## Security Considerations

### Authentication
- **GitHub:** Personal Access Token (PAT) or GitHub App
- **AgentCore:** OAuth 2.0 via Cognito
- **AWS Security Agent (if used):** IAM role with `SecurityAgentWebAppAPIPolicy`

### Data Privacy
- PR code processed in-memory only (not stored)
- AWS Security Agent: Data never used for model training
- CloudTrail logging for audit compliance

---

## Realistic Expectations

### What This Solution DOES
✅ Fast feedback (2-3 minutes)
✅ Catches common issues (secrets, SQL injection, code quality)
✅ Consistent review standards
✅ Reduces manual review time by 50-70%

### What This Solution DOESN'T Do
❌ Replace human code review
❌ Catch complex business logic errors
❌ Run full test suites
❌ Perform penetration testing
❌ Guarantee zero false positives

---

## Success Criteria

**Deployment Success:**
- PR reviews complete in < 3 minutes
- < 5% agent failure rate
- GitHub comments posted successfully

**Business Success:**
- 50%+ reduction in manual review time
- Catch 80%+ of common security issues
- Developer satisfaction with feedback quality

---

## Conclusion

This architecture provides a **realistic, deployable** PR review solution that:
- ✅ Uses AWS Strands Swarm pattern (4 specialized agents)
- ✅ Integrates with GitHub via webhooks + MCP
- ✅ Deploys on AgentCore Runtime (A2A protocol)
- ✅ Optionally uses AWS Security Agent for deep security analysis
- ✅ Completes reviews in 2-3 minutes
- ✅ Costs < $0.15 per PR review

**Estimated Setup Time:** 1-2 days for initial deployment
**Estimated Review Time:** 2-3 minutes per PR (vs 15-30 minutes manual)
