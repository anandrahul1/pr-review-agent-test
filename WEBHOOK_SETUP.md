# GitHub Webhook Setup Guide

## Overview
The PR Review Agent now supports automatic reviews via GitHub webhooks. When a PR is opened, updated, or reopened, GitHub will automatically trigger the agent.

## Architecture
- **Webhook Endpoint**: `/webhook/github` (handles GitHub events)
- **A2A Endpoint**: `/` (handles direct AgentCore invocations)
- **Health Check**: `/ping` (returns `{"status": "healthy"}`)

## Setup Options

### Option 1: AWS API Gateway (Recommended for Production)

#### Step 1: Create API Gateway
```bash
# Create REST API
aws apigateway create-rest-api \
  --name "pr-review-agent-webhook" \
  --description "GitHub webhook for PR Review Agent" \
  --region us-east-1

# Note the API ID from output
export API_ID=<your-api-id>
```

#### Step 2: Get Root Resource ID
```bash
aws apigateway get-resources \
  --rest-api-id $API_ID \
  --region us-east-1 \
  --query 'items[0].id' \
  --output text
```

#### Step 3: Create Webhook Resource
```bash
# Get root resource ID
export ROOT_ID=$(aws apigateway get-resources --rest-api-id $API_ID --region us-east-1 --query 'items[0].id' --output text)

# Create /webhook resource
aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $ROOT_ID \
  --path-part webhook \
  --region us-east-1

export WEBHOOK_ID=<webhook-resource-id>

# Create /webhook/github resource
aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $WEBHOOK_ID \
  --path-part github \
  --region us-east-1

export GITHUB_ID=<github-resource-id>
```

#### Step 4: Create POST Method
```bash
# Create method
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $GITHUB_ID \
  --http-method POST \
  --authorization-type NONE \
  --region us-east-1

# Create integration (HTTP proxy to AgentCore)
aws apigateway put-integration \
  --rest-api-id $API_ID \
  --resource-id $GITHUB_ID \
  --http-method POST \
  --type HTTP_PROXY \
  --integration-http-method POST \
  --uri "http://<agentcore-runtime-url>/webhook/github" \
  --region us-east-1
```

#### Step 5: Deploy API
```bash
aws apigateway create-deployment \
  --rest-api-id $API_ID \
  --stage-name prod \
  --region us-east-1

# Your webhook URL will be:
echo "https://${API_ID}.execute-api.us-east-1.amazonaws.com/prod/webhook/github"
```

### Option 2: Direct AgentCore Invocation (Current Setup)

For now, you can use the manual invocation method:

```bash
cd /home/ubuntu/prreview
source venv/bin/activate

agentcore invoke '{
  "jsonrpc": "2.0",
  "id": "pr-review-001",
  "method": "message/send",
  "params": {
    "message": {
      "role": "user",
      "parts": [{"kind": "text", "text": "Review PR #<NUMBER> in <OWNER>/<REPO>"}],
      "messageId": "msg-001"
    }
  }
}'
```

### Option 3: GitHub Actions (Automated without API Gateway)

Create `.github/workflows/pr-review.yml` in your repository:

```yaml
name: PR Review Agent

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Invoke PR Review Agent
        run: |
          aws bedrock-agentcore invoke-runtime \
            --runtime-id x-bMWWBTEmLd \
            --region us-east-1 \
            --payload '{
              "jsonrpc": "2.0",
              "id": "pr-${{ github.event.pull_request.number }}",
              "method": "message/send",
              "params": {
                "message": {
                  "role": "user",
                  "parts": [{
                    "kind": "text",
                    "text": "Review PR #${{ github.event.pull_request.number }} in ${{ github.repository }}"
                  }],
                  "messageId": "gh-action-${{ github.run_id }}"
                }
              }
            }'
```

## Configure GitHub Webhook (For Option 1)

1. Go to your repository: https://github.com/anandrahul1/pr-review-agent-test
2. Navigate to **Settings** → **Webhooks** → **Add webhook**
3. Configure:
   - **Payload URL**: Your API Gateway URL from Option 1
   - **Content type**: `application/json`
   - **Secret**: (optional) Set `GITHUB_WEBHOOK_SECRET` env var in AgentCore
   - **Events**: Select "Pull requests"
   - **Active**: ✓ Checked
4. Click **Add webhook**

## Testing

### Test Webhook Endpoint Locally
```bash
curl -X POST http://localhost:9000/webhook/github \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: pull_request" \
  -d '{
    "action": "opened",
    "pull_request": {"number": 1},
    "repository": {"full_name": "anandrahul1/pr-review-agent-test"}
  }'
```

### Test via GitHub
1. Create a new PR in your test repository
2. Check CloudWatch logs:
```bash
aws logs tail /aws/bedrock-agentcore/runtimes/x-bMWWBTEmLd-DEFAULT \
  --log-stream-name-prefix "2025/12/30/[runtime-logs]" \
  --follow
```

## Security

### Webhook Secret Verification
To enable signature verification:

```bash
# Generate a secret
WEBHOOK_SECRET=$(openssl rand -hex 32)

# Configure in AgentCore
agentcore configure --env GITHUB_WEBHOOK_SECRET=$WEBHOOK_SECRET

# Redeploy
agentcore launch

# Add the same secret to GitHub webhook settings
```

## Troubleshooting

### Check Agent Logs
```bash
aws logs tail /aws/bedrock-agentcore/runtimes/x-bMWWBTEmLd-DEFAULT \
  --log-stream-name-prefix "2025/12/30/[runtime-logs]" \
  --since 10m
```

### Test Health Endpoint
```bash
curl http://localhost:9000/ping
# Should return: {"status": "healthy"}
```

### Verify Webhook Delivery
In GitHub:
1. Go to Settings → Webhooks
2. Click on your webhook
3. Check "Recent Deliveries" tab
4. View request/response details

## Current Status

✅ Webhook handler implemented in `main.py`
✅ Agent deployed with webhook support
⏳ Pending: API Gateway setup OR GitHub Actions workflow
⏳ Pending: GitHub webhook configuration

## Recommended Next Steps

**For Quick Testing**: Use Option 3 (GitHub Actions) - no infrastructure setup needed
**For Production**: Use Option 1 (API Gateway) - proper webhook endpoint with monitoring
