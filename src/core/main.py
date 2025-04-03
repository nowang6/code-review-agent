import os
from typing import AsyncIterator
from dotenv import load_dotenv
from openai import OpenAI
import textwrap
from src.core.const import system_prompt, code_style_guide
from src.core.git_utils import get_original_code, get_git_diff

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url="https://api.deepseek.com/v1")
model = "deepseek-chat"

class LLMService:
    def get_streaming_response(self, prompt: str):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            raise e

async def main(repo_path: str, commit_id: str):
    llm_service = LLMService()
    
    # Read git diff from file
    with open("data/diff.patch", "r") as f:
        git_diff = f.read()
    
    prompt = textwrap.dedent(f"""
        # Code Review Request

        ## Git Changes
        {git_diff}

        ## Code Style Guide
        {code_style_guide}

        Please review the code changes and provide feedback based on the Code Style Guide.
    """).strip()
    
    print("Response:")
    for chunk in llm_service.get_streaming_response(prompt):
        print(chunk, end="", flush=True)
    print("\n")

if __name__ == "__main__":
    import asyncio
    repo_path = "/Users/niwang/Desktop/code/operator"
    commit_id = "793007efbf56a55019df9ec24d0ad663632d1bc3"
    asyncio.run(main(repo_path, commit_id))
