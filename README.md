# PR Review Agent

AI-powered PR review system using AWS Strands Agents on Amazon Bedrock AgentCore Runtime.

## Architecture

- **Pattern**: Swarm (4 specialist agents + orchestrator)
- **Review Time**: 2-3 minutes
- **Security**: Comprehensive OWASP Top 10 + vulnerability scanning

## Agents

1. **Orchestrator** - Coordinates review workflow
2. **Code Quality & Architecture** - Code quality, naming, design patterns
3. **Security** - OWASP Top 10, injection attacks, secrets, vulnerabilities
4. **Performance & Testing** - Performance patterns, test coverage
5. **Documentation & Compliance** - Docs, compliance, backwards compatibility

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

Required variables:
- `GITHUB_TOKEN` - GitHub personal access token
- `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN` - Jira credentials

### 3. Test Locally

```bash
python main.py
```

Server runs on `http://localhost:9000`

Test endpoint:
```bash
curl -X POST "http://localhost:9000/review?repo=owner/repo&pr_number=123"
```

### 4. Deploy to AgentCore Runtime

```bash
# Configure AgentCore
agentcore configure -e main.py --protocol A2A

# Deploy
agentcore deploy
```

### 5. Configure GitHub Webhook

In your GitHub repository:
1. Go to Settings → Webhooks → Add webhook
2. Payload URL: `https://your-agentcore-url/webhook`
3. Content type: `application/json`
4. Events: Select "Pull requests"
5. Save

## Project Structure

```
pr-review-agent/
├── agents/
│   ├── orchestrator.py              # Swarm coordinator
│   ├── code_quality_agent.py        # Code quality reviews
│   ├── security_agent.py            # Security scanning
│   ├── performance_testing_agent.py # Performance & tests
│   └── documentation_compliance_agent.py # Docs & compliance
├── tools/
│   ├── github_tools.py              # GitHub MCP tools
│   ├── jira_tools.py                # Jira MCP tools
│   └── security_tools.py            # Security scanning tools
├── main.py                          # FastAPI application
├── requirements.txt                 # Dependencies
└── .env.example                     # Environment template
```

## Review Output

The agent posts a comprehensive review comment to GitHub:

```markdown
## 🤖 PR Review Results

🎫 **Jira**: PROJ-123 - Add user authentication

**Recommendation:** ⚠️ Request Changes

### Summary
- ✅ Code Quality: PASS
- ❌ Security: FAIL (2 critical issues)
- ✅ Performance: PASS
- ⚠️ Documentation: WARNINGS

### Critical Issues Blocking Approval:
1. **SQL Injection Risk** (src/api/users.py:45)
2. **Hardcoded API Key** (src/config.py:12)

### Human Reviewer: Please decide
- [ ] Approve
- [ ] Request Changes (recommended)
- [ ] Comment only

Review completed in 2m 47s
```

## Cost Estimate

- AgentCore Runtime: ~$0.05-0.10 per PR
- **Total**: < $0.15 per PR review

## Monitoring

Key metrics tracked:
- Review completion time
- Critical issues found
- Agent failure rate

## Security

- GitHub PAT with repo access
- No PR code stored (in-memory only)
- CloudTrail logging enabled

## Support

For issues or questions, refer to:
- [AWS Strands Agents Documentation](https://docs.aws.amazon.com/strands/)
- [AgentCore Runtime Guide](https://docs.aws.amazon.com/bedrock/agentcore/)
# Trigger redeploy with token
# Updated token - Thu Jan  1 13:34:05 UTC 2026
