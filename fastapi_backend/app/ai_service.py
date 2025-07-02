import os
from typing import List, Dict, Any, Optional
from .config import settings
from .file_service import file_service


class AIService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.client = None
        self.model = "gpt-4o-mini"  # Using GPT-4o-mini for cost efficiency

        if self.api_key:
            try:
                from openai import OpenAI

                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                print("OpenAI package not installed. Install with: pip install openai")
                self.client = None

    async def generate_doc_suggestions(
        self, query: str, doc_content: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate documentation update suggestions using OpenAI API.

        Args:
            query: User's natural language query about what to update
            doc_content: Optional documentation content to analyze

        Returns:
            List of suggestion dictionaries
        """
        if not self.client:
            print("OpenAI client not available. Using fallback suggestions.")
            return self._get_fallback_suggestions(query)

        try:
            # Get relevant documentation sections
            relevant_sections = file_service.find_relevant_sections(query)

            # Build context from relevant sections
            context = self._build_context(relevant_sections)

            # Build the prompt
            system_prompt = """You are an expert technical writer and documentation specialist. 
            Your task is to analyze documentation update requests and provide specific, actionable suggestions.
            
            For each suggestion, provide:
            - A clear description of what needs to be changed
            - The specific section or area that needs updating
            - The rationale for the change
            - The file path where the change should be made (if you can determine it)
            
            Format your response as a JSON array of objects with these fields:
            - id: unique identifier (number)
            - section: the section name or area
            - suggestion: detailed description of the suggested change
            - file_path: suggested file path (if applicable)
            - line_number: suggested line number (if applicable)
            
            Be specific and actionable in your suggestions. If you can identify specific files or sections that need updating, include that information."""

            user_prompt = f"""
            User Query: {query}
            
            Relevant Documentation Context:
            {context if context else 'No specific documentation content found.'}
            
            Please provide suggestions for updating the documentation based on this query.
            Focus on the most relevant sections and provide specific, actionable recommendations.
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=1000,
            )

            # Parse the response
            content = response.choices[0].message.content
            suggestions = self._parse_suggestions(content)

            # Enhance suggestions with file paths if available
            suggestions = self._enhance_suggestions_with_files(
                suggestions, relevant_sections
            )

            return suggestions

        except Exception as e:
            print(f"Error generating suggestions: {e}")
            # Return fallback suggestions
            return self._get_fallback_suggestions(query)

    def _build_context(self, relevant_sections: List[Dict[str, Any]]) -> str:
        """
        Build context string from relevant sections.
        """
        if not relevant_sections:
            return ""

        context_parts = []
        for item in relevant_sections[:5]:  # Limit to top 5 most relevant
            file_path = item["file_path"]
            section = item["section"]
            context_parts.append(f"File: {file_path}")
            context_parts.append(f"Section: {section['title']}")
            context_parts.append(
                f"Content: {section['content'][:200]}..."
            )  # Truncate for token efficiency
            context_parts.append("---")

        return "\n".join(context_parts)

    def _enhance_suggestions_with_files(
        self, suggestions: List[Dict[str, Any]], relevant_sections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Enhance suggestions with file paths from relevant sections.
        """
        # Create a mapping of section titles to file paths
        section_to_file = {}
        for item in relevant_sections:
            section_to_file[item["section"]["title"].lower()] = item["file_path"]

        for suggestion in suggestions:
            section_title = suggestion.get("section", "").lower()
            if section_title in section_to_file and not suggestion.get("file_path"):
                suggestion["file_path"] = section_to_file[section_title]

        return suggestions

    def _parse_suggestions(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse the AI response into structured suggestions.
        """
        try:
            # Try to extract JSON from the response
            import json
            import re

            # Look for JSON in the response
            json_match = re.search(r"\[.*\]", content, re.DOTALL)
            if json_match:
                suggestions = json.loads(json_match.group())
                return suggestions

            # If no JSON found, create structured suggestions from text
            return self._parse_text_suggestions(content)

        except Exception as e:
            print(f"Error parsing suggestions: {e}")
            return self._get_fallback_suggestions("general update")

    def _parse_text_suggestions(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse text-based suggestions when JSON parsing fails.
        """
        suggestions = []
        lines = content.split("\n")
        current_suggestion = None

        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith(("1.", "2.", "3.", "4.", "5.")) or line.startswith("-"):
                if current_suggestion:
                    suggestions.append(current_suggestion)

                current_suggestion = {
                    "id": len(suggestions) + 1,
                    "section": "General",
                    "suggestion": (
                        line[line.find(".") + 1 :].strip()
                        if "." in line
                        else line[1:].strip()
                    ),
                    "file_path": None,
                    "line_number": None,
                }
            elif current_suggestion and line:
                current_suggestion["suggestion"] += " " + line

        if current_suggestion:
            suggestions.append(current_suggestion)

        return (
            suggestions
            if suggestions
            else self._get_fallback_suggestions("general update")
        )

    def _get_fallback_suggestions(self, query: str) -> List[Dict[str, Any]]:
        """
        Provide fallback suggestions when AI service fails.
        """
        return [
            {
                "id": 1,
                "section": "General",
                "suggestion": f"Review and update documentation based on: {query}",
                "file_path": "README.md",
                "line_number": None,
            },
            {
                "id": 2,
                "section": "Usage",
                "suggestion": "Update usage examples and code snippets to reflect the changes mentioned in the query.",
                "file_path": "docs/usage.md",
                "line_number": None,
            },
        ]


# Global AI service instance
ai_service = AIService()
