#!/bin/bash

# Rebase all open pull request branches onto main
# This script automates the process of rebasing all conflicted PRs

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MAIN_BRANCH="main"
REPO_OWNER="MrWizard94-Compile"
REPO_NAME="Agents-Constitution"

# PR branches to rebase
PR_BRANCHES=(
  "codex/verify-low-level-lifecycle-hooks"
  "codex/distinguish-skill-and-pack-roots"
  "resolve-pack-one-level"
  "skill-evolution-live-entry-20260915"
)

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}PR Rebase Automation Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to print status
print_status() {
  echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

# Function to print success
print_success() {
  echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error
print_error() {
  echo -e "${RED}✗ $1${NC}"
}

# Verify we're in a git repository
if [ ! -d .git ]; then
  print_error "Not in a git repository. Please run this script from the repository root."
  exit 1
fi

# Fetch latest from origin
print_status "Fetching latest from origin..."
git fetch origin
print_success "Fetch complete"
echo ""

# Track successes and failures
SUCCESSFUL=()
FAILED=()
SKIPPED=()

# Process each branch
for branch in "${PR_BRANCHES[@]}"; do
  echo -e "${BLUE}-------------------------------------------${NC}"
  print_status "Processing branch: $branch"
  
  # Check if branch exists
  if ! git rev-parse --verify origin/$branch > /dev/null 2>&1; then
    print_error "Branch $branch does not exist on origin (skipping)"
    SKIPPED+=("$branch")
    continue
  fi
  
  # Check if we're on the branch already
  current_branch=$(git rev-parse --abbrev-ref HEAD)
  if [ "$current_branch" != "$branch" ]; then
    print_status "Checking out $branch..."
    if ! git checkout $branch 2>/dev/null; then
      print_error "Failed to checkout $branch"
      FAILED+=("$branch")
      continue
    fi
  fi
  
  # Update branch from origin
  print_status "Pulling latest changes for $branch..."
  git pull origin $branch --quiet
  
  # Attempt rebase
  print_status "Rebasing $branch onto $MAIN_BRANCH..."
  
  if git rebase origin/$MAIN_BRANCH > /dev/null 2>&1; then
    # Rebase successful
    print_success "Rebase successful for $branch"
    
    # Force push with lease (safer than --force)
    print_status "Force pushing $branch to origin..."
    if git push --force-with-lease origin $branch > /dev/null 2>&1; then
      print_success "Successfully pushed $branch"
      SUCCESSFUL+=("$branch")
    else
      print_error "Failed to push $branch"
      FAILED+=("$branch")
      # Reset to remote state
      git reset --hard origin/$branch
    fi
  else
    # Rebase has conflicts
    print_error "Rebase conflict detected in $branch"
    print_status "Showing conflicted files:"
    git diff --name-only --diff-filter=U
    
    print_status "To manually resolve conflicts:"
    echo "  1. Review conflicts: git diff"
    echo "  2. Stage resolved files: git add <file>"
    echo "  3. Continue rebase: git rebase --continue"
    echo "  4. Or abort: git rebase --abort"
    echo ""
    
    FAILED+=("$branch")
    
    # Reset to remote state to avoid leaving repo in bad state
    print_status "Aborting rebase to leave repo in clean state..."
    git rebase --abort
    git reset --hard origin/$branch
  fi
  echo ""
done

# Return to main branch
print_status "Returning to $MAIN_BRANCH..."
git checkout $MAIN_BRANCH --quiet
git pull origin $MAIN_BRANCH --quiet

# Summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Rebase Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ ${#SUCCESSFUL[@]} -gt 0 ]; then
  echo -e "${GREEN}Successfully rebased (${#SUCCESSFUL[@]}):${NC}"
  for branch in "${SUCCESSFUL[@]}"; do
    echo -e "  ${GREEN}✓${NC} $branch"
  done
  echo ""
fi

if [ ${#FAILED[@]} -gt 0 ]; then
  echo -e "${RED}Failed/Conflicted (${#FAILED[@]}):${NC}"
  for branch in "${FAILED[@]}"; do
    echo -e "  ${RED}✗${NC} $branch (has merge conflicts - manual resolution needed)"
  done
  echo ""
fi

if [ ${#SKIPPED[@]} -gt 0 ]; then
  echo -e "${YELLOW}Skipped (${#SKIPPED[@]}):${NC}"
  for branch in "${SKIPPED[@]}"; do
    echo -e "  ${YELLOW}⊘${NC} $branch (branch not found)"
  done
  echo ""
fi

# Exit status
if [ ${#FAILED[@]} -eq 0 ]; then
  echo -e "${GREEN}All branches processed successfully!${NC}"
  exit 0
else
  echo -e "${YELLOW}Some branches have conflicts requiring manual resolution.${NC}"
  echo -e "${YELLOW}See details above for next steps.${NC}"
  exit 1
fi
