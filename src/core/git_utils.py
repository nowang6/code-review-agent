import subprocess

def get_original_code(repo_path: str, commit_id: str, max_lines: int = 100) -> str:
    try:
        # Get the parent commit hash
        parent_commit = subprocess.check_output(
            ['git', 'rev-parse', f'{commit_id}^'],
            cwd=repo_path,
            text=True
        ).strip()
        
        # Get the list of changed files
        changed_files = subprocess.check_output(
            ['git', 'diff', '--name-only', parent_commit, commit_id],
            cwd=repo_path,
            text=True
        ).splitlines()
        
        # Get the content of each changed file at the parent commit
        original_contents = []
        for file_path in changed_files:
            if not file_path:  # Skip empty lines
                continue
                
            try:
                content = subprocess.check_output(
                    ['git', 'show', f'{parent_commit}:{file_path}'],
                    cwd=repo_path,
                    text=True
                )
                
                # Count lines and limit if necessary
                lines = content.splitlines()
                if len(lines) > max_lines:
                    content = "\n".join(lines[:max_lines]) + f"\n... (skipped {len(lines) - max_lines} lines)"
                
                original_contents.append(f"File: {file_path}\n```\n{content}\n```\n")
            except subprocess.CalledProcessError:
                # If file didn't exist in parent commit, skip it
                continue
                
        return "\n".join(original_contents)
        
    except subprocess.CalledProcessError as e:
        print(f"Error getting original code: {e}")
        return "Error: Could not retrieve original code"

def get_git_diff(repo_path: str, commit_id: str) -> str:
    try:
        # Get the parent commit hash
        parent_commit = subprocess.check_output(
            ['git', 'rev-parse', f'{commit_id}^'],
            cwd=repo_path,
            text=True
        ).strip()
        
        # Get the diff with context
        diff = subprocess.check_output(
            ['git', 'diff', '-U5', parent_commit, commit_id],
            cwd=repo_path,
            text=True
        )
        
        # If no diff output, it might be a new file
        if not diff:
            # Try to get the new file content
            new_files = subprocess.check_output(
                ['git', 'diff', '--name-only', '--diff-filter=A', parent_commit, commit_id],
                cwd=repo_path,
                text=True
            ).splitlines()
            
            if new_files:
                new_contents = []
                for file_path in new_files:
                    if not file_path:  # Skip empty lines
                        continue
                    try:
                        content = subprocess.check_output(
                            ['git', 'show', f'{commit_id}:{file_path}'],
                            cwd=repo_path,
                            text=True
                        )
                        new_contents.append(f"New file: {file_path}\n```\n{content}\n```\n")
                    except subprocess.CalledProcessError:
                        continue
                return "\n".join(new_contents)
            
        return diff
        
    except subprocess.CalledProcessError as e:
        print(f"Error getting git diff: {e}")
        return "Error: Could not retrieve git diff" 