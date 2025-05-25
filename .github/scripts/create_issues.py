import os
import requests
from typing import List, Dict

# GitHub API configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_OWNER = 'pai-interviews'
REPO_NAME = 'task-management-interview'

# Headers for GitHub API
headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

def create_issue(title: str, body: str, labels: List[str] = None) -> None:
    """Create a new GitHub issue."""
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues'
    data = {
        'title': title,
        'body': body,
        'labels': labels or []
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        print(f"Created issue: {title}")
    else:
        print(f"Failed to create issue {title}: {response.text}")

def main():
    # Define the issues to create
    issues = [
        {
            'title': 'Setup Development Environment',
            'body': """## Task: Set up the development environment

### Description
Set up the development environment for the task management system. This includes:
- Installing Python 3.10+
- Setting up a virtual environment
- Installing backend dependencies
- Setting up the database

### Acceptance Criteria
- [ ] Virtual environment is created and activated
- [ ] All dependencies from requirements.txt are installed
- [ ] Database is properly configured
- [ ] Server can be started locally

### Notes
- Refer to the README for setup instructions
- Make sure to use Python 3.10 or higher""",
            'labels': ['good first issue', 'documentation']
        },
        {
            'title': 'Implement Authentication Middleware',
            'body': """## Task: Implement Authentication Middleware

### Description
Implement JWT-based authentication middleware for the API endpoints.

### Acceptance Criteria
- [ ] JWT token validation middleware is implemented
- [ ] Protected routes require valid tokens
- [ ] Token refresh mechanism is in place
- [ ] Unit tests for authentication

### Technical Notes
- Use PyJWT for JWT implementation
- Store secret key in environment variables
- Implement proper error handling""",
            'labels': ['backend', 'security']
        },
        {
            'title': 'Fix SQL Injection in Task Endpoint',
            'body': """## Bug: SQL Injection Vulnerability

### Description
There is a potential SQL injection vulnerability in the task retrieval endpoint.

### Steps to Reproduce
1. Make a GET request to `/api/tasks?status=' OR '1'='1`
2. Observe that the query returns all tasks instead of filtering by status

### Expected Behavior
- The endpoint should properly sanitize input
- Only return tasks matching the provided status

### Technical Details
- File: `backend/app/api/v1/endpoints/tasks.py`
- Function: `read_tasks`

### Acceptance Criteria
- [ ] Input is properly sanitized
- [ ] SQL injection is prevented
- [ ] Unit tests verify the fix""",
            'labels': ['bug', 'security', 'backend']
        },
        {
            'title': 'Implement Rate Limiting',
            'body': """## Task: Implement Rate Limiting

### Description
Add rate limiting to prevent abuse of the API endpoints.

### Acceptance Criteria
- [ ] Rate limiting is applied to all endpoints
- [ ] Configuration allows for different limits per endpoint
- [ ] Proper HTTP headers are set (X-RateLimit-*) 
- [ ] Tests verify rate limiting works

### Technical Notes
- Use FastAPI's built-in rate limiting or a library like slowapi
- Consider different limits for authenticated vs unauthenticated users""",
            'labels': ['backend', 'security']
        },
        {
            'title': 'Add Input Validation',
            'body': """## Task: Add Input Validation

### Description
Implement proper input validation for all API endpoints.

### Acceptance Criteria
- [ ] All endpoints validate input data
- [ ] Proper error messages are returned for invalid input
- [ ] Validation rules are documented
- [ ] Tests cover edge cases

### Technical Notes
- Use Pydantic models for request/response validation
- Consider using regex for complex validations
- Document validation rules in OpenAPI/Swagger""",
            'labels': ['backend', 'documentation']
        }
    ]

    # Create each issue
    for issue in issues:
        create_issue(issue['title'], issue['body'], issue.get('labels', []))

if __name__ == "__main__":
    if not GITHUB_TOKEN:
        print("Error: GITHUB_TOKEN environment variable is not set")
        print("Please set it with: export GITHUB_TOKEN=your_github_token")
        exit(1)
    main()
