"""
Document Extraction Module
Handles PDF extraction, preprocessing, and chunking with source tracking.
"""

from PyPDF2 import PdfReader
from typing import List, Dict, Tuple
import re


class DocumentExtractor:
    """Extracts text and metadata from PDF documents."""

    def __init__(self, pdf_path: str):
        """
        Initialize the document extractor.

        Args:
            pdf_path: Path to the PDF file
        """
        self.pdf_path = pdf_path
        self.doc_text = ""
        self.pages_data = []
        self._extract_text()

    def _extract_text(self):
        """Extract text from PDF with page tracking."""
        reader = PdfReader(self.pdf_path)
        full_text = ""

        for page_num, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            self.pages_data.append({
                'page_num': page_num,
                'text': text,
                'length': len(text)
            })
            full_text += f"\n--- PAGE {page_num} ---\n{text}\n"

        self.doc_text = full_text

    def get_full_text(self) -> str:
        """Get the complete document text."""
        return self.doc_text

    def get_page_text(self, page_num: int) -> str:
        """Get text from a specific page."""
        if page_num < 1 or page_num > len(self.pages_data):
            return ""
        return self.pages_data[page_num - 1]['text']

    def find_section_with_source(self, keyword: str, context_lines: int = 3) -> List[Dict]:
        """
        Find sections containing a keyword and return with source info.

        Args:
            keyword: The keyword to search for
            context_lines: Number of lines of context to include

        Returns:
            List of dicts with 'content', 'page', 'section' keys
        """
        results = []
        keyword_lower = keyword.lower()

        for page_data in self.pages_data:
            lines = page_data['text'].split('\n')
            for line_idx, line in enumerate(lines):
                if keyword_lower in line.lower():
                    # Get context
                    start_idx = max(0, line_idx - context_lines)
                    end_idx = min(len(lines), line_idx + context_lines + 1)
                    context = '\n'.join(lines[start_idx:end_idx])

                    results.append({
                        'content': context,
                        'page': page_data['page_num'],
                        'keyword': keyword,
                        'line_num': line_idx + 1
                    })

        return results

    def get_text_with_source_tracking(self, start_page: int = 1, end_page: int = None) -> List[Dict]:
        """
        Get text chunks with source information.

        Args:
            start_page: Starting page number
            end_page: Ending page number (None for all)

        Returns:
            List of text chunks with source info
        """
        if end_page is None:
            end_page = len(self.pages_data)

        chunks = []
        for page_data in self.pages_data:
            if start_page <= page_data['page_num'] <= end_page:
                # Split into sentences while preserving source
                sentences = self._split_into_sentences(page_data['text'])
                for sent_idx, sentence in enumerate(sentences):
                    if sentence.strip():
                        chunks.append({
                            'text': sentence,
                            'page': page_data['page_num'],
                            'section_num': sent_idx,
                            'source': f"Page {page_data['page_num']}, Section {sent_idx + 1}"
                        })

        return chunks

    @staticmethod
    def _split_into_sentences(text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting on periods, exclamation marks, newlines
        sentences = re.split(r'(?<=[.!?\n])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def get_document_stats(self) -> Dict:
        """Get statistics about the document."""
        return {
            'total_pages': len(self.pages_data),
            'total_chars': len(self.doc_text),
            'total_words': len(self.doc_text.split()),
            'avg_page_length': len(self.doc_text) // len(self.pages_data) if self.pages_data else 0
        }


def extract_lease_document(pdf_path: str) -> DocumentExtractor:
    """Convenience function to extract a lease document."""
    return DocumentExtractor(pdf_path)
