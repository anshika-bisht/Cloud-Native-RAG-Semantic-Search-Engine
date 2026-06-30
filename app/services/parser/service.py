import fitz  # PyMuPDF
import pdfplumber
import logging
from abc import ABC, abstractmethod
from typing import List

logger = logging.getLogger("rag_engine.parser")

class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> str:
        pass

class DocumentParser(BaseParser):
    """
    Hybrid PDF Parser.
    Attempts extraction using PyMuPDF first (fast), falls back to pdfplumber for complex layouts.
    """
    def parse(self, file_path: str) -> str:
        try:
            return self._parse_pymupdf(file_path)
        except Exception as e:
            logger.warning(f"PyMuPDF failed parsing {file_path}, falling back to pdfplumber. Error: {e}")
            return self._parse_pdfplumber(file_path)

    def _parse_pymupdf(self, file_path: str) -> str:
        doc = fitz.open(file_path)
        extracted_text = []
        for page in doc:
            text = page.get_text("text")
            if text.strip():
                extracted_text.append(self._clean_text(text))
        return "\n".join(extracted_text)

    def _parse_pdfplumber(self, file_path: str) -> str:
        extracted_text = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text and text.strip():
                    extracted_text.append(self._clean_text(text))
        return "\n".join(extracted_text)

    def _clean_text(self, text: str) -> str:
        import re
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
