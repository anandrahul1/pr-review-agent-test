import os
import logging
import hmac
import hashlib
from strands.multiagent.a2a import A2AServer
from agents.orchestrator import orchestrator_agent
import uvicorn
from fastapi import FastAPI, Request, BackgroundTasks

logging.basicConfig(level=logging.INFO)

runtime_url = os.environ.get('AGENTCORE_RUNTIME_URL', 'http://127.0.0.1:9000/')
github_webhook_secret = os.environ.get('GITHUB_WEBHOOK_SECRET', '')
logging.info(f"Runtime URL: {runtime_url}")

# Wrap orchestrator in A2A server
a2a_server = A2AServer(
    agent=orchestrator_agent,
    http_url=runtime_url,
    serve_at_root=True
)

app = FastAPI()

def verify_github_signature(payload: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature"""
    if not github_webhook_secret:
        return True  # Skip if no secret
    expected = "sha256=" + hmac.new(
        github_webhook_secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

async def process_pr_review(repo: str, pr_number: int):
    """Process PR review in background"""
    try:
        message = f"Review PR #{pr_number} in {repo}"
        await orchestrator_agent.ainvoke(message)
        logging.info(f"Completed review for {repo} PR #{pr_number}")
    except Exception as e:
        logging.error(f"Error processing PR review: {e}")

@app.post("/webhook/github")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle GitHub webhook events"""
    signature = request.headers.get("X-Hub-Signature-256", "")
    payload = await request.body()
    
    if not verify_github_signature(payload, signature):
        return {"error": "Invalid signature"}, 401
    
    event_type = request.headers.get("X-GitHub-Event")
    data = await request.json()
    
    if event_type == "pull_request":
        action = data.get("action")
        if action in ["opened", "synchronize", "reopened"]:
            pr = data["pull_request"]
            repo = data["repository"]["full_name"]
            pr_number = pr["number"]
            
            background_tasks.add_task(process_pr_review, repo, pr_number)
            logging.info(f"Queued review for {repo} PR #{pr_number}")
            
            return {"status": "review_queued", "pr": pr_number}
    
    return {"status": "ignored"}

@app.get("/ping")
def ping():
    return {"status": "healthy"}

app.mount("/", a2a_server.to_fastapi_app())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
# Updated Wed Dec 31 05:38:17 UTC 2025
# Updated Thu Jan  1 13:41:38 UTC 2026
