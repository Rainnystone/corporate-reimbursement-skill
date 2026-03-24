from docling.document_converter import DocumentConverter
from .utils import setup_logger

logger = setup_logger(__name__)

# Initialize the converter globally to avoid reloading models for every file
converter = DocumentConverter()

def extract_pdf_text(file_path: str) -> str:
    """
    Extracts text from a PDF file using docling and returns it as a Markdown string.
    """
    logger.info(f"Extracting text from {file_path} using docling...")
    try:
        result = converter.convert(file_path)
        return result.document.export_to_markdown()
    except Exception as e:
        logger.error(f"Failed to extract text from {file_path}: {e}")
        return ""
