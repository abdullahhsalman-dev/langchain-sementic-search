"""
FastAPI Semantic Search Engine with LangChain
============================================

This module provides a REST API for semantic search over PDF documents using:
- FastAPI for the web framework
- LangChain for document processing and RAG
- PostgreSQL with pgvector for vector storage
- Sentence Transformers for free embeddings

Main Features:
- Upload and process PDF documents
- Semantic search through document content
- RAG-based question answering
- Vector similarity search
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

# Import our custom modules
# What's happening: Importing all the core business logic modules from the src/ directory.
from src.document_processor import DocumentProcessor
from src.semantic_search import SemanticSearchEngine
from src.rag_engine import RAGEngine
from src.data_loader import DataFolderLoader
from src.ollama_client import OllamaClient

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI application with metadata
# What's happening: Creating the FastAPI application instance with metadata.
app = FastAPI(
    title="LangChain Semantic Search Engine",
    description="A semantic search engine for PDF documents using LangChain, PostgreSQL, and free embeddings",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI documentation endpoint
    redoc_url="/redoc"  # ReDoc documentation endpoint
)

# Pydantic models for request/response validation
class SearchQuery(BaseModel):
    """Model for semantic search requests"""
    query: str
    top_k: Optional[int] = 5  # Number of results to return
    similarity_threshold: Optional[float] = 0.7  # Minimum similarity score

class RAGQuery(BaseModel):
    """Model for RAG (Retrieval Augmented Generation) requests"""
    question: str
    top_k: Optional[int] = 3  # Number of context documents to retrieve
    max_tokens: Optional[int] = 512  # Maximum tokens in generated response

class SearchResult(BaseModel):
    """Model for search result responses"""
    content: str
    similarity_score: float
    metadata: dict
    chunk_id: str

class RAGResponse(BaseModel):
    """Model for RAG response"""
    answer: str
    source_documents: List[SearchResult]
    confidence_score: float

# Global instances - initialized on startup
# What's happening: Declaring global variables for core components (initialized later).
document_processor: DocumentProcessor = None
search_engine: SemanticSearchEngine = None
rag_engine: RAGEngine = None
data_loader: DataFolderLoader = None
ollama_client: OllamaClient = None

#  What's happening:
#   - When FastAPI starts, this runs once
#   - Initializes all core components with proper dependencies
#   - Automatically processes any PDFs in data/ folder
#   - Sets up the entire system before handling requests


#    # Startup initialization (not HTTP route)
@app.on_event("startup")
async def startup_event():
    """
    Initialize application components on startup
    
    This function runs when the FastAPI application starts up and initializes:
    - Document processor for PDF handling
    - Semantic search engine with embeddings
    - Ollama client for local LLM inference
    - RAG engine for question answering
    - Data loader for automatic PDF processing
    """
    global document_processor, search_engine, rag_engine, data_loader, ollama_client
    
    try:
        # Initialize document processor
        document_processor = DocumentProcessor()
        
        # Initialize semantic search engine with database connection
        search_engine = SemanticSearchEngine()
        search_engine.initialize()
        
        # Initialize Ollama client
        ollama_client = OllamaClient()
        ollama_client.health_check()
        
        # Initialize RAG engine with Ollama client
        rag_engine = RAGEngine(search_engine, ollama_client)
        rag_engine.initialize()
        
        # Initialize data loader for automatic PDF processing
        data_loader = DataFolderLoader(
            data_dir="data",
            search_engine=search_engine,
            document_processor=document_processor
        )
        
        # Automatically process any PDFs in the data folder
        print("🔄 Processing PDFs from data/ directory...")
        processing_result = data_loader.process_all_files()
        
        # Extract statistics from result
        stats = processing_result.get("statistics", {})
        files_processed = stats.get("files_processed", 0)
        
        if files_processed > 0:
            print(f"✅ Processed {files_processed} PDF files from data/ directory")
        else:
            print("📭 No new PDF files to process")
        
        print("✅ Application startup completed successfully")
        
    except Exception as e:
        print(f"❌ Error during startup: {str(e)}")
        raise e

@app.get("/")
async def root():
    """
    Root endpoint providing API information
    
    Returns:
        dict: Basic API information and available endpoints
    """
    return {
        "message": "LangChain Semantic Search Engine API",
        "version": "1.0.0",
        "note": "Place PDF files in the 'data/' directory for automatic processing",
        "endpoints": {
            "search": "/search",
            "rag": "/rag",
            "documents": "/documents",
            "process_data_folder": "/process-data-folder",
            "data_folder_info": "/data-folder-info",
            "health": "/health"
        },
        "documentation": "/docs"
    }

@app.post("/process-data-folder")
async def process_data_folder(force_reprocess: bool = False):
    """
    Process all PDF files in the data/ directory
    
    This endpoint:
    1. Scans the data/ directory for PDF files
    2. Processes new or modified files (unless force_reprocess=True)
    3. Generates embeddings and stores in database
    4. Returns processing summary
    
    Args:
        force_reprocess: If True, reprocess all files regardless of cache
        
    Returns:
        dict: Processing summary and statistics
        
    Raises:
        HTTPException: If processing fails
    """
    try:
        processing_result = data_loader.process_all_files(force_reprocess=force_reprocess)
        
        return {
            "message": "Data folder processing completed",
            "processing_summary": processing_result,
            "force_reprocess": force_reprocess
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing data folder: {str(e)}"
        )

@app.get("/data-folder-info")
async def get_data_folder_info():
    """
    Get information about the data folder and processed files
    
    Returns:
        dict: Information about processed files and statistics
    """
    try:
        info = data_loader.get_processed_files_info()
        
        return {
            "message": "Data folder information",
            "data_directory": info["data_directory"],
            "total_processed_files": len(info["processed_files"]),
            "processed_files": info["processed_files"],
            "statistics": info["statistics"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting data folder info: {str(e)}"
        )

@app.post("/search", response_model=List[SearchResult])
async def semantic_search(query: SearchQuery):
    """
    Perform semantic search across uploaded documents
    
    This endpoint:
    1. Converts the query text to embeddings
    2. Performs vector similarity search in PostgreSQL
    3. Returns ranked results based on similarity scores
    
    Args:
        query (SearchQuery): Search parameters including query text and filters
        
    Returns:
        List[SearchResult]: List of matching document chunks with similarity scores
        
    Raises:
        HTTPException: If search fails or no results found
    """
    try:
        # Perform semantic search
        results = search_engine.search(
            query=query.query,
            top_k=query.top_k,
            similarity_threshold=query.similarity_threshold
        )
        
        if not results:
            return []
        
        # Format results for response
        formatted_results = []
        for result in results:
            formatted_results.append(SearchResult(
                content=result["content"],
                similarity_score=result["similarity_score"],
                metadata=result["metadata"],
                chunk_id=result["chunk_id"]
            ))
        
        return formatted_results
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error performing search: {str(e)}"
        )

@app.post("/rag", response_model=RAGResponse)
async def rag_query(query: RAGQuery):
    """
    Answer questions using RAG (Retrieval Augmented Generation)
    
    This endpoint:
    1. Retrieves relevant document chunks based on the question
    2. Uses retrieved context to generate a comprehensive answer
    3. Returns both the answer and source documents
    
    Args:
        query (RAGQuery): Question and RAG parameters
        
    Returns:
        RAGResponse: Generated answer with source documents and confidence
        
    Raises:
        HTTPException: If RAG processing fails
    """
    try:
        # Generate answer using RAG
        result = rag_engine.generate_answer(
            question=query.question,
            top_k=query.top_k,
            max_tokens=query.max_tokens
        )
        
        # Format source documents
        source_docs = []
        for doc in result["source_documents"]:
            source_docs.append(SearchResult(
                content=doc["content"],
                similarity_score=doc["similarity_score"],
                metadata=doc["metadata"],
                chunk_id=doc["chunk_id"]
            ))
        
        return RAGResponse(
            answer=result["answer"],
            source_documents=source_docs,
            confidence_score=result["confidence_score"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating RAG response: {str(e)}"
        )

@app.get("/documents")
async def list_documents():
    """
    List all uploaded documents and their metadata
    
    Returns:
        dict: List of documents with their processing statistics
    """
    try:
        documents = search_engine.get_all_documents()
        return {
            "total_documents": len(documents),
            "documents": documents
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving documents: {str(e)}"
        )

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document and all its associated chunks
    
    Args:
        document_id (str): ID of the document to delete
        
    Returns:
        dict: Deletion confirmation
        
    Raises:
        HTTPException: If document not found or deletion fails
    """
    try:
        deleted = search_engine.delete_document(document_id)
        
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )
        
        return {
            "message": f"Document {document_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting document: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    
    Returns:
        dict: Application health status and component checks
    """
    try:
        # Check database connection
        db_healthy = search_engine.health_check()
        
        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "database": "connected" if db_healthy else "disconnected",
            "components": {
                "document_processor": "initialized" if document_processor else "not_initialized",
                "search_engine": "initialized" if search_engine else "not_initialized",
                "rag_engine": "initialized" if rag_engine else "not_initialized"
            }
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 error handler"""
    return JSONResponse(
        status_code=404,
        content={"message": "Endpoint not found", "available_endpoints": ["/docs", "/search", "/rag", "/process-data-folder", "/data-folder-info"]}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 error handler"""
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "detail": "Please check the logs for more information"}
    )


#   What's happening: When you run python main.py, it starts the uvicorn server.
if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", 8000)),
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )