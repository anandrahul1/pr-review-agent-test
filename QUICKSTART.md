# Quick Start Guide

## Prerequisites

1. **AWS CLI configured** with credentials
2. **GitHub Personal Access Token** with `repo` scope
3. **Jira API Token** (if using Jira integration)
4. **AWS Security Agent Instance** created

## Step 1: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Required credentials:
- `GITHUB_TOKEN` - Create at https://github.com/settings/tokens
- `JIRA_URL` - Your Jira instance URL
- `JIRA_EMAIL` - Your Jira email
- `JIRA_API_TOKEN` - Create at https://id.atlassian.com/manage-profile/security/api-tokens
- `AWS_SECURITY_AGENT_INSTANCE_ID` - Your Security Agent instance ID

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 3: Test Locally

```bash
# Start the server
python main.py

# In another terminal, test the endpoint
curl -X POST "http://localhost:9000/review?repo=owner/repo&pr_number=123"
```

## Step 4: Deploy to AgentCore

```bash
# Run deployment script
./deploy.sh
```

Or manually:
```bash
# Configure AgentCore
agentcore configure -e main.py --protocol A2A

# Deploy
agentcore deploy
```

## Step 5: Configure GitHub Webhook

1. Go to your GitHub repository
2. Navigate to **Settings → Webhooks → Add webhook**
3. Configure:
   - **Payload URL**: `https://your-agentcore-url/webhook`
   - **Content type**: `application/json`
   - **Events**: Select "Pull requests"
   - **Active**: ✓ Checked
4. Save webhook

## Step 6: Test with a Real PR

1. Create a test PR in your repository
2. The agent will automatically review it
3. Check the PR for the review comment

## Troubleshooting

### Agent not responding
- Check AgentCore logs: `agentcore logs`
- Verify webhook is active in GitHub settings
- Test manual endpoint: `curl -X POST "https://your-url/review?repo=owner/repo&pr_number=123"`

### Missing Jira ticket
- Ensure PR title or branch contains ticket ID (e.g., "PROJ-123")
- Verify Jira credentials in .env

### Security scan failing
- Verify AWS Security Agent instance ID
- Check IAM permissions for Security Agent
- Review CloudWatch logs

## Architecture Overview

```
GitHub PR → Webhook → AgentCore Runtime → Orchestrator
                                              ↓
                                    ┌─────────┴─────────┐
                                    ↓                   ↓
                            Specialist Agents    Security Scans
                            (4 agents)           (Pattern + AWS)
                                    ↓                   ↓
                                    └─────────┬─────────┘
                                              ↓
                                    Aggregated Review
                                              ↓
                                    GitHub Comment
```

## Cost Monitoring

Track costs in AWS Cost Explorer:
- AgentCore Runtime usage
- AWS Security Agent API calls
- Bedrock model invocations

Expected: < $0.15 per PR review

## Next Steps

- Customize agent instructions in `agents/` directory
- Add custom security patterns in `tools/security_tools.py`
- Configure AgentCore Memory for learning (optional)
- Set up CloudWatch dashboards for monitoring
