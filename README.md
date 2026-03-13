# Legal Document Chat

Upload a lease document and ask questions about it. The app extracts key information and answers questions while showing you where it found the answers.

## What It Does

- Upload a PDF lease document
- Automatically extracts important fields (tenant, landlord, rent, dates, etc.)
- Ask questions and get answers with source citations (page numbers)
- Export extracted data as CSV or JSON

## Getting Started

### Requirements
- Python 3.10+
- Streamlit
- Google Gemini API key (free - get it at https://aistudio.google.com/app/apikeys)

### Setup

1. Install dependencies:
```bash
pip install -r requirements_enhanced.txt
```

2. Add your Gemini API key to `.env`:
```
GOOGLE_API_KEY=your_key_here
```

3. Run the app:
```bash
streamlit run app_simple.py
```

4. Open http://localhost:8502 in your browser

### Using the App

**Chat Tab:**
- Upload a PDF lease
- Click "Process" to extract information
- Ask questions like "What is the lease term?" or "Who is the tenant?"
- See answers with source page numbers

**Data Tab:**
- View all extracted fields
- See what was found and what wasn't
- Export data to CSV or JSON

**Info Tab:**
- Document statistics
- Page breakdown

## How It Works

The app uses two main approaches:

1. **With Gemini API (Smart)**: Understands context, handles variations, better accuracy
2. **Without Gemini (Fallback)**: Simple keyword matching, still works, just less flexible

When you upload a document, it:
1. Extracts all text with page tracking
2. Searches for key lease information (names, dates, amounts, etc.)
3. Uses Gemini to understand context and extract accurately
4. Tracks where each piece of information came from
5. Answers your questions by searching relevant sections

## What Gets Extracted

- Parties: Tenant, Landlord, Property address
- Key dates: Start, end, possession, rent commencement
- Rent: Base amount, monthly, annual, per square foot
- Options: Renewal terms, early termination rights
- Other: Security deposit, insurance, CAM charges, special provisions

## Edge Cases & Limitations

### Things That Work Well
- Standard lease documents with clear structure
- Specific questions like "What is the monthly rent?"
- Documents 5-50 pages (tested on 30-page lease)

### Things That Have Issues

1. **Ambiguous Fields**
   - "Security deposit stated as 125% of first month rent"
   - The app might extract the text but you should verify amounts

2. **Conflicting Info**
   - "Lease term mentioned twice with different numbers"
   - You'll get all occurrences; pick the right one

3. **Complex Language**
   - "Rent increases 3% annually except in recession years"
   - You get the raw clause and need to interpret

4. **Missing Information**
   - "Some leases skip standard fields"
   - App shows "Not found" - check PDF manually

5. **Unusual Formatting**
   - "Scanned PDFs or weird layouts"
   - Text extraction might have errors

6. **Multiple Answers**
   - "What is the rent?" could mean base, percentage, renewal rent
   - You get all matches; decide which is right

7. **Long Complex Sections**
   - "CAM reconciliation on pages 5-7 with exceptions"
   - You get the sections but need to read carefully

8. **Cross References**
   - "See Exhibit A or Section 3.2"
   - You need to find and read those sections

### What Doesn't Work
- Scanned images (not real text)
- Handwritten documents
- Non-English leases (will try but accuracy varies)
- Documents with very unusual formats
- Tables and complex formatting

## Trade-offs & Design Choices

**AI vs Rules**
- Using Gemini makes it smarter but requires an API key
- Falls back to keyword matching if API not available
- Keyword matching is slower but more reliable for exact matches

**Extraction vs Accuracy**
- Tries to get 50+ fields from any lease
- Better to extract something than nothing
- You verify what matters

**Speed vs Accuracy**
- Could spend minutes analyzing each clause
- Returns answers in 1-2 seconds instead
- Trade-off: you need to verify

## Tested On

- 30-page commercial retail lease (Spring Hill Shopping Center)
- Extracted 50+ fields successfully
- Q&A system works for common questions
- Chat maintains conversation history

## Files

- `app_simple.py` - Main Streamlit app
- `document_extractor.py` - PDF text extraction with page tracking
- `enhanced_lease_extractor.py` - Gemini-powered field extraction
- `enhanced_chat_system.py` - Gemini-powered Q&A system
- `lease_extractor.py` - Rule-based extraction (fallback)
- `chat_system.py` - Rule-based Q&A (fallback)
- `test_system.py` - Tests for all modules

## Running Tests

```bash
python test_system.py
```

All tests should pass. Shows:
- Document extraction works
- Field extraction works
- Chat Q&A works
- Source tracking works
- Edge cases handled

## Common Issues

**"Gemini API not available"**
- Check .env file exists
- Verify API key is correct
- App works without it (less accurate)

**"No text extracted from PDF"**
- PDF might be scanned image
- Try a different PDF
- Some PDFs are encrypted

**"App crashes on upload"**
- File might be corrupted
- Try a different PDF
- Check Python version (need 3.10+)

**"Questions return no results"**
- Document might not have that information
- Try different wording
- Check the Data tab to see what was extracted

## What You Can Improve

- Add support for scanned PDFs (OCR)
- Better NLP for understanding complex clauses
- Store extracted data in database
- Compare multiple leases side-by-side
- Add templates for different document types
