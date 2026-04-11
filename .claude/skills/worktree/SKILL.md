---
name: worktree
description: Create and manage git worktrees for running multiple Claude agents in parallel within the same project. Use when the user wants parallel work, isolated changes, or an experiment they can roll back.
---

# Git Worktree Manager

Manage isolated working copies of a project using git worktree. This allows multiple Claude agents to work in parallel within the same project without interfering with each other.

## When to Activate

- The user says: "create a worktree", "work in a separate branch", "do this in isolation"
- The user wants parallel work: "do X and Y in parallel", "run this separately"
- The user wants an experiment they can roll back: "try this, but make it reversible"
- The user says: "merge worktree", "delete worktree", "show worktrees", "list worktrees"

## Operations

### 1. Create a Worktree

**Argument:** `$ARGUMENTS` = worktree name (for example: `research`, `content`, `experiment`)

```bash
# Ensure .claude/worktrees/ is listed in .gitignore
grep -q '.claude/worktrees/' .gitignore 2>/dev/null || echo '.claude/worktrees/' >> .gitignore

# Create the worktree with its own branch
git worktree add .claude/worktrees/$ARGUMENTS -b worktree-$ARGUMENTS
```

After creating, inform the user:
```
Worktree "$ARGUMENTS" has been created.
- Folder: .claude/worktrees/$ARGUMENTS/
- Branch: worktree-$ARGUMENTS
- All file operations will now take place inside this folder.

When finished, say "merge worktree $ARGUMENTS" to bring the changes into the main project.
```

**After creation — switch all work to the worktree:**
- Perform ALL file operations through the path `.claude/worktrees/$ARGUMENTS/`
- Read files from: `.claude/worktrees/$ARGUMENTS/path/to/file`
- Write files to: `.claude/worktrees/$ARGUMENTS/path/to/file`
- Run scripts with: `cd .claude/worktrees/$ARGUMENTS && python3 execution/...`
- Do not modify files in the project root

### 2. List All Worktrees

```bash
git worktree list
```

### 3. Merge a Worktree

**Argument:** `$ARGUMENTS` = name of the worktree to merge

```bash
# 1. Commit any uncommitted changes in the worktree
cd .claude/worktrees/$ARGUMENTS && git add -A && git status
```

If there are changes to commit:
```bash
cd .claude/worktrees/$ARGUMENTS && git commit -m "worktree $ARGUMENTS: description of changes"
```

```bash
# 2. Return to the project root and merge
cd <project_root> && git merge worktree-$ARGUMENTS --no-edit
```

If a merge conflict occurs, notify the user and assist in resolving it.

After a successful merge, ask: "Delete worktree $ARGUMENTS? The changes are already in the main branch."

### 4. Delete a Worktree

**Argument:** `$ARGUMENTS` = name of the worktree to delete

```bash
git worktree remove .claude/worktrees/$ARGUMENTS
git branch -d worktree-$ARGUMENTS
```

## Rules for Working Inside a Worktree

1. **All paths** must go through `.claude/worktrees/<name>/` — never through the project root
2. **Scripts** must be run with `cd .claude/worktrees/<name> && python3 ...`
3. **Output files** should be written to `.claude/worktrees/<name>/tmp/...`
4. **Commit frequently** — small, focused commits produce cleaner merges
5. **Do not touch the root** — work only within your assigned worktree
6. **CLAUDE.md and skills** are read from the project root and are shared across all worktrees

## Error Handling

| Error | Resolution |
|-------|-----------|
| `fatal: is not a git repository` | The project has not been initialised as a git repository. Run `git init` first. |
| `fatal: '$ARGUMENTS' is already checked out` | A worktree with this name already exists. Run `git worktree list` to review. |
| `error: branch 'worktree-X' not found` | The branch has already been deleted. Remove the directory manually: `rm -rf .claude/worktrees/X` |
| Merge conflict | Display the conflicting files, help the user resolve them, then run `git add` followed by `git commit`. |
