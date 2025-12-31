#!/bin/bash
# Setup OIDC provider and role for GitHub Actions

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REPO="anandrahul1/pr-review-agent-test"  # Change to your repo

echo "Setting up OIDC for GitHub Actions..."
echo "Account: $ACCOUNT_ID"
echo "Repository: $REPO"

# Create OIDC provider (if not exists)
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1 \
  2>/dev/null || echo "OIDC provider already exists"

# Create trust policy
cat > /tmp/trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::${ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:${REPO}:*"
        }
      }
    }
  ]
}
EOF

# Create role
aws iam create-role \
  --role-name GitHubActionsAgentCoreDeployRole \
  --assume-role-policy-document file:///tmp/trust-policy.json \
  --description "Role for GitHub Actions to deploy AgentCore Runtime" \
  2>/dev/null || echo "Role already exists"

# Attach policies
aws iam attach-role-policy \
  --role-name GitHubActionsAgentCoreDeployRole \
  --policy-arn arn:aws:iam::aws:policy/PowerUserAccess

aws iam attach-role-policy \
  --role-name GitHubActionsAgentCoreDeployRole \
  --policy-arn arn:aws:iam::aws:policy/IAMFullAccess

ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/GitHubActionsAgentCoreDeployRole"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Add this to your GitHub repository secrets:"
echo "AWS_ROLE_ARN = $ROLE_ARN"
echo ""
echo "Go to: https://github.com/${REPO}/settings/secrets/actions"
