"""
Enhanced Chat System with Gemini API
Provides natural language Q&A with better understanding and formatting
"""

import os
from typing import List, Dict, Tuple, Optional
from document_extractor import DocumentExtractor
from dotenv import load_dotenv

load_dotenv()

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

if GEMINI_AVAILABLE:
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)


class EnhancedChat:
    """
    Enhanced chat system using Gemini for intelligent Q&A.
    Falls back to keyword-based search if API unavailable.
    """

    def __init__(self, document_extractor: DocumentExtractor, use_gemini: bool = True):
        """Initialize enhanced chat."""
        self.doc = document_extractor
        self.use_gemini = use_gemini and GEMINI_AVAILABLE and os.getenv('GOOGLE_API_KEY')
        self.chat_history = []

        if self.use_gemini:
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None

    def answer_question(self, question: str) -> Tuple[str, str, List[Dict]]:
        """
        Answer a question with enhanced formatting.

        Returns:
            Tuple of (full_answer, summary, sources)
        """
        if self.use_gemini:
            return self._answer_with_gemini(question)
        else:
            return self._answer_with_keywords(question)

    def _answer_with_gemini(self, question: str) -> Tuple[str, str, List[Dict]]:
        """Answer using Gemini API."""
        # First, find relevant context from document
        doc_text = self.doc.get_full_text()

        context_prompt = f"""
Given this lease document, provide a clear, concise answer to the question.
Format the answer in a friendly, easy-to-understand way.

LEASE DOCUMENT (excerpt):
{doc_text[:4000]}

QUESTION: {question}

Please provide:
1. A direct, clear answer
2. If information isn't in the document, say so clearly

Keep your answer concise and user-friendly.
"""

        try:
            response = self.model.generate_content(context_prompt)
            full_answer = response.text

            # Find relevant sources
            keywords = self._extract_keywords(question)
            sources = self._find_sources(keywords)

            # Create summary
            summary = full_answer.split('\n')[0] if full_answer else "No answer found"
            if len(summary) > 150:
                summary = summary[:150] + "..."

            # Store in history
            self.chat_history.append({
                'question': question,
                'answer': full_answer,
                'sources': sources,
                'method': 'Gemini'
            })

            return full_answer, summary, sources

        except Exception as e:
            print(f"[!] Gemini failed: {str(e)}")
            return self._answer_with_keywords(question)

    def _answer_with_keywords(self, question: str) -> Tuple[str, str, List[Dict]]:
        """Fallback to keyword-based search."""
        keywords = self._extract_keywords(question)
        sources = self._find_sources(keywords)

        if not sources:
            answer = f"I couldn't find information about '{question}' in the lease document. Try asking about:\n• Lease dates\n• Rent amounts\n• Renewal options\n• Tenant/landlord\n• Security deposit"
            summary = "No information found"
        else:
            # Build answer from sources
            answer_parts = [f"Based on the lease document:\n"]
            for idx, source in enumerate(sources[:3], 1):
                answer_parts.append(f"{idx}. {source['content'][:200]}\n   → Page {source['page']}")

            answer = "\n".join(answer_parts)
            summary = f"Found {len(sources)} relevant section(s)"

        self.chat_history.append({
            'question': question,
            'answer': answer,
            'sources': sources,
            'method': 'Keyword Search'
        })

        return answer, summary, sources

    def _extract_keywords(self, question: str) -> List[str]:
        """Extract meaningful keywords from question."""
        stop_words = {
            'what', 'is', 'the', 'are', 'a', 'an', 'and', 'or', 'but',
            'does', 'do', 'can', 'how', 'when', 'where', 'why', 'which',
            'this', 'that', 'with', 'for', 'to', 'of', 'in', 'on', 'at'
        }

        words = [w.lower() for w in question.split() if w.lower() not in stop_words and len(w) > 2]
        return words[:5]

    def _find_sources(self, keywords: List[str]) -> List[Dict]:
        """Find source citations for keywords."""
        all_results = []

        for keyword in keywords:
            results = self.doc.find_section_with_source(keyword, context_lines=3)
            all_results.extend(results)

        # Deduplicate and sort by page
        unique_results = {}
        for result in all_results:
            key = (result['page'], result['content'][:50])
            if key not in unique_results:
                unique_results[key] = result

        sorted_results = sorted(unique_results.values(), key=lambda x: x['page'])
        return sorted_results[:3]

    def format_answer(self, answer: str) -> str:
        """Format answer for user-friendly display."""
        # Basic formatting - add bullet points and structure
        lines = answer.split('\n')
        formatted = []

        for line in lines:
            if line.strip():
                formatted.append(line)

        return "\n".join(formatted)

    def get_chat_history(self) -> List[Dict]:
        """Get conversation history."""
        return self.chat_history

    def clear_history(self):
        """Clear chat history."""
        self.chat_history = []

    def extraction_mode(self) -> str:
        """Get current extraction mode."""
        if self.use_gemini:
            return "🤖 Powered by Gemini AI"
        else:
            return "📖 Using Keyword Search"

    def suggest_questions(self) -> List[str]:
        """Suggest relevant questions about the lease."""
        return [
            "What is the lease term?",
            "Who is the tenant and landlord?",
            "What is the monthly rent?",
            "When does the lease start and end?",
            "What are the renewal options?",
            "What is the security deposit?",
            "What are the early termination rights?",
            "What insurance is required?",
            "What is the permitted use?",
            "Are there any special provisions?"
        ]
