# A2A Protocol Migration - SUCCESS ✅

## Problem
FastAPI webhook implementation was incompatible with AgentCore A2A protocol, resulting in 424 errors.

## Root Causes
1. **Wrong Protocol**: Using REST endpoints instead of A2A JSON-RPC
2. **Wrong Port**: Using 8080 instead of 9000
3. **Wrong Path**: Using `/webhook` instead of root `/`
4. **Model Issue**: Using direct model ID instead of inference profile

## Solution

### 1. Converted to A2A Protocol
**File**: `main.py`

```python
import os
import logging
from strands.multiagent.a2a import A2AServer
from agents.orchestrator import orchestrator_agent
import uvicorn
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)

runtime_url = os.environ.get('AGENTCORE_RUNTIME_URL', 'http://127.0.0.1:9000/')
logging.info(f"Runtime URL: {runtime_url}")

# Wrap orchestrator in A2A server
a2a_server = A2AServer(
    agent=orchestrator_agent,
    http_url=runtime_url,
    serve_at_root=True
)

app = FastAPI()

@app.get("/ping")
def ping():
    return {"status": "healthy"}

app.mount("/", a2a_server.to_fastapi_app())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
```

### 2. Fixed Model Configuration
Changed all agents from:
```python
model="anthropic.claude-3-5-sonnet-20241022-v2:0"
```

To inference profile:
```python
model="us.anthropic.claude-3-5-sonnet-20241022-v2:0"
```

### 3. Updated Dependencies
```
strands-agents[a2a]>=0.1.0  # Added A2A support
```

## Deployment Status

✅ **Agent ARN**: `arn:aws:bedrock-agentcore:us-east-1:216989103085:runtime/x-bMWWBTEmLd`
✅ **Protocol**: A2A (JSON-RPC)
✅ **Port**: 9000
✅ **Path**: `/` (root)
✅ **Model**: Inference profile
✅ **Status**: READY and responding

## Testing

### Test Command
```bash
agentcore invoke '{
  "jsonrpc": "2.0",
  "id": "test-001",
  "method": "message/send",
  "params": {
    "message": {
      "role": "user",
      "parts": [
        {
          "kind": "text",
          "text": "Review PR #123 in owner/repo"
        }
      ],
      "messageId": "12345678-1234-1234-1234-123456789012"
    }
  }
}'
```

### Test Result
✅ Agent responds correctly
✅ Asks for repo and PR number
✅ Explains review process
✅ No errors in logs

## Key Differences: A2A vs REST

| Aspect | REST (Old) | A2A (New) |
|--------|-----------|-----------|
| Protocol | HTTP REST | JSON-RPC |
| Port | 8080 | 9000 |
| Path | `/webhook`, `/review` | `/` (root) |
| Format | Custom JSON | JSON-RPC 2.0 |
| Discovery | None | Agent Card at `/.well-known/agent-card.json` |

## Next Steps

1. **GitHub Integration**: Configure GitHub webhook to call AgentCore endpoint
2. **Testing**: Test with real PR data
3. **Monitoring**: Set up CloudWatch dashboards
4. **Documentation**: Update README with A2A invocation examples

## Resources

- [A2A Protocol Docs](https://a2a-protocol.org/)
- [AgentCore A2A Guide](https://aws.github.io/bedrock-agentcore-starter-toolkit/user-guide/runtime/a2a.md)
- [Strands A2A Integration](https://strandsagents.com/latest/user-guide/concepts/model-providers/amazon-bedrock/)

## Logs

CloudWatch Logs:
```bash
aws logs tail /aws/bedrock-agentcore/runtimes/x-bMWWBTEmLd-DEFAULT \
  --log-stream-name-prefix "2025/12/30/[runtime-logs]" --follow
```

GenAI Dashboard:
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#gen-ai-observability/agent-core
