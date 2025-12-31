"""Orchestrator Agent - Swarm Coordinator"""
from strands import Agent
from strands.multiagent import Swarm
from tools.github_tools import get_pr_details, get_pr_diff, get_pr_files, post_review_comment
from tools.jira_tools import get_jira_ticket
from agents.code_quality_agent import code_quality_agent
from agents.security_agent import security_agent
from agents.performance_testing_agent import performance_testing_agent
from agents.documentation_compliance_agent import documentation_compliance_agent
import re

orchestrator_agent = Agent(
    name="PR Review Orchestrator",
    description="Coordinates PR review across specialized agents and aggregates findings",
    tools=[get_pr_details, get_pr_diff, get_pr_files, get_jira_ticket, post_review_comment],
    system_prompt="""
    You are the PR Review Orchestrator. Follow this workflow:
    
    1. PRE-FLIGHT CHECKS:
       - Fetch PR details (title, description, files)
       - Extract Jira ticket ID from PR title/branch (e.g., PROJ-123)
       - Fetch Jira ticket details
       - Validate PR context and scope
    
    2. DISTRIBUTE TO SPECIALISTS:
       Hand off to each specialist agent with the PR diff:
       - Code Quality & Architecture Agent
       - Security Agent (runs both pattern + AWS scans)
       - Performance & Testing Agent
       - Documentation & Compliance Agent
    
    3. AGGREGATE FINDINGS:
       Collect all findings and categorize by severity:
       - CRITICAL: Blocks approval
       - HIGH: Should be fixed
       - MEDIUM: Recommended fixes
       - LOW: Nice-to-have improvements
    
    4. GENERATE REVIEW:
       Create comprehensive review comment with:
       - Jira ticket context
       - Summary by agent (PASS/FAIL/WARNINGS)
       - Critical issues blocking approval
       - Recommendations
       - Human decision prompt
    
    5. POST TO GITHUB:
       Post the review comment to the PR
    
    Be thorough but concise. Focus on actionable feedback.
    """,
    model="us.anthropic.claude-3-5-sonnet-20241022-v2:0"
)

# Create the swarm
pr_review_swarm = Swarm(
    nodes=[
        orchestrator_agent,
        code_quality_agent,
        security_agent,
        performance_testing_agent,
        documentation_compliance_agent
    ],
    entry_point=orchestrator_agent
)

async def review_pr(repo: str, pr_number: int) -> dict:
    """Main entry point for PR review"""
    result = await pr_review_swarm.run(
        f"Review PR #{pr_number} in {repo}",
        invocation_state={
            "repo": repo,
            "pr_number": pr_number
        }
    )
    return result
