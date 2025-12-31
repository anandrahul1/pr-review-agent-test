"""Jira MCP Tools for ticket information"""
import os
import httpx
from strands import tool

JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

@tool
async def get_jira_ticket(ticket_id: str) -> dict:
    """Fetch Jira ticket details"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{JIRA_URL}/rest/api/3/issue/{ticket_id}",
            auth=(JIRA_EMAIL, JIRA_API_TOKEN)
        )
        if response.status_code != 200:
            return {"error": f"Ticket {ticket_id} not found"}
        
        data = response.json()
        fields = data["fields"]
        return {
            "ticket_id": ticket_id,
            "title": fields["summary"],
            "status": fields["status"]["name"],
            "assignee": fields.get("assignee", {}).get("displayName", "Unassigned"),
            "priority": fields.get("priority", {}).get("name", "None"),
            "description": fields.get("description", "No description")
        }
