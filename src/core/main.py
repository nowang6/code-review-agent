import os
from typing import AsyncIterator
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.callbacks import AsyncIteratorCallbackHandler
from src.core.const import system_prompt, code_style_guide
import subprocess

load_dotenv()
model = "deepseek-chat"

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

class LLMService:
    def create_prompt(self, template: str) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", template)
        ])
    
    async def get_streaming_response(self, prompt: str) -> AsyncIterator[str]:
        """Get a streaming response from the LLM for the given prompt."""
        callback_handler = AsyncIteratorCallbackHandler()
        
        # Create streaming-enabled LLM instance
        streaming_llm = ChatOpenAI(
            model=model,
            temperature=0.7,
            streaming=True,
            callbacks=[callback_handler]
        )
        
        prompt_template = self.create_prompt(prompt)
        chain = prompt_template | streaming_llm | StrOutputParser()
        
        # Start the chain running in the background
        task = asyncio.create_task(chain.ainvoke({"input": prompt}))
        
        try:
            async for token in callback_handler.aiter():
                yield token
                
            # Make sure to complete the chain
            await task
        except Exception as e:
            # Cancel the task if something goes wrong
            task.cancel()
            raise e

async def main(repo_path: str, commit_id: str):
    # Initialize the service
    llm_service = LLMService()
    
    original_code = get_original_code(repo_path, commit_id)
    git_diff = get_git_diff(repo_path, commit_id)
    
    prompt = f"""
# Code Review Request

## Original Code
{original_code}

## Git Changes
{git_diff}

## Code Style Guide
{code_style_guide}

Please review the code changes and provide feedback based on the Code Style Guide."""
    
    print("Response:")
    async for chunk in llm_service.get_streaming_response(prompt):
        print(chunk, end="", flush=True)
    print("\n")

if __name__ == "__main__":
    import asyncio
    repo_path = "/Users/niwang/Desktop/code/operator"
    commit_id = "793007efbf56a55019df9ec24d0ad663632d1bc3"
    asyncio.run(main(repo_path, commit_id))
