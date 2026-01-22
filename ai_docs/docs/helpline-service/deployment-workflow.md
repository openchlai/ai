# Deployment Workflow

Complete guide to the Git-based deployment workflow for Helpline Service.

## Overview

```
Developer Branch → Dev Branch → Staging Deploy → Code Review → Main Branch → Production
```

The deployment workflow follows these principles:
- **Feature branches** for development
- **Dev branch** as integration point
- **Automatic staging deployment** on dev merge
- **Code review** before production
- **Staging access** for testing: `http://192.168.10.119/helpline`

## Step-by-Step Guide for Contributors

### 1. Clone the Repository

```bash
# Clone the repository
git clone https://github.com/openchlai/ai.git
cd ai/helplinev1

# Verify you're on the main branch
git branch -a
```

### 2. Create Your Feature Branch

```bash
# Update main branch
git checkout main
git pull origin main

# Create a feature branch
git checkout -b feature/your-feature-name

# OR for bug fixes
git checkout -b bugfix/issue-description

# OR for documentation
git checkout -b docs/documentation-update
```

**Branch Naming Conventions:**
- `feature/` - New features
- `bugfix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions

### 3. Make Your Changes

```bash
# Make changes to your files
# ... edit files ...

# Test locally
docker-compose up -d
docker-compose logs -f

# Verify everything works
# Test the application
# Run tests
```

### 4. Commit Your Changes

```bash
# Check what you changed
git status

# Stage files
git add .
# or selectively
git add specific-file.php

# Commit with descriptive message
git commit -m "Add feature: description of what you did"

# Good commit messages:
# - "Add email notifications for new cases"
# - "Fix SQL injection vulnerability in search"
# - "Update documentation for API v2"
# - "Refactor user authentication module"
```

**Commit Message Best Practices:**
- Use present tense ("Add feature" not "Added feature")
- Be specific about what changed
- Reference issue numbers: "Fix #123 - Add export to CSV"
- Keep first line under 50 characters
- Add more details in description if needed

### 5. Push to Your Branch

```bash
# Push your feature branch
git push origin feature/your-feature-name

# If branch doesn't exist yet on remote
git push -u origin feature/your-feature-name

# Verify it's pushed
git branch -r
# Should show: origin/feature/your-feature-name
```

### 6. Create a Pull Request

**Via GitHub:**

1. Go to https://github.com/openchlai/ai
2. You'll see a prompt about your recently pushed branch
3. Click **"Compare & pull request"**
4. **Base branch**: Select `dev` (NOT `main`)
5. **Compare branch**: Your feature branch
6. Fill in the PR description:

```markdown
## Description
Brief description of what this PR does

## Changes
- Change 1
- Change 2
- Change 3

## Testing
- [ ] Tested locally with docker-compose
- [ ] No breaking changes
- [ ] Database migrations tested

## Checklist
- [ ] Code follows project style
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No console errors/warnings
```

7. Click **"Create pull request"**

### 7. Review Process

**Automated Checks:**
- Syntax validation
- Code style checks
- Security scanning
- Unit tests

**Manual Review:**
- Code review by maintainers
- Feedback and discussion
- Requested changes
- Approval

**What to do if changes are requested:**

```bash
# Make the requested changes locally
# ... edit files ...

# Commit with descriptive message
git commit -m "Address review feedback: description"

# Push to the same branch
git push origin feature/your-feature-name

# The PR automatically updates with new commits
```

### 8. Merge to Dev

Once approved, maintainers will merge your PR to `dev` branch.

```bash
# After merge, your branch is merged to dev
# This is done through GitHub's merge button
```

### 9. Automatic Staging Deployment

**Immediately after merge to dev:**

1. GitHub Actions CI/CD pipeline runs
2. Code is automatically tested
3. Docker image is built
4. Service deployed to staging

**Access staging deployment:**
```
http://192.168.10.119/helpline
```

**Verify staging deployment:**
```bash
# SSH into staging server (if you have access)
ssh user@192.168.10.119

# Check deployment status
docker ps | grep helpline

# View logs
docker logs helpline-nginx
docker logs helpline-php
```

### 10. Test in Staging

After your PR is merged and deployed to staging:

1. Access http://192.168.10.119/helpline
2. Test your changes thoroughly
3. Verify no breaking changes
4. Check database migrations worked
5. Validate API endpoints if applicable

**If issues are found:**
```bash
# Create a new PR to dev with fixes
git checkout -b bugfix/staging-issue
# ... make fixes ...
git push origin bugfix/staging-issue
# Create PR to dev
```

## Complete Workflow Example

```bash
# 1. Clone and setup
git clone https://github.com/openchlai/ai.git
cd ai/helplinev1

# 2. Create feature branch
git checkout -b feature/add-export-csv

# 3. Make changes
# Edit application files...
# Update tests...
# Update documentation...

# 4. Test locally
docker-compose up -d
# Test the feature in browser
# Verify API works
# Check database

# 5. Commit
git add .
git commit -m "Add CSV export feature for cases"

# 6. Push to remote
git push -u origin feature/add-export-csv

# 7. Go to GitHub and create PR
# - Base: dev
# - Compare: feature/add-export-csv
# - Add description

# 8. Wait for checks to pass
# - Code review from team
# - Address feedback if needed

# 9. After approval, maintainer merges
# - Automatic deployment to staging

# 10. Test in staging
# - Access http://192.168.10.119/helpline
# - Verify CSV export works
# - Check other features still work

# 11. After staging validation
# - Move forward for production release
# - Or report issues for fixes
```

## Cleaning Up

After your PR is merged:

```bash
# Switch back to main
git checkout main

# Update main locally
git pull origin main

# Delete your local feature branch
git branch -d feature/your-feature-name

# Delete remote feature branch
git push origin --delete feature/your-feature-name

# List remaining branches
git branch -a
```

## Common Issues

### PR is against wrong base branch

```bash
# If PR is to main instead of dev:
# Edit PR on GitHub to change base to dev
# Or create a new PR with correct base
```

### Merge conflicts

```bash
# Update your branch with latest dev
git fetch origin
git merge origin/dev

# Resolve conflicts in editor
# Stage resolved files
git add .

# Complete merge
git commit -m "Resolve merge conflicts"
git push origin feature/your-feature-name

# PR automatically updates
```

### Need to make changes after PR

```bash
# Make changes locally
# ... edit files ...

# Commit and push to same branch
git commit -m "Address feedback"
git push origin feature/your-feature-name

# PR automatically updates with new commits
```

### Want to cancel/close PR

```bash
# Go to GitHub PR page
# Click "Close pull request" button
# Optionally delete the branch
```

## Production Deployment

Production deployment follows a separate process:

1. **Code Review**: All code reviewed and approved
2. **Testing**: Thoroughly tested in staging
3. **Release Branch**: Created from main
4. **Version Bump**: Update version numbers
5. **Release Notes**: Document changes
6. **Tag Release**: Git tag created
7. **Deploy**: Production deployment triggered
8. **Monitor**: Watch for issues

**Production deployments happen less frequently** and are coordinated by the team lead.

## Git Commands Reference

```bash
# View branch status
git status

# List branches
git branch -a

# Create and switch to branch
git checkout -b new-branch

# Switch branches
git checkout existing-branch

# View commit history
git log --oneline

# View changes
git diff
git diff origin/dev

# Undo uncommitted changes
git restore file.php

# Undo last commit (keep changes)
git reset --soft HEAD~1

# See what changed in remote
git fetch origin
git log origin/dev -1
```

## Questions or Issues?

- Open an issue on GitHub
- Ask in team chat
- Contact maintainers
- Check documentation

## Resources

- [Git Basics](https://git-scm.com/book/en/v2/Getting-Started-Git-Basics)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [Commit Messages](https://chris.beams.io/posts/git-commit/)
- [Code Review Best Practices](https://smartbear.com/blog/develop/best-practices-for-code-review/)
