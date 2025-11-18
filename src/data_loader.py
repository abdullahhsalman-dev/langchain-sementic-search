"""
Data Loader Module
==================

This module handles automatic processing of PDF files from the data/ directory.
It provides functionality for:
- Scanning the data directory for PDF files
- Processing new or modified PDFs automatically
- Tracking processed files to avoid duplicates
- Batch processing for efficiency

Replaces the upload endpoint with automatic file detection.
"""

import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
import hashlib
import json
from datetime import datetime
import time

from .document_processor import DocumentProcessor
from .semantic_search import SemanticSearchEngine

class DataFolderLoader:
    """
    Handles automatic PDF processing from the data/ directory
    
    This class:
    - Scans for PDF files in the data directory
    - Tracks which files have been processed
    - Processes new or modified files automatically
    - Provides batch processing capabilities
    """
    
    def __init__(self, 
                 data_dir: str = "data",
                 search_engine: SemanticSearchEngine = None,
                 document_processor: DocumentProcessor = None):
        """
        Initialize the data folder loader
        
        Args:
            data_dir: Path to directory containing PDF files
            search_engine: Initialized semantic search engine
            document_processor: Initialized document processor
        """
        self.data_dir = Path(data_dir)
        self.search_engine = search_engine
        self.document_processor = document_processor or DocumentProcessor()
        
        # File to track processed files and their hashes
        # here we are attaching the folder, processed_files.jsom, is directory ma attach ho gay.
        self.processed_files_cache = self.data_dir / ".processed_files.json"
        
        # Load existing processed files cache
        self.processed_files: Dict[str, Dict[str, Any]] = self._load_processed_files_cache()
        
        # Statistics
        self.processing_stats = {
            "total_files_found": 0,
            "files_processed": 0,
            "files_skipped": 0,
            "processing_errors": 0,
            "last_scan_time": None
        }
    
    def _load_processed_files_cache(self) -> Dict[str, Dict[str, Any]]:
        """
        Load the cache of previously processed files
        
        Returns:
            Dict mapping file paths to processing metadata
        """
        if not self.processed_files_cache.exists():
            return {}
        
        try:
            with open(self.processed_files_cache, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  Warning: Could not load processed files cache: {e}")
            return {}
    
    def _save_processed_files_cache(self):
        """Save the processed files cache to disk"""
        try:
            # Ensure data directory exists
            self.data_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.processed_files_cache, 'w') as f:
                json.dump(self.processed_files, f, indent=2, default=str)
        except IOError as e:
            print(f"⚠️  Warning: Could not save processed files cache: {e}")
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """
        Calculate SHA-256 hash of a file to detect changes
        
        Args:
            file_path: Path to the file
            
        Returns:
            str: Hexadecimal hash of the file content
        """
        hasher = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                # Read file in chunks to handle large files
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except IOError as e:
            print(f"❌ Error reading file {file_path}: {e}")
            return ""
    
    def scan_data_directory(self) -> List[Path]:
        """
        Scan the data directory for PDF files
        
        Returns:
            List of Path objects for all PDF files found
        """
        if not self.data_dir.exists():
            print(f"📁 Creating data directory: {self.data_dir}")
            self.data_dir.mkdir(parents=True, exist_ok=True)
            return []
        
        pdf_files = []
        
        # Recursively find all PDF files
        for pdf_file in self.data_dir.rglob("*.pdf"):
            if pdf_file.is_file():
                pdf_files.append(pdf_file)
        
        # Sort by modification time (newest first)
        pdf_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        self.processing_stats["total_files_found"] = len(pdf_files)
        self.processing_stats["last_scan_time"] = datetime.now().isoformat()
        
        print(f"📄 Found {len(pdf_files)} PDF files in {self.data_dir}")
        
        return pdf_files
    
    def identify_new_or_modified_files(self, pdf_files: List[Path]) -> List[Path]:
        """
        Identify files that are new or have been modified since last processing
        
        Args:
            pdf_files: List of all PDF files found
            
        Returns:
            List of files that need processing
        """
        files_to_process = []
        
        for pdf_file in pdf_files:
            file_path_str = str(pdf_file.relative_to(self.data_dir))
            
            # Calculate current file hash
            current_hash = self._calculate_file_hash(pdf_file)
            if not current_hash:
                continue
            
            # Check if file was previously processed
            if file_path_str in self.processed_files:
                stored_info = self.processed_files[file_path_str]
                stored_hash = stored_info.get("file_hash", "")
                
                if current_hash == stored_hash:
                    # File unchanged, skip processing
                    self.processing_stats["files_skipped"] += 1
                    continue
                else:
                    print(f"🔄 File modified: {file_path_str}")
            else:
                print(f"🆕 New file: {file_path_str}")
            
            files_to_process.append(pdf_file)
        
        return files_to_process
    
    def process_pdf_file(self, pdf_file: Path) -> Optional[Dict[str, Any]]:
        """
        Process a single PDF file
        
        Args:
            pdf_file: Path to the PDF file to process
            
        Returns:
            Dict with processing results or None if failed
        """
        file_path_str = str(pdf_file.relative_to(self.data_dir))
        
        try:
            print(f"🔄 Processing: {file_path_str}")
            start_time = time.time()
            
            # Read PDF file
            with open(pdf_file, 'rb') as f:
                pdf_content = f.read()
            
            # Process the PDF using document processor
            result = self.document_processor.process_pdf(
                file_content=pdf_content,
                filename=pdf_file.name
            )
            
            # Store document chunks using search engine
            if self.search_engine:
                chunks_stored = self.search_engine.store_document_chunks(
                    chunks=result["chunks"],
                    metadata=result["metadata"]
                )
                result["chunks_stored"] = chunks_stored
            
            processing_time = time.time() - start_time
            
            # Update processed files cache
            file_hash = self._calculate_file_hash(pdf_file)
            self.processed_files[file_path_str] = {
                "file_hash": file_hash,
                "processed_at": datetime.now().isoformat(),
                "document_id": result["document_id"],
                "chunks_created": result["total_chunks"],
                "chunks_stored": result.get("chunks_stored", 0),
                "processing_time": processing_time,
                "file_size": pdf_file.stat().st_size
            }
            
            print(f"✅ Processed {file_path_str}: {result['total_chunks']} chunks in {processing_time:.2f}s")
            self.processing_stats["files_processed"] += 1
            
            return result
            
        except Exception as e:
            print(f"❌ Error processing {file_path_str}: {str(e)}")
            self.processing_stats["processing_errors"] += 1
            
            # Still update cache to avoid repeated failures
            self.processed_files[file_path_str] = {
                "error": str(e),
                "error_time": datetime.now().isoformat(),
                "file_hash": self._calculate_file_hash(pdf_file)
            }
            
            return None
    
    def process_all_files(self, force_reprocess: bool = False) -> Dict[str, Any]:
        """
        Process all PDF files in the data directory
        
        Args:
            force_reprocess: If True, reprocess all files regardless of cache
            
        Returns:
            Dict with processing summary and statistics
        """
        print(f"🚀 Starting data directory processing...")
        start_time = time.time()
        
        # Reset statistics
        self.processing_stats = {
            "total_files_found": 0,
            "files_processed": 0,
            "files_skipped": 0,
            "processing_errors": 0,
            "last_scan_time": None
        }
        
        # Scan for PDF files
        pdf_files = self.scan_data_directory()
        
        if not pdf_files:
            print("📭 No PDF files found in data directory")
            return {
                "summary": "No PDF files found",
                "statistics": self.processing_stats
            }
        
        # Identify files to process
        if force_reprocess:
            files_to_process = pdf_files
            print(f"🔄 Force reprocessing all {len(pdf_files)} files")
        else:
            files_to_process = self.identify_new_or_modified_files(pdf_files)
        
        if not files_to_process:
            print("✅ All files are up to date")
            return {
                "summary": "All files already processed",
                "statistics": self.processing_stats
            }
        
        print(f"📋 Processing {len(files_to_process)} files...")
        
        # Process files one by one (could be made parallel if needed)
        processed_results = []
        for pdf_file in files_to_process:
            result = self.process_pdf_file(pdf_file)
            if result:
                processed_results.append(result)
        
        # Save the updated cache
        self._save_processed_files_cache()
        
        total_time = time.time() - start_time
        
        # Generate summary
        summary = {
            "total_processing_time": round(total_time, 2),
            "files_found": len(pdf_files),
            "files_processed": self.processing_stats["files_processed"],
            "files_skipped": self.processing_stats["files_skipped"],
            "processing_errors": self.processing_stats["processing_errors"],
            "processed_documents": [r["document_id"] for r in processed_results],
            "statistics": self.processing_stats
        }
        
        print(f"🎉 Processing complete! {self.processing_stats['files_processed']} files processed in {total_time:.2f}s")
        
        return summary
    
    def process_specific_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Process a specific file by name
        
        Args:
            filename: Name of the file to process (relative to data directory)
            
        Returns:
            Processing result or None if file not found
        """
        file_path = self.data_dir / filename
        
        if not file_path.exists():
            print(f"❌ File not found: {filename}")
            return None
        
        if not file_path.suffix.lower() == '.pdf':
            print(f"❌ Not a PDF file: {filename}")
            return None
        
        return self.process_pdf_file(file_path)
    
    def get_processed_files_info(self) -> Dict[str, Any]:
        """
        Get information about all processed files
        
        Returns:
            Dict with processed files information and statistics
        """
        return {
            "processed_files": self.processed_files,
            "statistics": self.processing_stats,
            "data_directory": str(self.data_dir),
            "cache_file": str(self.processed_files_cache)
        }
    
    def clear_cache(self):
        """Clear the processed files cache"""
        self.processed_files.clear()
        if self.processed_files_cache.exists():
            self.processed_files_cache.unlink()
        print("🧹 Processed files cache cleared")