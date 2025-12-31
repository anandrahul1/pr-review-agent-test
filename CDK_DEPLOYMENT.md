# CDK Deployment Guide

## Overview

This project uses AWS CDK with GitHub Actions for automatic deployment to AgentCore Runtime.

## Architecture

```
Code Push → GitHub Actions → CDK Deploy → AgentCore Runtime
```

## What Happens Automatically

1. **Push to main branch** triggers GitHub Actions
2. **Docker build** (ARM64) happens in GitHub Actions runner
3. **CDK deploy** pushes image to ECR and updates AgentCore Runtime
4. **Runtime ARN** is output for reference

## Setup (One-Time)

### 1. Bootstrap CDK

```bash
npx cdk bootstrap aws://216989103085/us-east-1
```

### 2. OIDC Role (Already Done)

✅ Role created: `GitHubActionsAgentCoreDeployRole`
✅ Secret added: `AWS_ROLE_ARN`

## Manual Deployment

```bash
# Test synthesis
npx cdk synth

# Deploy
npx cdk deploy
```

## Automatic Deployment

Push to main branch with changes to:
- `agents/**`
- `tools/**`
- `main.py`
- `requirements.txt`
- `Dockerfile`
- `.bedrock_agentcore.yaml`
- `lib/**` or `bin/**`

## Monitoring

Check deployment status:
```bash
gh run list --repo anandrahul1/pr-review-agent-test --limit 5
```

View logs:
```bash
gh run view <run-id> --log
```

## Runtime ARN

After deployment, get the runtime ARN:
```bash
aws cloudformation describe-stacks \
  --stack-name PrReviewAgentStack \
  --query 'Stacks[0].Outputs[?OutputKey==`RuntimeArn`].OutputValue' \
  --output text
```

## Invoking the Agent

```bash
agentcore invoke '{
  "jsonrpc": "2.0",
  "id": "test-001",
  "method": "message/send",
  "params": {
    "message": {
      "role": "user",
      "parts": [{"kind": "text", "text": "Review PR #3 in anandrahul1/pr-review-agent-test"}],
      "messageId": "test-001"
    }
  }
}'
```

## Cost

- AgentCore Runtime: ~$0.05-0.10 per PR review
- ECR storage: ~$0.10/month
- CloudFormation: Free

## Troubleshooting

### Deployment fails with "No space left on device"
GitHub Actions runner ran out of space during Docker build. This is rare but can happen with large dependencies.

### "Runtime name already exists"
Delete the existing runtime first:
```bash
aws bedrock-agentcore delete-runtime --runtime-name prreviewagent
```

### CDK bootstrap required
```bash
npx cdk bootstrap
```
