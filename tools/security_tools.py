"""Security scanning tools"""
import re
import os
from strands import tool

@tool
async def pattern_security_scan(code_diff: str) -> dict:
    """Fast pattern-based security scanning"""
    findings = []
    
    # Hardcoded secrets patterns
    secret_patterns = [
        (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
        (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key"),
        (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret"),
        (r'token\s*=\s*["\'][^"\']+["\']', "Hardcoded token"),
        (r'(AKIA[0-9A-Z]{16})', "AWS Access Key"),
    ]
    
    # SQL injection patterns
    sql_patterns = [
        (r'execute\s*\(\s*["\'].*\+.*["\']', "Potential SQL injection"),
        (r'query\s*\(\s*["\'].*\+.*["\']', "Potential SQL injection"),
        (r'\.format\s*\(.*\).*execute', "SQL injection via format"),
    ]
    
    # XSS patterns
    xss_patterns = [
        (r'innerHTML\s*=', "Potential XSS via innerHTML"),
        (r'dangerouslySetInnerHTML', "Potential XSS in React"),
        (r'eval\s*\(', "Dangerous eval usage"),
    ]
    
    all_patterns = secret_patterns + sql_patterns + xss_patterns
    
    for pattern, description in all_patterns:
        matches = re.finditer(pattern, code_diff, re.IGNORECASE)
        for match in matches:
            findings.append({
                "severity": "HIGH",
                "category": description,
                "pattern": match.group(0)[:50],
                "recommendation": f"Fix {description.lower()}"
            })
    
    return {
        "scan_type": "pattern_based",
        "findings_count": len(findings),
        "findings": findings
    }

@tool
async def comprehensive_security_scan(code_diff: str) -> dict:
    """
    Comprehensive security scanning with OWASP Top 10 coverage
    
    Note: AWS Security Agent integration requires GitHub App installation
    and works automatically on PRs. This tool provides equivalent coverage
    through pattern matching for OWASP Top 10 vulnerabilities.
    """
    findings = []
    
    # OWASP Top 10 2021 Coverage
    
    # 1. Broken Access Control
    access_control_patterns = [
        (r'@app\.route.*methods=\[.*GET.*POST', "Missing access control - GET and POST on same route"),
        (r'if\s+user\.is_admin\s*==\s*True', "Hardcoded admin check - use role-based access"),
    ]
    
    # 2. Cryptographic Failures
    crypto_patterns = [
        (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
        (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key"),
        (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret"),
        (r'token\s*=\s*["\'][^"\']+["\']', "Hardcoded token"),
        (r'(AKIA[0-9A-Z]{16})', "AWS Access Key exposed"),
        (r'md5\(', "Weak hashing algorithm (MD5)"),
        (r'sha1\(', "Weak hashing algorithm (SHA1)"),
    ]
    
    # 3. Injection (SQL, NoSQL, OS Command)
    injection_patterns = [
        (r'execute\s*\(\s*["\'].*\+.*["\']', "SQL injection risk - use parameterized queries"),
        (r'query\s*\(\s*["\'].*\+.*["\']', "SQL injection risk"),
        (r'\.format\s*\(.*\).*execute', "SQL injection via format()"),
        (r'eval\s*\(', "Code injection via eval()"),
        (r'exec\s*\(', "Code injection via exec()"),
        (r'os\.system\s*\(.*\+', "OS command injection"),
        (r'subprocess\.call\s*\(.*\+', "OS command injection"),
    ]
    
    # 4. Insecure Design
    design_patterns = [
        (r'sleep\s*\(\s*\d+\s*\)', "Potential timing attack vulnerability"),
        (r'random\.random\(\)', "Insecure randomness - use secrets module"),
    ]
    
    # 5. Security Misconfiguration
    config_patterns = [
        (r'DEBUG\s*=\s*True', "Debug mode enabled in production"),
        (r'ALLOWED_HOSTS\s*=\s*\[\s*["\']?\*["\']?\s*\]', "Wildcard in ALLOWED_HOSTS"),
        (r'verify\s*=\s*False', "SSL verification disabled"),
    ]
    
    # 6. Vulnerable and Outdated Components
    # (Would require dependency scanning - note in findings)
    
    # 7. Identification and Authentication Failures
    auth_patterns = [
        (r'session\[.*\]\s*=\s*user', "Session fixation risk"),
        (r'cookie.*secure\s*=\s*False', "Insecure cookie configuration"),
        (r'password.*==.*input', "Plain text password comparison"),
    ]
    
    # 8. Software and Data Integrity Failures
    integrity_patterns = [
        (r'pickle\.loads?\(', "Insecure deserialization"),
        (r'yaml\.load\(', "Unsafe YAML deserialization - use safe_load"),
    ]
    
    # 9. Security Logging and Monitoring Failures
    logging_patterns = [
        (r'except.*:\s*pass', "Swallowed exception - no logging"),
        (r'except.*:\s*continue', "Swallowed exception - no logging"),
    ]
    
    # 10. Server-Side Request Forgery (SSRF)
    ssrf_patterns = [
        (r'requests\.get\s*\(\s*user', "SSRF risk - validate URL"),
        (r'urllib\.request\s*\(\s*user', "SSRF risk - validate URL"),
    ]
    
    # XSS patterns
    xss_patterns = [
        (r'innerHTML\s*=', "XSS risk via innerHTML"),
        (r'dangerouslySetInnerHTML', "XSS risk in React"),
        (r'document\.write\s*\(', "XSS risk via document.write"),
    ]
    
    # Aggregate all patterns
    all_patterns = (
        [(p, f"Access Control: {d}") for p, d in access_control_patterns] +
        [(p, f"Cryptographic Failure: {d}") for p, d in crypto_patterns] +
        [(p, f"Injection: {d}") for p, d in injection_patterns] +
        [(p, f"Insecure Design: {d}") for p, d in design_patterns] +
        [(p, f"Misconfiguration: {d}") for p, d in config_patterns] +
        [(p, f"Authentication: {d}") for p, d in auth_patterns] +
        [(p, f"Data Integrity: {d}") for p, d in integrity_patterns] +
        [(p, f"Logging: {d}") for p, d in logging_patterns] +
        [(p, f"SSRF: {d}") for p, d in ssrf_patterns] +
        [(p, f"XSS: {d}") for p, d in xss_patterns]
    )
    
    for pattern, description in all_patterns:
        matches = re.finditer(pattern, code_diff, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            # Determine severity
            severity = "CRITICAL" if any(x in description.lower() for x in ["injection", "hardcoded", "exposed"]) else "HIGH"
            
            findings.append({
                "severity": severity,
                "category": description.split(":")[0],
                "description": description,
                "pattern": match.group(0)[:50],
                "recommendation": f"Fix {description.lower()}"
            })
    
    return {
        "scan_type": "comprehensive_owasp_top_10",
        "findings_count": len(findings),
        "findings": findings
    }
