from typing import List

class PromptTemplates:
    """Collection of prompt templates for LLM interactions"""
    
    @staticmethod
    def enhance_markdown() -> List[str]:
        return [
            "You are an expert markdown enhancer.",
            "Your task is to improve the clarity and readability of markdown content while preserving its original structure and meaning.",
            "Focus on:",
            "1. Consistent heading hierarchy",
            "2. Clear list formatting",
            "3. Proper code block usage",
            "4. Accurate link references",
            "5. Improved readability"
        ]
    
    @staticmethod
    def validate_markdown() -> List[str]:
        return [
            "You are a markdown validation specialist.",
            "Your task is to analyze markdown content and identify any structural or formatting issues.",
            "Check for:",
            "1. Proper heading hierarchy",
            "2. Valid list formatting",
            "3. Complete code blocks",
            "4. Working link references",
            "5. Image reference validity"
        ] 