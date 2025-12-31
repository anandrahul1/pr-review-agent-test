#!/usr/bin/env python3
"""
Test script for PR Review Agent
Tests all components before deployment
"""
import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test environment configuration"""
    print("🔍 Testing environment configuration...")
    load_dotenv()
    
    required_vars = [
        'GITHUB_TOKEN',
        'JIRA_URL',
        'JIRA_EMAIL',
        'JIRA_API_TOKEN'
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        return False
    
    print("✅ All environment variables configured")
    return True

def test_imports():
    """Test all required imports"""
    print("\n🔍 Testing imports...")
    
    try:
        from strands import Agent, tool
        from strands.multiagent import Swarm
        print("✅ Strands imports successful")
    except ImportError as e:
        print(f"❌ Strands import failed: {e}")
        return False
    
    try:
        from fastapi import FastAPI
        import uvicorn
        print("✅ FastAPI imports successful")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import boto3
        print("✅ Boto3 import successful")
    except ImportError as e:
        print(f"❌ Boto3 import failed: {e}")
        return False
    
    return True

def test_tools():
    """Test tool imports"""
    print("\n🔍 Testing tools...")
    
    try:
        from tools.github_tools import get_pr_details, get_pr_diff, get_pr_files, post_review_comment
        print("✅ GitHub tools imported")
    except ImportError as e:
        print(f"❌ GitHub tools import failed: {e}")
        return False
    
    try:
        from tools.jira_tools import get_jira_ticket
        print("✅ Jira tools imported")
    except ImportError as e:
        print(f"❌ Jira tools import failed: {e}")
        return False
    
    try:
        from tools.security_tools import pattern_security_scan, comprehensive_security_scan
        print("✅ Security tools imported")
    except ImportError as e:
        print(f"❌ Security tools import failed: {e}")
        return False
    
    return True

def test_agents():
    """Test agent imports"""
    print("\n🔍 Testing agents...")
    
    try:
        from agents.code_quality_agent import code_quality_agent
        print("✅ Code Quality Agent imported")
    except ImportError as e:
        print(f"❌ Code Quality Agent import failed: {e}")
        return False
    
    try:
        from agents.security_agent import security_agent
        print("✅ Security Agent imported")
    except ImportError as e:
        print(f"❌ Security Agent import failed: {e}")
        return False
    
    try:
        from agents.performance_testing_agent import performance_testing_agent
        print("✅ Performance & Testing Agent imported")
    except ImportError as e:
        print(f"❌ Performance & Testing Agent import failed: {e}")
        return False
    
    try:
        from agents.documentation_compliance_agent import documentation_compliance_agent
        print("✅ Documentation & Compliance Agent imported")
    except ImportError as e:
        print(f"❌ Documentation & Compliance Agent import failed: {e}")
        return False
    
    try:
        from agents.orchestrator import orchestrator_agent, pr_review_swarm
        print("✅ Orchestrator Agent imported")
    except ImportError as e:
        print(f"❌ Orchestrator Agent import failed: {e}")
        return False
    
    return True

def test_aws_credentials():
    """Test AWS credentials"""
    print("\n🔍 Testing AWS credentials...")
    
    try:
        import boto3
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS credentials valid (Account: {identity['Account']})")
        return True
    except Exception as e:
        print(f"❌ AWS credentials test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("PR Review Agent - Pre-Deployment Tests")
    print("=" * 60)
    
    tests = [
        ("Environment", test_environment),
        ("Imports", test_imports),
        ("Tools", test_tools),
        ("Agents", test_agents),
        ("AWS Credentials", test_aws_credentials)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} test crashed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed! Ready to deploy.")
        print("\nNext steps:")
        print("1. Run: ./deploy.sh")
        print("2. Configure GitHub webhook")
        print("3. Test with a real PR")
        return 0
    else:
        print("❌ Some tests failed. Please fix issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
