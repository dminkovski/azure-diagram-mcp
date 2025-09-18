# Copyright (c) Microsoft Corporation. All rights reserved.
"""Scanner and code analysis for the azure-diagram-mcp-server."""

import ast
import os
from pydantic import BaseModel, Field
from tempfile import NamedTemporaryFile
from typing import Any, Dict, List, Optional, Tuple

class SecurityIssue(BaseModel):
    """Model for security issues found in code."""
    severity: str
    confidence: str
    line: int
    issue_text: str
    issue_type: str

class CodeMetrics(BaseModel):
    """Model for code metrics."""
    total_lines: int
    code_lines: int
    comment_lines: int
    blank_lines: int
    comment_ratio: float

class CodeScanResult(BaseModel):
    """Model for code scan result."""
    has_errors: bool
    syntax_valid: bool
    security_issues: List[SecurityIssue] = Field(default_factory=list)
    error_message: Optional[str] = None
    metrics: Optional[CodeMetrics] = None

async def validate_syntax(code: str) -> Tuple[bool, Optional[str]]:
    """Validate Python code syntax using ast."""
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        error_msg = f'Syntax error at line {e.lineno}: {e.msg}'
        return False, error_msg
    except Exception as e:
        return False, str(e)


async def count_code_metrics(code: str) -> CodeMetrics:
    """Count code metrics like lines, comments, etc."""
    lines = code.split('\n')
    total_lines = len(lines)
    code_lines = 0
    comment_lines = 0
    blank_lines = 0
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            blank_lines += 1
        elif stripped.startswith('#'):
            comment_lines += 1
        else:
            code_lines += 1
    
    comment_ratio = comment_lines / total_lines if total_lines > 0 else 0.0
    
    return CodeMetrics(
        total_lines=total_lines,
        code_lines=code_lines,
        comment_lines=comment_lines,
        blank_lines=blank_lines,
        comment_ratio=comment_ratio
    )


async def check_security(code: str) -> List[SecurityIssue]:
    """Check code for security issues using basic patterns."""
    security_issues = []
    
    # Basic security checks for common dangerous patterns
    dangerous_patterns = [
        ('exec(', 'Code execution detected'),
        ('eval(', 'Code evaluation detected'), 
        ('__import__', 'Dynamic import detected'),
        ('subprocess', 'Subprocess execution detected'),
        ('os.system', 'System command execution detected'),
    ]
    
    lines = code.split('\n')
    for line_num, line in enumerate(lines, 1):
        for pattern, message in dangerous_patterns:
            if pattern in line:
                security_issues.append(SecurityIssue(
                    severity='MEDIUM',
                    confidence='HIGH',
                    line=line_num,
                    issue_text=message,
                    issue_type='SecurityPattern'
                ))
    
    return security_issues


async def scan_python_code(code: str) -> CodeScanResult:
    """Use ast and bandit to scan the python code for security issues."""
    # Get code metrics
    metrics = await count_code_metrics(code)

    # Check syntax
    syntax_valid, syntax_error = await validate_syntax(code)
    if not syntax_valid:
        return CodeScanResult(
            has_errors=True, syntax_valid=False, error_message=syntax_error, metrics=metrics
        )

    # Check security
    security_issues = await check_security(code)

    # Check for dangerous functions explicitly
    dangerous_functions = check_dangerous_functions(code)
    if dangerous_functions:
        for func in dangerous_functions:
            security_issues.append(
                SecurityIssue(
                    severity='HIGH',
                    confidence='HIGH',
                    line=func['line'],
                    issue_text=f"Dangerous function '{func['function']}' detected",
                    issue_type='DangerousFunctionDetection',
                )
            )

    # Determine if there are errors
    has_errors = bool(security_issues)

    # Generate error message if needed
    error_message = None
    if has_errors:
        messages = [f'{issue.issue_type}: {issue.issue_text}' for issue in security_issues]
        error_message = '\n'.join(messages) if messages else None

    return CodeScanResult(
        has_errors=has_errors,
        syntax_valid=True,
        security_issues=security_issues,
        error_message=error_message,
        metrics=metrics,
    )


def check_dangerous_functions(code: str) -> List[Dict[str, Any]]:
    """Check for dangerous functions like exec, eval, etc."""
    dangerous_patterns = [
        'exec(',
        'eval(',
        'subprocess.',
        'os.system',
        'os.popen',
        '__import__',
        'pickle.loads',
    ]

    results = []
    lines = code.splitlines()

    for i, line in enumerate(lines):
        for pattern in dangerous_patterns:
            if pattern in line:
                results.append(
                    {
                        'function': pattern.rstrip('('),
                        'line': i + 1,
                        'code': line.strip(),
                    }
                )

    return results


def get_fix_suggestion(issue: Dict[str, Any]) -> str:
    """Provide suggestions for fixing security issues."""
    suggestions = {
        'B102': "As an AI assistant, you should not use the exec() function. Instead, describe the code or suggest safer alternatives that don't involve direct code execution.",
        'B307': 'As an AI assistant, you should not use eval(). You can use ast.literal_eval() for parsing simple data structures.',
        'B602': 'As an AI assistant, you should not use subprocess calls. Instead, describe the system operation you want to perform or suggest higher-level library alternatives.',
        'B605': 'As an AI assistant, you should avoid shell commands. Instead, describe the desired operation or suggest library-based alternatives.',
        'B103': 'The pickle module is not secure. Use JSON or other secure serialization methods.',
        'B201': 'Flask app appears to be run with debug=True, which enables the Werkzeug debugger and should not be used in production.',
        'B301': 'Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data.',
        'B324': 'Use of weak cryptographic key. Consider using stronger key lengths.',
        'B501': 'Request with verify=False disables SSL certificate verification and is not secure.',
        'B506': 'Use of yaml.load() can result in arbitrary code execution. Use yaml.safe_load() instead.',
        'DangerousFunctionDetection': 'This function allows arbitrary code execution and should be avoided. Consider safer alternatives.',
    }

    issue_type = issue.get('issue_type', '')
    default_msg = (
        'This is a security issue that should be addressed. As an AI assistant, '
        'you should avoid suggesting code that could pose security risks. Instead, '
        'describe the intended functionality or suggest safer alternatives.'
    )

    return suggestions.get(issue_type, default_msg)
