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
       - Extract Jira ticket ID from PR title/branch (e.g., PROJ-123, TICKET-456)
       - Validate Jira ticket format (PROJECT-NUMBER pattern)
       - Fetch Jira ticket details if valid ID found
       - Validate PR context and scope
    
    2. DISTRIBUTE TO SPECIALISTS:
       Hand off to each specialist agent with the PR diff:
       - Code Quality & Architecture Agent
       - Security Agent (runs both pattern + AWS scans)
       - Performance & Testing Agent
       - Documentation & Compliance Agent
    
    3. AGGREGATE FINDINGS:
       Collect all findings and categorize by severity:
       - CRITICAL: Blocks approval (security, breaking changes)
       - HIGH: Should be fixed (performance, architecture)
       - MEDIUM: Recommended fixes (code quality)
       - LOW: Nice-to-have improvements (documentation)
       
       For each finding, include:
       - Specific line numbers from the diff
       - Exact code snippet causing the issue
       - Before/After code examples for CRITICAL issues
    
    4. GENERATE REVIEW:
       Create comprehensive review comment with:
       
       **JIRA VALIDATION:**
       - ✅ Jira ticket found: [PROJ-123] Title
       - ❌ No Jira ticket reference found in PR title or description
       
       **SUMMARY BY AGENT:**
       - Code Quality: PASS/FAIL/WARNINGS
       - Security: PASS/FAIL/WARNINGS
       - Performance: PASS/FAIL/WARNINGS
       - Documentation: PASS/FAIL/WARNINGS
       
       **CRITICAL ISSUES (with line numbers and code examples):**
       For each CRITICAL issue:
       ```
       ### 🚨 [Issue Name] (Line X)
       
       **Current Code:**
       ```language
       [exact problematic code from diff]
       ```
       
       **Fixed Code:**
       ```language
       [corrected version]
       ```
       
       **Why:** [Brief explanation]
       ```
       
       **HIGH/MEDIUM ISSUES (with line numbers):**
       - Line X: [Issue description]
       - Line Y: [Issue description]
       
       **RECOMMENDATIONS:**
       - Actionable next steps
       
       **HUMAN DECISION:**
       - Approve / Request Changes / Comment
    
    5. POST TO GITHUB:
       Post the formatted review comment to the PR
    
    IMPORTANT FORMATTING RULES:
    - Always include line numbers for issues
    - Show code examples for CRITICAL issues only
    - Keep code snippets concise (5-10 lines max)
    - Use proper markdown formatting
    - Be thorough but concise
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
