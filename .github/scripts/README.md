# GitHub Issue Management Scripts

This directory contains scripts to help manage GitHub issues for the task management interview project.

## Setup

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your GitHub Personal Access Token:
   - Go to GitHub > Settings > Developer settings > Personal access tokens
   - Generate a new token with the `repo` scope
   - Export it as an environment variable:
     ```bash
     export GITHUB_TOKEN=your_token_here
     ```

## Creating Issues

To create all the standard interview issues:

```bash
python create_issues.py
```

This will create several issues in the repository, including:
- Setup instructions
- Authentication implementation
- Security fixes
- Feature implementations

## Customizing Issues

Edit the `create_issues.py` file to modify the issues that get created. Each issue is defined with:
- A title
- A detailed body (in Markdown)
- Optional labels

## Notes

- The script will only create issues that don't already exist (based on title)
- Make sure you have write access to the repository
- The script requires Python 3.6+
