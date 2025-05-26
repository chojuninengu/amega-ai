from typing import List, Dict, Optional
import difflib
from pathlib import Path

class PRReviewer:
    def __init__(self, llm_manager):
        """Initialize PR Reviewer with LLM manager."""
        self.llm_manager = llm_manager
        
    async def review_changes(self, diff_content: str) -> Dict:
        """
        Review the changes in a pull request and provide suggestions.
        
        Args:
            diff_content (str): The git diff content to review
            
        Returns:
            Dict containing review comments and suggestions
        """
        # Prepare the prompt for the LLM
        prompt = self._prepare_review_prompt(diff_content)
        
        # Get review comments from LLM
        review_response = await self.llm_manager.generate_response(
            prompt,
            max_length=1000,
            temperature=0.7
        )
        
        return self._parse_review_response(review_response)
    
    def _prepare_review_prompt(self, diff_content: str) -> str:
        """Prepare the prompt for the LLM to review the code changes."""
        return f"""Please review the following code changes and provide:
1. Potential issues or bugs
2. Code style improvements
3. Performance considerations
4. Security concerns
5. Suggested improvements

Changes to review:
{diff_content}

Format your response as:
ISSUES:
- [List any potential issues found]

STYLE:
- [List style improvements]

PERFORMANCE:
- [List performance considerations]

SECURITY:
- [List security concerns]

SUGGESTIONS:
- [List specific improvement suggestions]
"""
    
    def _parse_review_response(self, response: str) -> Dict:
        """Parse the LLM response into structured feedback."""
        sections = {
            'ISSUES': [],
            'STYLE': [],
            'PERFORMANCE': [],
            'SECURITY': [],
            'SUGGESTIONS': []
        }
        
        current_section = None
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.endswith(':') and line.rstrip(':').upper() in sections:
                current_section = line.rstrip(':').upper()
            elif current_section and line.startswith('-'):
                sections[current_section].append(line[1:].strip())
                
        return sections
    
    async def suggest_improvements(self, file_content: str) -> Dict:
        """
        Suggest specific code improvements for a given file.
        
        Args:
            file_content (str): The content of the file to improve
            
        Returns:
            Dict containing suggested improvements
        """
        prompt = f"""Please suggest improvements for the following code:

{file_content}

Focus on:
1. Code organization
2. Best practices
3. Performance optimizations
4. Error handling
5. Documentation

Provide specific, actionable suggestions."""

        suggestions = await self.llm_manager.generate_response(
            prompt,
            max_length=800,
            temperature=0.7
        )
        
        return {'suggestions': suggestions.split('\n')} 