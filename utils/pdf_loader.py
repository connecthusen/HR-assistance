# utils/pdf_loader.py

from pypdf import PdfReader
import logging

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        logger.info(f"✓ Extracted {len(text)} chars from {pdf_path}")
        return text.strip()
    except Exception as e:
        logger.error(f"✗ Failed to read PDF {pdf_path}: {e}")
        return ""
