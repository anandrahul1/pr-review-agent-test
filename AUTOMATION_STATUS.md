# Automatic PR Review Setup - Current Status

## ❌ GitHub Actions Approach - Not Working

The AgentCore SDK (`bedrock-agentcore-sdk`) is not yet publicly available on PyPI, so we cannot install it in GitHub Actions.

## ✅ Working Solution: Manual Invocation

Until AgentCore provides a public API endpoint or the SDK becomes available, use manual invocation:

### When a PR is Created/Updated:

```bash
cd /home/ubuntu/prreview
source venv/bin/activate

agentcore invoke '{
  "jsonrpc": "2.0",
  "id": "pr-<NUMBER>",
  "method": "message/send",
  "params": {
    "message": {
      "role": "user",
      "parts": [{"kind": "text", "text": "Review PR #<NUMBER> in anandrahul1/pr-review-agent-test"}],
      "messageId": "manual-<TIMESTAMP>"
    }
  }
}'
```

### Example for PR #3:

```bash
agentcore invoke '{
  "jsonrpc": "2.0",
  "id": "pr-3",
  "method": "message/send",
  "params": {
    "message": {
      "role": "user",
      "parts": [{"kind": "text", "text": "Review PR #3 in anandrahul1/pr-review-agent-test"}],
      "messageId": "manual-001"
    }
  }
}'
```

## 🔮 Future Automation Options

### Option 1: When AgentCore SDK is Public
Update `.github/workflows/pr-review.yml` to install the SDK and invoke the agent.

### Option 2: API Gateway + Lambda
1. Create Lambda function that calls `agentcore invoke`
2. Expose via API Gateway
3. Configure GitHub webhook to call API Gateway
4. Lambda invokes AgentCore agent

### Option 3: Local Webhook Server
Run a local server that:
1. Receives GitHub webhooks
2. Calls `agentcore invoke`
3. Requires ngrok or similar for public URL

## Current Recommendation

**Use manual invocation** until AgentCore provides:
- Public SDK on PyPI
- Direct HTTP API endpoint
- AWS CLI integration

The agent works perfectly - it's just the automation trigger that needs manual intervention for now.
