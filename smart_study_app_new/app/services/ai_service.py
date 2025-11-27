import google.generativeai as genai
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
import json

load_dotenv()

class AIService:
    def __init__(self):
        """Initialize the AI service with Gemini API."""
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    async def _generate_content(self, prompt: str) -> str:
        """Generate content using Gemini API."""
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Error generating content: {str(e)}")

    async def generate_summary(self, text: str) -> str:
        """Generate a concise summary of the provided text."""
        prompt = f"""
        Summarize the following text concisely in 2-3 sentences.
        Focus on the key points and main ideas.
        Return only the summary text, no additional formatting.
        
        Text to summarize:
        {text}
        """
        return await self._generate_content(prompt)

    async def generate_flashcards(self, text: str, num_cards: int = 5) -> List[Dict[str, str]]:
        """Generate flashcards from the provided text."""
        prompt = f"""
        Create {num_cards} flashcards from the following text.
        Each flashcard should have a clear question and answer.
        Return as a JSON array of objects with 'question' and 'answer' keys.
        
        Text for flashcards:
        {text}
        
        Format example:
        [
            {{"question": "What is...", "answer": "It is..."}},
            ...
        ]
        """
        response = await self._generate_content(prompt)
        try:
            # Clean up the response to ensure valid JSON
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            json_str = response[json_start:json_end]
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Fallback to a simple format if JSON parsing fails
            return [{"question": "Could not parse response", "answer": response}]

    async def generate_mcqs(self, text: str, num_questions: int = 3) -> List[Dict[str, Any]]:
        """Generate multiple-choice questions from the provided text."""
        prompt = f"""
        Create {num_questions} multiple-choice questions based on the following text.
        Each question should have 4 options (a, b, c, d) and one correct answer.
        Return as a JSON array of objects with 'question', 'options', and 'correct_answer' keys.
        
        Text for MCQs:
        {text}
        
        Format example:
        [
            {{
                "question": "What is...?",
                "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                "correct_answer": "a"
            }},
            ...
        ]
        """
        response = await self._generate_content(prompt)
        try:
            # Clean up the response to ensure valid JSON
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            json_str = response[json_start:json_end]
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Fallback to a simple format if JSON parsing fails
            return [{"question": "Could not parse response", "options": ["Error"], "correct_answer": "a"}]

    async def generate_explanation(self, text: str, concept: str) -> str:
        """Generate an explanation of a specific concept from the text."""
        prompt = f"""
        Explain the following concept in detail based on the provided text.
        Use clear and simple language, and provide examples if possible.
        
        Concept to explain: {concept}
        
        Text for context:
        {text}
        
        Provide a detailed explanation:
        """
        return await self._generate_content(prompt)

# Singleton instance
ai_service = AIService()
