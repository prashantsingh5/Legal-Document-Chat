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
