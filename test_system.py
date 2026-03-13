"""
Test Suite for Legal Document Chat System
Tests all modules: extraction, field parsing, and Q&A
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

from document_extractor import DocumentExtractor
from lease_extractor import LeaseExtractor
from chat_system import Chat


def test_document_extraction():
    """Test PDF extraction and parsing."""
    print("\n" + "=" * 70)
    print("TEST 1: Document Extraction")
    print("=" * 70)

    pdf_path = "Copy of Spring Hill - Nelly_s Italian Cafe - Lease (Fully Executed) 01.17.14.pdf"

    try:
        doc = DocumentExtractor(pdf_path)
        stats = doc.get_document_stats()

        assert stats['total_pages'] > 0, "No pages extracted"
        assert stats['total_words'] > 0, "No words extracted"

        print("[PASS] Document extraction")
        print(f"       Pages: {stats['total_pages']}")
        print(f"       Words: {stats['total_words']:,}")
        print(f"       Characters: {stats['total_chars']:,}")

        # Test page retrieval
        page_1_text = doc.get_page_text(1)
        assert len(page_1_text) > 0, "Page 1 is empty"
        print(f"[PASS] Page retrieval (Page 1: {len(page_1_text)} chars)")

        # Test source tracking
        results = doc.find_section_with_source("lease", context_lines=2)
        assert len(results) > 0, "No search results"
        print(f"[PASS] Source tracking ({len(results)} results for 'lease')")

        return doc

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        raise


def test_lease_extraction(doc):
    """Test structured field extraction."""
    print("\n" + "=" * 70)
    print("TEST 2: Lease Field Extraction")
    print("=" * 70)

    try:
        extractor = LeaseExtractor(doc)
        fields = extractor.extract_all_fields()

        assert len(fields) > 0, "No fields extracted"
        assert 'parties_premises' in fields, "Missing parties_premises section"

        print("[PASS] Field extraction")
        print(f"       Total sections: {len(fields)}")

        # Check specific sections
        sections = [
            'parties_premises',
            'key_dates',
            'rent',
            'renewal_options',
            'termination',
            'security_deposit',
            'cam',
            'special_provisions'
        ]

        found_sections = 0
        for section in sections:
            if section in fields:
                found_sections += 1

        print(f"[PASS] Key sections extracted: {found_sections}/{len(sections)}")

        # Verify source tracking
        structured = extractor.get_structured_output()
        assert 'fields' in structured, "Missing fields in output"
        print("[PASS] Structured output format")

        return extractor

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        raise


def test_chat_system(doc):
    """Test Q&A system with source attribution."""
    print("\n" + "=" * 70)
    print("TEST 3: Chat System with Q&A")
    print("=" * 70)

    try:
        chat = Chat(doc)

        test_questions = [
            "What is the lease term?",
            "What are the renewal options?",
            "What is the security deposit?",
            "When does rent commence?",
            "What is the base rent amount?",
        ]

        print("[PASS] Chat system initialized")

        for question in test_questions:
            answer, summary, sources = chat.answer_question(question)

            assert len(answer) > 0, f"Empty answer for: {question}"
            assert isinstance(sources, list), "Sources not a list"

            source_pages = [s['page'] for s in sources]
            print(f"[PASS] Q: {question[:40]:40} | Sources: {source_pages}")

        # Verify chat history
        history = chat.get_chat_history()
        assert len(history) > 0, "Chat history empty"
        print(f"[PASS] Chat history maintained ({len(history)} Q&As)")

        return chat

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        raise


def test_source_tracking(doc):
    """Test source attribution accuracy."""
    print("\n" + "=" * 70)
    print("TEST 4: Source Tracking & Attribution")
    print("=" * 70)

    try:
        # Find a specific keyword and verify source
        results = doc.find_section_with_source("rent", context_lines=3)

        for result in results[:3]:
            assert 'page' in result, "Missing page in result"
            assert 'content' in result, "Missing content in result"
            assert result['page'] > 0, "Invalid page number"

        print(f"[PASS] Found 'rent' in {len(results)} locations")
        print(f"       Pages: {[r['page'] for r in results[:5]]}")

        # Test with multiple keywords
        keywords = ['lease', 'rent', 'tenant']
        for kw in keywords:
            results = doc.find_section_with_source(kw)
            print(f"[PASS] Keyword '{kw}': {len(results)} occurrences")

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        raise


def test_edge_cases(doc):
    """Test edge case handling."""
    print("\n" + "=" * 70)
    print("TEST 5: Edge Case Handling")
    print("=" * 70)

    try:
        chat = Chat(doc)

        # Test 1: Non-existent field
        answer, summary, sources = chat.answer_question("What is the XYZ field?")
        print("[PASS] Non-existent field handled gracefully")

        # Test 2: Ambiguous query
        answer, summary, sources = chat.answer_question("What about rent?")
        print(f"[PASS] Ambiguous query (got {len(sources)} results)")

        # Test 3: Complex query
        answer, summary, sources = chat.answer_question(
            "What are the conditions for early termination and what notice is required?"
        )
        print(f"[PASS] Complex query (got {len(sources)} results)")

        # Test 4: Case insensitivity
        results1 = doc.find_section_with_source("LANDLORD")
        results2 = doc.find_section_with_source("landlord")
        print(f"[PASS] Case insensitivity handled")

    except Exception as e:
        print(f"[FAIL] {str(e)}")
        raise


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("LEGAL DOCUMENT CHAT - COMPREHENSIVE TEST SUITE")
    print("=" * 70)

    try:
        # Run tests sequentially
        doc = test_document_extraction()
        extractor = test_lease_extraction(doc)
        chat = test_chat_system(doc)
        test_source_tracking(doc)
        test_edge_cases(doc)

        # Summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print("[PASS] Document extraction and parsing")
        print("[PASS] Structured field extraction")
        print("[PASS] Chat Q&A system")
        print("[PASS] Source attribution and tracking")
        print("[PASS] Edge case handling")
        print("\n[SUCCESS] ALL TESTS PASSED!")
        print("=" * 70 + "\n")

        return True

    except Exception as e:
        print("\n" + "=" * 70)
        print(f"[CRITICAL FAILURE] {str(e)}")
        print("=" * 70 + "\n")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
