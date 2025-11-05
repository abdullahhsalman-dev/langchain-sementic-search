"""
Document Processing Module
=========================

This module handles PDF document processing for the semantic search engine.
It includes functionality for:
- PDF text extraction
- Text chunking and preprocessing
- Metadata extraction
- Document cleaning and normalization

Uses PyMuPDF (fitz) for robust PDF processing and LangChain for text splitting.
"""

import fitz  # PyMuPDF for PDF processing
import uuid
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dataclasses import dataclass

@dataclass
class DocumentChunk:
    """
    Represents a chunk of text from a document
    
    Attributes:
        chunk_id: Unique identifier for the chunk
        content: The actual text content
        metadata: Additional information about the chunk
        chunk_index: Position of chunk in the original document
    """
    chunk_id: str
    content: str
    metadata: Dict[str, Any]
    chunk_index: int

class DocumentProcessor:
    """
    Handles PDF document processing and text chunking
    
    This class provides methods to:
    - Extract text from PDF documents
    - Split documents into manageable chunks
    - Clean and preprocess text
    - Generate metadata for documents and chunks
    """
    
    def __init__(self, 
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200,
                 min_chunk_size: int = 100):
        """
        Initialize the document processor
        
        Args:
            chunk_size: Maximum size of each text chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
            min_chunk_size: Minimum size for a chunk to be considered valid
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        
        # Initialize the text splitter for chunking documents
        # RecursiveCharacterTextSplitter tries to split on natural boundaries
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]  # Try these separators in order
        )
    
    async def process_pdf(self, 
                         file_content: bytes, 
                         filename: str) -> Dict[str, Any]:
        """
        Process a PDF file and extract chunks for semantic search
        
        This method:
        1. Extracts text from all pages of the PDF
        2. Cleans and preprocesses the text
        3. Splits the text into chunks
        4. Generates metadata for the document and chunks
        
        Args:
            file_content: Raw PDF file content as bytes
            filename: Original filename of the PDF
            
        Returns:
            Dict containing:
                - document_id: Unique identifier for the document
                - chunks: List of DocumentChunk objects
                - metadata: Document-level metadata
                -
        Raises:
            Exception: If PDF processing fails
        """
        try:
            # Generate unique document ID based on content hash
            document_id = self._generate_document_id(file_content, filename)
            
            # Extract text from PDF
            extracted_text = self._extract_pdf_text(file_content)
            
            # Clean and preprocess the text
            cleaned_text = self._clean_text(extracted_text)
            
            # Generate document metadata
            doc_metadata = self._generate_document_metadata(
                filename=filename,
                content=cleaned_text,
                file_size=len(file_content)
            )
            
            # Split text into chunks
            text_chunks = self.text_splitter.split_text(cleaned_text)
            
            # Create DocumentChunk objects with metadata
            chunks = []
            for i, chunk_text in enumerate(text_chunks):
                # Skip chunks that are too small
                if len(chunk_text.strip()) < self.min_chunk_size:
                    continue
                
                chunk = DocumentChunk(
                    chunk_id=f"{document_id}_chunk_{i}",
                    content=chunk_text.strip(),
                    metadata=self._generate_chunk_metadata(
                        document_id=document_id,
                        chunk_index=i,
                        doc_metadata=doc_metadata
                    ),
                    chunk_index=i
                )
                chunks.append(chunk)
            
            return {
                "document_id": document_id,
                "chunks": chunks,
                "metadata": doc_metadata,
                "total_chunks": len(chunks),
                "original_text_length": len(extracted_text),
                "cleaned_text_length": len(cleaned_text)
            }
            
        except Exception as e:
            raise Exception(f"Failed to process PDF: {str(e)}")
    
    def _extract_pdf_text(self, file_content: bytes) -> str:
        """
        Extract text content from PDF using PyMuPDF
        
        This method:
        - Opens the PDF from bytes
        - Extracts text from each page
        - Handles various PDF formats and encodings
        - Preserves basic structure with page breaks
        
        Args:
            file_content: Raw PDF file content
            
        Returns:
            str: Extracted text from all pages
            
        Raises:
            Exception: If PDF cannot be opened or processed
        """
        try:
            # Open PDF document from bytes
            pdf_document = fitz.open(stream=file_content, filetype="pdf")
            
            extracted_text = ""
            
            # Process each page
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                
                # Extract text from the page
                page_text = page.get_text()
                
                # Add page separator for better chunking
                extracted_text += f"\n--- Page {page_num + 1} ---\n"
                extracted_text += page_text
                extracted_text += "\n"
            
            # Close the PDF document
            pdf_document.close()
            
            return extracted_text
            
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text
        
        This method:
        - Removes excessive whitespace
        - Normalizes line breaks
        - Removes special characters that might interfere with processing
        - Preserves meaningful punctuation and structure
        
        Args:
            text: Raw extracted text
            
        Returns:
            str: Cleaned and normalized text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Normalize line breaks (preserve paragraph structure)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove page headers/footers patterns (common in PDFs)
        text = re.sub(r'--- Page \d+ ---', '', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[.]{3,}', '...', text)
        
        # Remove control characters but preserve basic punctuation
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]', '', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def _generate_document_id(self, file_content: bytes, filename: str) -> str:
        """
        Generate a unique document ID based on content and filename
        
        Uses SHA-256 hash of file content to ensure uniqueness
        and prevent duplicate processing of the same document.
        
        Args:
            file_content: Raw file content
            filename: Original filename
            
        Returns:
            str: Unique document identifier
        """
        # Create hash from file content
        content_hash = hashlib.sha256(file_content).hexdigest()[:16]
        
        # Clean filename for use in ID
        clean_filename = re.sub(r'[^a-zA-Z0-9_-]', '_', filename.split('.')[0])
        
        # Combine timestamp, filename, and content hash
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"doc_{clean_filename}_{timestamp}_{content_hash}"
    
    def _generate_document_metadata(self, 
                                  filename: str, 
                                  content: str, 
                                  file_size: int) -> Dict[str, Any]:
        """
        Generate comprehensive metadata for a document
        
        Args:
            filename: Original filename
            content: Processed text content
            file_size: Size of original file in bytes
            
        Returns:
            Dict: Document metadata including statistics and processing info
        """
        return {
            "filename": filename,
            "file_size_bytes": file_size,
            "content_length": len(content),
            "word_count": len(content.split()),
            "processed_at": datetime.now().isoformat(),
            "file_type": "pdf",
            "processing_version": "1.0",
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap
        }
    
    def _generate_chunk_metadata(self, 
                               document_id: str, 
                               chunk_index: int, 
                               doc_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate metadata for individual chunks
        
        Args:
            document_id: Parent document identifier
            chunk_index: Position of chunk in document
            doc_metadata: Document-level metadata
            
        Returns:
            Dict: Chunk-specific metadata
        """
        return {
            "document_id": document_id,
            "chunk_index": chunk_index,
            "filename": doc_metadata["filename"],
            "file_type": doc_metadata["file_type"],
            "processed_at": doc_metadata["processed_at"],
            "chunk_size_config": doc_metadata["chunk_size"],
            "chunk_overlap_config": doc_metadata["chunk_overlap"]
        }
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Get current processing configuration and statistics
        
        Returns:
            Dict: Processing configuration details
        """
        return {
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "min_chunk_size": self.min_chunk_size,
            "splitter_type": "RecursiveCharacterTextSplitter",
            "separators": ["\n\n", "\n", " ", ""]
        }