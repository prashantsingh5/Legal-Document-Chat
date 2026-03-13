"""
Lease Field Extraction Module
Uses LLM to extract structured lease fields with source tracking.
"""

from typing import Dict, List, Optional, Tuple
import json
import re
from document_extractor import DocumentExtractor


class LeaseExtractor:
    """
    Extracts lease fields from documents using prompts and rules.
    Tracks the source of each extracted field.
    """

    def __init__(self, document_extractor: DocumentExtractor, use_llm: bool = False):
        """
        Initialize the lease extractor.

        Args:
            document_extractor: Instance of DocumentExtractor
            use_llm: Whether to use LLM (for future enhancement)
        """
        self.doc = document_extractor
        self.use_llm = use_llm
        self.extracted_fields = {}
        self.field_sources = {}  # Track where each field came from

    def extract_all_fields(self) -> Dict:
        """Extract all lease fields using rule-based extraction."""
        results = {}

        # PARTIES & PREMISES
        results['parties_premises'] = self._extract_parties_premises()

        # KEY DATES
        results['key_dates'] = self._extract_key_dates()

        # RENT
        results['rent'] = self._extract_rent()

        # RENEWAL OPTIONS
        results['renewal_options'] = self._extract_renewal_options()

        # TERMINATION
        results['termination'] = self._extract_termination()

        # SECURITY DEPOSIT
        results['security_deposit'] = self._extract_security_deposit()

        # CAM / OPERATING EXPENSES
        results['cam'] = self._extract_cam()

        # TAXES
        results['taxes'] = self._extract_taxes()

        # INSURANCE
        results['insurance'] = self._extract_insurance()

        # SIGNAGE
        results['signage'] = self._extract_signage()

        # SUBLEASE & ASSIGNMENT
        results['sublease_assignment'] = self._extract_sublease_assignment()

        # DEFAULT & REMEDIES
        results['default'] = self._extract_default()

        # SPECIAL PROVISIONS
        results['special_provisions'] = self._extract_special_provisions()

        self.extracted_fields = results
        return results

    def _search_and_track(self, keywords: List[str], context_lines: int = 5) -> Tuple[List[Dict], List[Dict]]:
        """
        Search for keywords and track sources.

        Returns:
            Tuple of (results, sources) where each result has the found text and page info
        """
        all_results = []
        for keyword in keywords:
            results = self.doc.find_section_with_source(keyword, context_lines)
            all_results.extend(results)
        return all_results

    def _extract_parties_premises(self) -> Dict:
        """Extract tenant, landlord, address, etc."""
        section = {
            'tenant': self._extract_field('tenant', ['tenant:', 'tenant name']),
            'landlord': self._extract_field('landlord', ['landlord:', 'lessor:', 'owner:']),
            'property_address': self._extract_field('address', ['spring hill', 'address:', 'location:']),
            'leased_area_sf': self._extract_field('leased area', ['leaseable', 'sq.', 'sf', 'square feet']),
            'security_deposit': self._extract_field('security deposit', ['security deposit', 'deposit']),
            'guarantor': self._extract_field('guarantor', ['guarantor', 'guarantee', 'guaranty']),
            'dba_name': self._extract_field('dba', ['dba', 'doing business', 'd/b/a']),
        }
        return section

    def _extract_key_dates(self) -> Dict:
        """Extract lease term, start dates, end dates, etc."""
        doc_text = self.doc.get_full_text()

        # Extract dates using regex patterns
        date_pattern = r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}\b'
        dates = re.findall(date_pattern, doc_text)

        section = {
            'lease_start_date': self._extract_field('lease start', ['commencement', 'start date', 'effective date', 'lease date']),
            'lease_end_date': self._extract_field('lease end', ['expiration', 'end date', 'lease term']),
            'lease_term_months': self._extract_field('lease term', ['lease term', 'term of lease', 'months']),
            'tenant_possession_date': self._extract_field('possession', ['tenant possession', 'possession date']),
            'rent_commencement_date': self._extract_field('rent commencement', ['rent commencement', 'rent begins']),
            'dates_found': dates[:5] if dates else []  # First 5 dates found
        }
        return section

    def _extract_rent(self) -> Dict:
        """Extract rent amounts and terms."""
        section = {
            'base_rent_annual': self._extract_field('base rent', ['base rent', 'minimum rent', 'annual rent']),
            'base_rent_monthly': self._extract_field('monthly rent', ['monthly rent', 'per month']),
            'base_rent_psf': self._extract_field('rent per sf', ['per square foot', '$/sf', 'psf']),
            'percentage_rent': self._extract_field('percentage rent', ['percentage rent', 'percentage']),
            'free_rent': self._extract_field('free rent', ['free rent', 'free period']),
            'tenant_allowance': self._extract_field('tenant allowance', ['tenant allowance', 'tenant improvement', 'allowance']),
            'late_fees': self._extract_field('late fees', ['late fee', 'late charge', 'interest']),
        }
        return section

    def _extract_renewal_options(self) -> Dict:
        """Extract renewal option details."""
        section = {
            'number_of_options': self._extract_field('renewal options', ['renewal option', 'option to renew', 'renew']),
            'option_term': self._extract_field('option term', ['option term', 'renewal term']),
            'option_rent': self._extract_field('option rent', ['option rent', 'renewal rent']),
            'notice_requirements': self._extract_field('notice', ['prior written notice', 'notice']),
        }
        return section

    def _extract_termination(self) -> Dict:
        """Extract termination clauses and early termination rights."""
        section = {
            'early_termination': self._extract_field('early termination', ['early termination', 'terminate', 'termination']),
            'termination_clause': self._extract_field('termination clause', ['termination clause', 'default clause']),
            'sales_kickout': self._extract_field('sales kickout', ['sales', 'sales kickout']),
            'cotenancy': self._extract_field('co-tenancy', ['co-tenancy', 'cotenancy']),
        }
        return section

    def _extract_security_deposit(self) -> Dict:
        """Extract security deposit information."""
        section = {
            'deposit_amount': self._extract_field('deposit amount', ['security deposit', 'deposit $', 'deposit amount']),
            'deposit_terms': self._extract_field('deposit terms', ['security deposit', 'deposit shall']),
        }
        return section

    def _extract_cam(self) -> Dict:
        """Extract CAM/Operating Expense information."""
        section = {
            'cam_charges': self._extract_field('cam', ['cam', 'operating expenses', 'common area']),
            'pro_rata_share': self._extract_field('pro rata', ['pro rata', 'percentage share']),
            'expense_stop': self._extract_field('expense stop', ['expense stop', 'base year']),
            'exclusions': self._extract_field('cam exclusions', ['cam exclusions', 'exclude', 'excluded']),
        }
        return section

    def _extract_taxes(self) -> Dict:
        """Extract tax information."""
        section = {
            'property_taxes': self._extract_field('property taxes', ['property tax', 'taxes', 'tax']),
            'pro_rata_tax_share': self._extract_field('tax share', ['pro rata', 'share', 'percentage']),
            'base_year': self._extract_field('base year', ['base year', 'base']),
        }
        return section

    def _extract_insurance(self) -> Dict:
        """Extract insurance requirements."""
        section = {
            'general_liability': self._extract_field('general liability', ['general liability', 'insurance', '$']),
            'property_insurance': self._extract_field('property', ['property insurance', 'property damage']),
            'workers_comp': self._extract_field('workers comp', ['workers', 'workers compensation']),
        }
        return section

    def _extract_signage(self) -> Dict:
        """Extract signage rights."""
        section = {
            'signage_rights': self._extract_field('signage', ['signage', 'sign', 'signage rights']),
            'permitted_use': self._extract_field('permitted use', ['permitted use', 'use of premises']),
            'exclusive_use': self._extract_field('exclusive use', ['exclusive use', 'exclusive']),
        }
        return section

    def _extract_sublease_assignment(self) -> Dict:
        """Extract sublease and assignment terms."""
        section = {
            'sublease_terms': self._extract_field('sublease', ['sublease', 'sublet', 'assignment']),
            'landlord_consent': self._extract_field('landlord consent', ['landlord consent', 'consent']),
            'recapture': self._extract_field('recapture', ['recapture', 'landlord recapture']),
        }
        return section

    def _extract_default(self) -> Dict:
        """Extract default and remedy terms."""
        section = {
            'default_clause': self._extract_field('default', ['default', 'event of default']),
            'notice_and_cure': self._extract_field('notice and cure', ['notice', 'cure', 'remedy']),
        }
        return section

    def _extract_special_provisions(self) -> Dict:
        """Extract special or unusual provisions."""
        doc_text = self.doc.get_full_text()

        # Look for common special provisions
        provisions = []
        keywords = [
            'hvac', 'parking', 'utilities', 'maintenance', 'repairs',
            'expansion', 'renewal', 'purchase option', 'environmental',
            'broker', 'commission', 'compliance', 'sustainability'
        ]

        for keyword in keywords:
            if keyword.lower() in doc_text.lower():
                results = self.doc.find_section_with_source(keyword)
                if results:
                    provisions.append({
                        'provision': keyword,
                        'source': results[0] if results else {}
                    })

        return {'special_provisions': provisions}

    def _extract_field(self, field_name: str, keywords: List[str]) -> Dict:
        """
        Extract a specific field and track its source.

        Returns:
            Dict with 'value' and 'source' keys
        """
        results = self._search_and_track(keywords, context_lines=3)

        if results:
            # Take the first result
            first_result = results[0]
            value = first_result['content'][:200]  # First 200 chars
            source = f"Page {first_result['page']}"

            return {
                'value': value,
                'source': source,
                'found': True
            }
        else:
            return {
                'value': 'Not found',
                'source': None,
                'found': False
            }

    def get_structured_output(self) -> Dict:
        """Get the extracted fields in the required template format."""
        if not self.extracted_fields:
            self.extract_all_fields()

        return {
            'document_name': 'Nelly\'s Italian Cafe Lease',
            'extraction_version': '1.0',
            'fields': self.extracted_fields
        }

    def get_field_with_source(self, field_name: str) -> Tuple[str, Optional[str]]:
        """
        Get a specific field's value and source.

        Returns:
            Tuple of (value, source_page)
        """
        flat_fields = self._flatten_fields(self.extracted_fields)
        if field_name in flat_fields:
            field_data = flat_fields[field_name]
            return (field_data.get('value', 'Not found'), field_data.get('source'))
        return ('Field not found', None)

    @staticmethod
    def _flatten_fields(fields: Dict, prefix: str = '') -> Dict:
        """Flatten nested fields dict."""
        flat = {}
        for key, value in fields.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                if 'value' in value and 'source' in value:
                    flat[full_key] = value
                else:
                    flat.update(LeaseExtractor._flatten_fields(value, full_key))
            else:
                flat[full_key] = {'value': value, 'source': None}
        return flat
