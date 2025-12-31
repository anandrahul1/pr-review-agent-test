#!/bin/bash
# Deployment script for PR Review Agent to AgentCore Runtime

set -e

echo "🚀 PR Review Agent Deployment Script"
echo "===================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please copy .env.example to .env and configure your credentials"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Test locally first
echo "🧪 Testing local setup..."
python -c "
from dotenv import load_dotenv
import os
load_dotenv()

required_vars = ['GITHUB_TOKEN', 'JIRA_URL', 'JIRA_EMAIL', 'JIRA_API_TOKEN']
missing = [v for v in required_vars if not os.getenv(v)]

if missing:
    print(f'❌ Missing environment variables: {missing}')
    exit(1)
else:
    print('✅ All required environment variables configured')
"

if [ $? -ne 0 ]; then
    exit 1
fi

# Configure AgentCore
echo "⚙️  Configuring AgentCore..."
agentcore configure -e main.py --protocol A2A

# Deploy to AgentCore Runtime
echo "🚀 Deploying to AgentCore Runtime..."
agentcore deploy

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Note the AgentCore Runtime URL from the deployment output"
echo "2. Configure GitHub webhook:"
echo "   - Go to your repo Settings → Webhooks"
echo "   - Add webhook with URL: https://your-agentcore-url/webhook"
echo "   - Content type: application/json"
echo "   - Events: Pull requests"
echo ""
echo "3. Test with a PR or use manual endpoint:"
echo "   curl -X POST 'https://your-agentcore-url/review?repo=owner/repo&pr_number=123'"
