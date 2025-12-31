"""GitHub MCP Tools for PR Review"""
import os
import httpx
from strands import tool

# Get token from environment variable
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_API = "https://api.github.com"

@tool
async def get_pr_details(repo: str, pr_number: int) -> dict:
    """Fetch PR details including title, description, and metadata"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}",
            headers={"Authorization": f"token {GITHUB_TOKEN}"}
        )
        data = response.json()
        return {
            "title": data["title"],
            "description": data["body"],
            "author": data["user"]["login"],
            "branch": data["head"]["ref"],
            "base_branch": data["base"]["ref"],
            "state": data["state"],
            "diff_url": data["diff_url"]
        }

@tool
async def get_pr_diff(repo: str, pr_number: int) -> str:
    """Fetch the PR diff content"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}",
            headers={
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3.diff"
            }
        )
        return response.text

@tool
async def get_pr_files(repo: str, pr_number: int) -> list:
    """Get list of files changed in PR"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}/files",
            headers={"Authorization": f"token {GITHUB_TOKEN}"}
        )
        files = response.json()
        return [
            {
                "filename": f["filename"],
                "status": f["status"],
                "additions": f["additions"],
                "deletions": f["deletions"],
                "changes": f["changes"]
            }
            for f in files
        ]

@tool
async def post_review_comment(repo: str, pr_number: int, body: str) -> dict:
    """Post review comment to GitHub PR"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{GITHUB_API}/repos/{repo}/issues/{pr_number}/comments",
            headers={"Authorization": f"token {GITHUB_TOKEN}"},
            json={"body": body}
        )
        return response.json()
