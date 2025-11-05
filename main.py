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

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

# Import our custom modules
from src.database import get_database_session
from src.document_processor import DocumentProcessor
from src.semantic_search import SemanticSearchEngine
from src.rag_engine import RAGEngine

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI application with metadata
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
document_processor: DocumentProcessor = None
search_engine: SemanticSearchEngine = None
rag_engine: RAGEngine = None

@app.on_event("startup")
async def startup_event():
    """
    Initialize application components on startup
    
    This function runs when the FastAPI application starts up and initializes:
    - Document processor for PDF handling
    - Semantic search engine with embeddings
    - RAG engine for question answering
    """
    global document_processor, search_engine, rag_engine
    
    try:
        # Initialize document processor
        document_processor = DocumentProcessor()
        
        # Initialize semantic search engine with database connection
        search_engine = SemanticSearchEngine()
        await search_engine.initialize()
        
        # Initialize RAG engine
        rag_engine = RAGEngine(search_engine)
        
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
        "endpoints": {
            "upload": "/upload-pdf",
            "search": "/search",
            "rag": "/rag",
            "documents": "/documents",
            "health": "/health"
        },
        "documentation": "/docs"
    }

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload and process a PDF document for semantic search
    
    This endpoint:
    1. Validates the uploaded file is a PDF
    2. Processes the PDF content into chunks
    3. Generates embeddings for each chunk
    4. Stores chunks and embeddings in PostgreSQL
    
    Args:
        file (UploadFile): The PDF file to upload and process
        
    Returns:
        dict: Processing results including number of chunks created
        
    Raises:
        HTTPException: If file is not PDF or processing fails
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Process the PDF document
        result = await document_processor.process_pdf(
            file_content=file_content,
            filename=file.filename
        )
        
        # Store processed chunks in vector database
        chunks_stored = await search_engine.store_document_chunks(
            chunks=result["chunks"],
            metadata=result["metadata"]
        )
        
        return {
            "message": f"Successfully processed {file.filename}",
            "chunks_created": len(result["chunks"]),
            "chunks_stored": chunks_stored,
            "document_id": result["document_id"],
            "metadata": result["metadata"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF: {str(e)}"
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
        results = await search_engine.search(
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
        result = await rag_engine.generate_answer(
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
        documents = await search_engine.get_all_documents()
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
        deleted = await search_engine.delete_document(document_id)
        
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
        db_healthy = await search_engine.health_check()
        
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
        content={"message": "Endpoint not found", "available_endpoints": ["/docs", "/search", "/rag", "/upload-pdf"]}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 error handler"""
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "detail": "Please check the logs for more information"}
    )

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