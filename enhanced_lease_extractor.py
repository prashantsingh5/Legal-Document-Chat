"""
Enhanced Lease Extractor with Gemini API
Uses Google's Gemini for intelligent field extraction and better accuracy
"""

import os
from typing import Dict, Optional, Tuple
from document_extractor import DocumentExtractor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Configure Gemini if available
if GEMINI_AVAILABLE:
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)


class EnhancedLeaseExtractor:
    """
    Enhanced lease extractor using Gemini API for intelligent extraction.
    Falls back to keyword-based extraction if API unavailable.
    """

    def __init__(self, document_extractor: DocumentExtractor, use_gemini: bool = True):
        """Initialize enhanced extractor."""
        self.doc = document_extractor
        self.use_gemini = use_gemini and GEMINI_AVAILABLE and os.getenv('GOOGLE_API_KEY')
        self.extracted_fields = {}
        self.field_sources = {}

        if self.use_gemini:
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None

    def extract_all_fields(self) -> Dict:
        """Extract all lease fields using Gemini or fallback to rules."""
        if self.use_gemini:
            return self._extract_with_gemini()
        else:
            return self._extract_with_rules()

    def _extract_with_gemini(self) -> Dict:
        """Extract fields using Gemini API."""
        print("[*] Using Gemini API for extraction...")

        doc_text = self.doc.get_full_text()[:5000]  # First 5000 chars for context

        extraction_prompt = f"""
You are a commercial real estate expert analyzing a lease agreement.
Extract the following key information from this lease document and provide ONLY the extracted information in a structured format.

LEASE DOCUMENT:
{doc_text}

Please extract and provide in this EXACT format (use "Not found" if information is not available):

TENANT: [tenant name]
LANDLORD: [landlord name]
PROPERTY ADDRESS: [full address]
LEASE START DATE: [date]
LEASE END DATE: [date]
LEASE TERM: [months/years]
MONTHLY RENT: [amount]
ANNUAL RENT: [amount]
SECURITY DEPOSIT: [amount]
RENEWAL OPTIONS: [details or "Not found"]
EARLY TERMINATION: [details or "Not found"]
PERMITTED USE: [use details or "Not found"]
INSURANCE REQUIRED: [insurance types or "Not found"]
CAM CHARGES: [details or "Not found"]
SPECIAL PROVISIONS: [key provisions or "Not found"]

Format your response clearly with each field on a new line.
"""

        try:
            response = self.model.generate_content(extraction_prompt)
            extracted_text = response.text

            # Parse Gemini response
            fields = self._parse_gemini_response(extracted_text)
            return fields

        except Exception as e:
            print(f"[!] Gemini extraction failed: {str(e)}")
            print("[*] Falling back to rule-based extraction...")
            return self._extract_with_rules()

    def _parse_gemini_response(self, response_text: str) -> Dict:
        """Parse structured response from Gemini."""
        fields = {
            'parties_premises': {},
            'key_dates': {},
            'rent': {},
            'options': {},
            'insurance': {},
            'special': {}
        }

        lines = response_text.split('\n')
        current_section = {}

        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_').replace('(', '').replace(')', '')
                value = value.strip()

                if value.lower() != 'not found':
                    if any(k in key for k in ['tenant', 'landlord', 'address', 'property']):
                        fields['parties_premises'][key] = {'value': value, 'source': 'Gemini', 'found': True}
                    elif any(k in key for k in ['date', 'term', 'start', 'end']):
                        fields['key_dates'][key] = {'value': value, 'source': 'Gemini', 'found': True}
                    elif any(k in key for k in ['rent', 'monthly', 'annual']):
                        fields['rent'][key] = {'value': value, 'source': 'Gemini', 'found': True}
                    elif any(k in key for k in ['renewal', 'option', 'termination']):
                        fields['options'][key] = {'value': value, 'source': 'Gemini', 'found': True}
                    elif any(k in key for k in ['insurance']):
                        fields['insurance'][key] = {'value': value, 'source': 'Gemini', 'found': True}
                    else:
                        fields['special'][key] = {'value': value, 'source': 'Gemini', 'found': True}

        return fields

    def _extract_with_rules(self) -> Dict:
        """Fallback to rule-based extraction."""
        print("[*] Using rule-based extraction (keyword matching)...")

        section = {
            'parties_premises': {
                'tenant': self._find_field('tenant', ['tenant:', 'tenant name', 'lessee']),
                'landlord': self._find_field('landlord', ['landlord:', 'lessor:', 'owner:']),
                'address': self._find_field('address', ['address:', 'property address', 'location']),
                'leased_area': self._find_field('leased area', ['leaseable', 'sq.', 'sf', 'square feet']),
                'security_deposit': self._find_field('deposit', ['security deposit', 'deposit']),
            },
            'key_dates': {
                'lease_start': self._find_field('start date', ['commencement', 'start date', 'effective']),
                'lease_end': self._find_field('end date', ['expiration', 'end date', 'expires']),
                'lease_term': self._find_field('term', ['lease term', 'term of lease']),
                'rent_commencement': self._find_field('rent', ['rent commencement', 'rent begins']),
            },
            'rent': {
                'base_rent_monthly': self._find_field('monthly', ['monthly rent', 'per month', '$/month']),
                'base_rent_annual': self._find_field('annual', ['annual rent', 'per year', '$/year']),
                'percentage_rent': self._find_field('percentage', ['percentage rent', 'percentage']),
                'free_rent': self._find_field('free', ['free rent', 'free period']),
                'late_fees': self._find_field('late', ['late fee', 'late charge']),
            },
            'options': {
                'renewal': self._find_field('renewal', ['renewal option', 'option to renew']),
                'early_termination': self._find_field('termination', ['early termination', 'terminate']),
                'sales_kickout': self._find_field('sales', ['sales kickout', 'sales']),
            },
            'insurance': {
                'general_liability': self._find_field('liability', ['general liability', 'insurance']),
                'property': self._find_field('property', ['property insurance', 'property damage']),
                'workers_comp': self._find_field('workers', ['workers compensation', 'workers']),
            },
            'special': {
                'signage': self._find_field('signage', ['signage', 'sign rights']),
                'parking': self._find_field('parking', ['parking', 'parking rights']),
                'cam': self._find_field('cam', ['cam', 'common area', 'operating expenses']),
            }
        }

        return section

    def _find_field(self, field_name: str, keywords: list) -> Dict:
        """Find a field by keywords."""
        results = self.doc.find_section_with_source(keywords[0], context_lines=2)

        if results:
            value = results[0]['content'][:150]
            source = f"Page {results[0]['page']}"
            return {
                'value': value,
                'source': source,
                'found': True
            }
        else:
            return {
                'value': 'Not found in document',
                'source': None,
                'found': False
            }

    def get_summary(self) -> str:
        """Get a user-friendly summary of extracted fields."""
        if not self.extracted_fields:
            self.extracted_fields = self.extract_all_fields()

        summary = []
        summary.append("=" * 60)
        summary.append("LEASE SUMMARY")
        summary.append("=" * 60)

        for section_name, fields in self.extracted_fields.items():
            if isinstance(fields, dict) and any(v.get('found') for v in fields.values() if isinstance(v, dict)):
                summary.append(f"\n{section_name.upper().replace('_', ' ')}")
                summary.append("-" * 40)

                for field_name, field_data in fields.items():
                    if isinstance(field_data, dict) and field_data.get('found'):
                        pretty_name = field_name.replace('_', ' ').title()
                        value = field_data.get('value', 'N/A')[:100]
                        source = field_data.get('source', 'Unknown')
                        summary.append(f"• {pretty_name}: {value}")
                        summary.append(f"  └─ Source: {source}")

        summary.append("\n" + "=" * 60)
        return "\n".join(summary)

    def extraction_status(self) -> str:
        """Get extraction status."""
        if self.use_gemini:
            return "🤖 Using Gemini AI for extraction (Advanced)"
        else:
            return "📖 Using keyword matching (Basic)"
