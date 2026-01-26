"""PDF service for extracting text from PDF files."""

from typing import Dict, Optional
from io import BytesIO
import PyPDF2
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.utils.exceptions import BadRequestException
from app.utils.logger import logger


class PDFService:
    """Service for handling PDF file text extraction."""
    
    def __init__(self):
        """Initialize PDF service."""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
    
    def extract_text_from_bytes(self, pdf_bytes: bytes, filename: str = "document.pdf") -> Dict[str, any]:
        """
        Extract text from PDF file bytes using PyPDF2.
        
        Args:
            pdf_bytes: PDF file content as bytes
            filename: Original filename for reference
        
        Returns:
            Dict containing extracted text and metadata
        
        Raises:
            BadRequestException: If PDF extraction fails
        """
        try:
            logger.info(f"Extracting text from PDF: {filename}")
            
            # Create a BytesIO object from bytes
            pdf_file = BytesIO(pdf_bytes)
            
            # Create PDF reader
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Get number of pages
            num_pages = len(pdf_reader.pages)
            
            logger.info(f"PDF has {num_pages} pages")
            
            # Extract text from all pages
            full_text = ""
            pages_content = {}
            
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                
                if page_text:
                    full_text += page_text + "\n\n"
                    pages_content[f"Page {page_num + 1}"] = page_text.strip()
            
            # Clean up the text
            full_text = self._clean_text(full_text)
            
            if not full_text.strip():
                raise BadRequestException("No text could be extracted from the PDF")
            
            result = {
                "filename": filename,
                "num_pages": num_pages,
                "full_content": full_text,
                "pages": pages_content,
                "character_count": len(full_text)
            }
            
            logger.info(f"Successfully extracted {len(full_text)} characters from PDF")
            
            return result
            
        except PyPDF2.errors.PdfReadError as e:
            logger.error(f"Invalid PDF file: {str(e)}")
            raise BadRequestException(f"Invalid or corrupted PDF file: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise BadRequestException(f"Failed to extract text from PDF: {str(e)}")
    
    def extract_text_from_file_path(self, file_path: str) -> Dict[str, any]:
        """
        Extract text from PDF file path using LangChain.
        
        Args:
            file_path: Path to PDF file
        
        Returns:
            Dict containing extracted text and metadata
        
        Raises:
            BadRequestException: If PDF extraction fails
        """
        try:
            logger.info(f"Loading PDF from path: {file_path}")
            
            # Use LangChain's PyPDFLoader
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            
            # Extract text from all pages
            full_text = ""
            pages_content = {}
            
            for i, page in enumerate(pages):
                page_text = page.page_content
                full_text += page_text + "\n\n"
                pages_content[f"Page {i + 1}"] = page_text.strip()
            
            # Clean up the text
            full_text = self._clean_text(full_text)
            
            if not full_text.strip():
                raise BadRequestException("No text could be extracted from the PDF")
            
            result = {
                "filename": file_path.split("/")[-1],
                "num_pages": len(pages),
                "full_content": full_text,
                "pages": pages_content,
                "character_count": len(full_text)
            }
            
            logger.info(f"Successfully extracted {len(full_text)} characters from PDF")
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF file: {str(e)}")
            raise BadRequestException(f"Failed to extract text from PDF: {str(e)}")
    
    def split_text_into_chunks(self, text: str) -> list:
        """
        Split text into manageable chunks for processing.
        
        Args:
            text: Full text to split
        
        Returns:
            List of text chunks
        """
        try:
            chunks = self.text_splitter.split_text(text)
            logger.info(f"Split text into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error splitting text: {str(e)}")
            return [text]  # Return full text as single chunk if splitting fails
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing excessive whitespace and special characters.
        
        Args:
            text: Raw extracted text
        
        Returns:
            Cleaned text
        """
        # Remove excessive newlines
        text = "\n".join([line.strip() for line in text.split("\n") if line.strip()])
        
        # Replace multiple spaces with single space
        import re
        text = re.sub(r' +', ' ', text)
        
        # Remove weird characters (optional, be careful with non-English text)
        # text = re.sub(r'[^\w\s\.,;:!?()\-\'\"]', '', text)
        
        return text.strip()
    
    def extract_metadata(self, pdf_bytes: bytes) -> Dict[str, any]:
        """
        Extract metadata from PDF.
        
        Args:
            pdf_bytes: PDF file content as bytes
        
        Returns:
            Dict containing PDF metadata
        """
        try:
            pdf_file = BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            metadata = pdf_reader.metadata
            
            if metadata:
                return {
                    "title": metadata.get("/Title", "Unknown"),
                    "author": metadata.get("/Author", "Unknown"),
                    "subject": metadata.get("/Subject", "Unknown"),
                    "creator": metadata.get("/Creator", "Unknown"),
                    "producer": metadata.get("/Producer", "Unknown"),
                    "creation_date": metadata.get("/CreationDate", "Unknown"),
                }
            
            return {}
            
        except Exception as e:
            logger.warning(f"Could not extract PDF metadata: {str(e)}")
            return {}


# Singleton instance
pdf_service = PDFService()
