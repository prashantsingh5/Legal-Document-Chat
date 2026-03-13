"""
Chat System with Source Attribution
Enables Q&A about the lease document with source citations.
"""

from typing import List, Dict, Tuple, Optional
from document_extractor import DocumentExtractor
import re


class Chat:
    """
    Chat system that answers questions about the lease document
    and provides source attribution.
    """

    def __init__(self, document_extractor: DocumentExtractor):
        """
        Initialize the chat system.

        Args:
            document_extractor: Instance of DocumentExtractor with the lease
        """
        self.doc = document_extractor
        self.chat_history = []
        self.context_window = 5  # Number of lines of context

    def answer_question(self, question: str) -> Tuple[str, str, List[Dict]]:
        """
        Answer a question about the lease with source attribution.

        Args:
            question: The user's question

        Returns:
            Tuple of (answer, summary, sources) where:
            - answer: The detailed answer
            - summary: A brief summary
            - sources: List of source references with page numbers
        """
        # Parse the question to identify key terms
        keywords = self._extract_keywords(question)

        # Search for relevant content
        search_results = self._search_relevant_content(keywords)

        if not search_results:
            return (
                "I couldn't find information about that in the lease document.",
                "Not found",
                []
            )

        # Compile answer from search results
        answer = self._compile_answer(question, search_results)
        summary = self._create_summary(answer)
        sources = self._create_source_list(search_results)

        # Add to chat history
        self.chat_history.append({
            'question': question,
            'answer': answer,
            'sources': sources
        })

        return answer, summary, sources

    def _extract_keywords(self, question: str) -> List[str]:
        """Extract search keywords from the question."""
        # Remove common stop words
        stop_words = {
            'what', 'is', 'the', 'are', 'a', 'an', 'and', 'or', 'but',
            'does', 'do', 'can', 'how', 'when', 'where', 'why', 'with',
            'about', 'for', 'to', 'of', 'in', 'on', 'at', 'by', 'from',
            'as', 'it', 'that', 'who', 'which', 'this', 'that', 'there'
        }

        words = [w.lower() for w in question.split() if w.lower() not in stop_words]
        return words[:5]  # Take first 5 meaningful words

    def _search_relevant_content(self, keywords: List[str]) -> List[Dict]:
        """Search for content relevant to the keywords."""
        all_results = []

        for keyword in keywords:
            results = self.doc.find_section_with_source(keyword, self.context_window)
            all_results.extend(results)

        # Remove duplicates and sort by page
        unique_results = {}
        for result in all_results:
            key = (result['page'], result['content'][:50])
            if key not in unique_results:
                unique_results[key] = result

        sorted_results = sorted(unique_results.values(), key=lambda x: x['page'])
        return sorted_results[:3]  # Return top 3 results

    def _compile_answer(self, question: str, search_results: List[Dict]) -> str:
        """Compile a comprehensive answer from search results."""
        if not search_results:
            return "No relevant information found."

        answer_parts = [
            f"Based on the lease document, here's what I found regarding: {question}\n"
        ]

        for idx, result in enumerate(search_results, 1):
            answer_parts.append(
                f"\n[From Page {result['page']}]:\n{result['content']}\n"
            )

        return "".join(answer_parts)

    def _create_summary(self, answer: str) -> str:
        """Create a brief summary of the answer."""
        # Take first 100-150 characters
        summary = answer.replace('\n', ' ').strip()
        if len(summary) > 150:
            summary = summary[:150] + "..."
        return summary

    def _create_source_list(self, search_results: List[Dict]) -> List[Dict]:
        """Create a formatted source list."""
        sources = []
        for result in search_results:
            sources.append({
                'page': result['page'],
                'keyword': result.get('keyword', 'lease content'),
                'context_start': result['content'][:80] + "..."
            })
        return sources

    def get_chat_history(self) -> List[Dict]:
        """Get the chat history."""
        return self.chat_history

    def clear_history(self):
        """Clear the chat history."""
        self.chat_history = []

    def ask_common_questions(self) -> Dict[str, Tuple[str, List[Dict]]]:
        """
        Answer common questions about the lease.

        Returns:
            Dictionary of common questions and their answers
        """
        common_questions = [
            "What is the lease term?",
            "What is the monthly rent amount?",
            "Who is the tenant and landlord?",
            "What are the renewal options?",
            "What is the security deposit amount?",
            "What are the termination clauses?",
            "What are the tenant's permitted uses?",
            "What insurance is required?",
        ]

        results = {}
        for question in common_questions:
            answer, summary, sources = self.answer_question(question)
            results[question] = (answer, sources)

        return results

    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Perform semantic search on the document.

        Args:
            query: The search query
            top_k: Number of top results to return

        Returns:
            List of relevant sections with sources
        """
        keywords = self._extract_keywords(query)
        doc_text = self.doc.get_full_text()

        # Split into chunks
        chunks = doc_text.split('\n--- PAGE ')
        results = []

        for chunk in chunks:
            lines = chunk.split('\n')
            page_match = re.match(r'^(\d+)', lines[0]) if lines else None
            page_num = int(page_match.group(1)) if page_match else 1

            # Score based on keyword matches
            content = ' '.join(lines[1:])  # Skip page marker
            score = sum(content.lower().count(kw.lower()) for kw in keywords)

            if score > 0:
                results.append({
                    'content': content[:500],
                    'page': page_num,
                    'relevance_score': score,
                    'source': f"Page {page_num}"
                })

        # Sort by relevance and return top k
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:top_k]
