import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as agentcore from '@aws-cdk/aws-bedrock-agentcore-alpha';
import { Construct } from 'constructs';

export class PrReviewAgentStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create AgentCore Runtime with automatic Docker build
    const runtime = new agentcore.Runtime(this, 'PrReviewAgentRuntime', {
      runtimeName: 'prreviewagent',
      agentRuntimeArtifact: agentcore.AgentRuntimeArtifact.fromAsset('.', {
        platform: cdk.aws_ecr_assets.Platform.LINUX_ARM64, // AgentCore requires ARM64
        exclude: [
          'cdk.out',
          'node_modules',
          '.git',
          '.github',
          '*.md',
          'bin',
          'lib',
          'tsconfig.json',
          'cdk.json',
          'package*.json',
          '.env*',
          'venv',
          '__pycache__',
          '*.pyc',
        ],
      }),
      networkConfiguration: agentcore.RuntimeNetworkConfiguration.usingPublicNetwork(),
      protocolConfiguration: agentcore.ProtocolType.A2A,
      environmentVariables: {
        GITHUB_TOKEN: process.env.GITHUB_TOKEN || '',
      },
    });

    // Add Bedrock model invocation permissions
    runtime.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['bedrock:InvokeModel*'],
        resources: [
          'arn:aws:bedrock:*::foundation-model/*',
          'arn:aws:bedrock:*:*:inference-profile/*',
        ],
      })
    );

    // Add GitHub API permissions (if using Secrets Manager)
    runtime.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['secretsmanager:GetSecretValue'],
        resources: ['arn:aws:secretsmanager:*:*:secret:github/*'],
      })
    );

    // Output the runtime ARN
    new cdk.CfnOutput(this, 'RuntimeArn', {
      value: runtime.agentRuntimeArn,
      description: 'AgentCore Runtime ARN',
    });
  }
}
