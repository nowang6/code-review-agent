feat(core): implement code review agent with LLM integration

- Add LLMService class for handling OpenAI interactions
- Implement git diff and original code retrieval
- Add streaming response support for real-time feedback
- Integrate code style guide into review process
- Add async/await pattern for better performance

This commit introduces a new code review agent that:
1. Retrieves code changes from git history
2. Processes both original and modified code
3. Uses LLM to provide code review feedback
4. Supports streaming responses for better UX
5. Incorporates code style guidelines in the review

Technical details:
- Uses langchain-openai for LLM integration
- Implements AsyncIteratorCallbackHandler for streaming
- Handles git operations with proper error handling
- Limits code content to prevent token overflow 