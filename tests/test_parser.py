import os
import pytest
from unittest.mock import patch, mock_open
from app.services.parser.service import DocumentParser

def test_parser_fallback_mechanism(parser: DocumentParser):
    with patch("fitz.open") as mock_fitz:
        # Force PyMuPDF to fail
        mock_fitz.side_effect = Exception("PyMuPDF failure")
        
        with patch("pdfplumber.open") as mock_plumber:
            mock_pdf = mock_plumber.return_value.__enter__.return_value
            mock_page = mock_pdf.pages[0] if mock_pdf.pages else None
            # Mock pdfplumber success
            
            try:
                parser.parse("dummy.pdf")
            except Exception:
                pass
            
            # Assert pdfplumber was called as fallback
            mock_plumber.assert_called_once_with("dummy.pdf")
