#!/usr/bin/env python3
"""
Example Usage Script for LangChain Semantic Search Engine
=========================================================

This script shows how to use the semantic search engine programmatically
by importing the modules directly (without using the REST API).

This is useful for:
- Batch processing multiple documents
- Custom integrations
- Advanced configuration and optimization
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.document_processor import DocumentProcessor
from src.semantic_search import SemanticSearchEngine
from src.rag_engine import RAGEngine

async def example_document_processing():
    """
    Example: Process a PDF document and extract chunks
    """
    print("📄 Example: Document Processing")
    print("-" * 40)
    
    # Initialize document processor
    processor = DocumentProcessor(
        chunk_size=800,      # Smaller chunks for better precision
        chunk_overlap=150,   # Good overlap for context preservation
        min_chunk_size=50    # Minimum chunk size
    )
    
    # Sample PDF path (you'll need to provide this)
    sample_pdf = "examples/sample_document.pdf"
    
    if not os.path.exists(sample_pdf):
        print(f"⚠️  Sample PDF not found at {sample_pdf}")
        print("   Please provide a PDF file to test document processing")
        return None
    
    try:
        # Read the PDF file
        with open(sample_pdf, 'rb') as f:
            pdf_content = f.read()
        
        # Process the PDF
        print(f"Processing: {os.path.basename(sample_pdf)}")
        result = await processor.process_pdf(pdf_content, os.path.basename(sample_pdf))
        
        print(f"✅ Processing completed:")
        print(f"   Document ID: {result['document_id']}")
        print(f"   Total chunks: {result['total_chunks']}")
        print(f"   Original text length: {result['original_text_length']:,} chars")
        print(f"   Cleaned text length: {result['cleaned_text_length']:,} chars")
        
        # Show sample chunks
        print(f"\n📝 Sample chunks:")
        for i, chunk in enumerate(result['chunks'][:3]):
            print(f"\n   Chunk {i+1}:")
            print(f"     ID: {chunk.chunk_id}")
            print(f"     Length: {len(chunk.content)} chars")
            print(f"     Content: {chunk.content[:100]}...")
        
        return result
        
    except Exception as e:
        print(f"❌ Error processing document: {str(e)}")
        return None

async def example_semantic_search():
    """
    Example: Set up semantic search engine and perform searches
    """
    print("\n🔍 Example: Semantic Search Setup")
    print("-" * 40)
    
    try:
        # Initialize search engine
        search_engine = SemanticSearchEngine(
            model_name="all-MiniLM-L6-v2",  # Fast, efficient model
            cache_embeddings=True
        )
        
        # Initialize the engine
        await search_engine.initialize()
        
        print("✅ Search engine initialized")
        print(f"   Model: {search_engine.model_name}")
        print(f"   Embedding dimension: {search_engine.embedding_dimension}")
        
        # Test embedding generation
        test_texts = [
            "Machine learning is a subset of artificial intelligence",
            "Natural language processing helps computers understand text",
            "Vector databases enable semantic search capabilities"
        ]
        
        print(f"\n🔄 Generating embeddings for {len(test_texts)} test texts...")
        embeddings = search_engine.generate_batch_embeddings(test_texts)
        
        print(f"✅ Embeddings generated:")
        for i, (text, embedding) in enumerate(zip(test_texts, embeddings)):
            print(f"   Text {i+1}: {text[:50]}...")
            print(f"   Embedding shape: {embedding.shape}")
            print(f"   Sample values: [{embedding[0]:.3f}, {embedding[1]:.3f}, ...]")
        
        return search_engine
        
    except Exception as e:
        print(f"❌ Error setting up search engine: {str(e)}")
        return None

async def example_rag_setup():
    """
    Example: Set up RAG engine for question answering
    """
    print("\n🤖 Example: RAG Engine Setup")
    print("-" * 40)
    
    # First set up search engine
    search_engine = await example_semantic_search()
    if not search_engine:
        print("❌ Cannot set up RAG without search engine")
        return None
    
    try:
        # Initialize RAG engine
        rag_engine = RAGEngine(
            search_engine=search_engine,
            model_name="gpt2",  # Use simpler model for example
            max_context_length=1000,
            temperature=0.7
        )
        
        # Initialize the RAG engine
        await rag_engine.initialize()
        
        print("✅ RAG engine initialized")
        print(f"   Language model: {rag_engine.model_name}")
        print(f"   Device: {rag_engine.device}")
        print(f"   Max context length: {rag_engine.max_context_length}")
        
        return rag_engine
        
    except Exception as e:
        print(f"❌ Error setting up RAG engine: {str(e)}")
        return None

async def example_full_pipeline():
    """
    Example: Complete pipeline from document upload to question answering
    """
    print("\n🔄 Example: Complete Pipeline")
    print("-" * 40)
    
    # Sample document (you would provide this)
    sample_pdf = "examples/sample_document.pdf"
    
    if not os.path.exists(sample_pdf):
        print(f"⚠️  Sample PDF not found at {sample_pdf}")
        print("   Skipping full pipeline example")
        return
    
    try:
        # Step 1: Process document
        print("Step 1: Processing document...")
        doc_result = await example_document_processing()
        if not doc_result:
            return
        
        # Step 2: Set up search engine
        print("\nStep 2: Setting up search engine...")
        search_engine = await example_semantic_search()
        if not search_engine:
            return
        
        # Step 3: Store document chunks
        print("\nStep 3: Storing document chunks...")
        chunks_stored = await search_engine.store_document_chunks(
            chunks=doc_result['chunks'],
            metadata=doc_result['metadata']
        )
        print(f"✅ Stored {chunks_stored} chunks in vector database")
        
        # Step 4: Perform semantic search
        print("\nStep 4: Testing semantic search...")
        search_queries = [
            "What is the main topic of this document?",
            "key benefits",
            "important concepts"
        ]
        
        for query in search_queries:
            print(f"\n   Query: '{query}'")
            results = await search_engine.search(query, top_k=3)
            print(f"   Found {len(results)} results")
            
            if results:
                best_result = results[0]
                print(f"   Best match (score: {best_result['similarity_score']:.3f}):")
                print(f"   {best_result['content'][:150]}...")
        
        # Step 5: Set up and test RAG
        print("\nStep 5: Setting up RAG for question answering...")
        rag_engine = RAGEngine(search_engine)
        await rag_engine.initialize()
        
        # Test RAG questions
        rag_questions = [
            "What are the main points discussed in this document?",
            "Can you summarize the key information?",
            "What should I know about this topic?"
        ]
        
        for question in rag_questions:
            print(f"\n   Question: '{question}'")
            try:
                answer_result = await rag_engine.generate_answer(
                    question=question,
                    top_k=3,
                    max_tokens=200
                )
                
                print(f"   Confidence: {answer_result['confidence_score']:.3f}")
                print(f"   Answer: {answer_result['answer'][:200]}...")
                
            except Exception as e:
                print(f"   ⚠️  RAG generation failed: {str(e)}")
        
        print("\n✅ Full pipeline completed successfully!")
        
    except Exception as e:
        print(f"❌ Pipeline error: {str(e)}")

async def example_performance_testing():
    """
    Example: Performance testing and optimization
    """
    print("\n📊 Example: Performance Testing")
    print("-" * 40)
    
    try:
        # Initialize components
        search_engine = SemanticSearchEngine(cache_embeddings=True)
        await search_engine.initialize()
        
        # Test embedding generation performance
        import time
        
        test_texts = [
            f"This is test document number {i} with some content about machine learning and AI."
            for i in range(50)
        ]
        
        # Test individual embedding generation
        print("Testing individual embedding generation...")
        start_time = time.time()
        for text in test_texts[:10]:
            embedding = search_engine.generate_embedding(text)
        individual_time = time.time() - start_time
        
        # Test batch embedding generation
        print("Testing batch embedding generation...")
        start_time = time.time()
        batch_embeddings = search_engine.generate_batch_embeddings(test_texts[:10])
        batch_time = time.time() - start_time
        
        print(f"✅ Performance results:")
        print(f"   Individual generation: {individual_time:.3f}s for 10 texts")
        print(f"   Batch generation: {batch_time:.3f}s for 10 texts")
        print(f"   Speedup: {individual_time/batch_time:.2f}x faster with batching")
        
        # Test caching
        print("\nTesting embedding cache...")
        start_time = time.time()
        for text in test_texts[:5]:  # Same texts again
            embedding = search_engine.generate_embedding(text)
        cache_time = time.time() - start_time
        
        print(f"   Cache test: {cache_time:.3f}s for 5 cached texts")
        
        # Get statistics
        stats = search_engine.get_search_statistics()
        print(f"\n📈 Search engine statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
    except Exception as e:
        print(f"❌ Performance testing error: {str(e)}")

async def main():
    """
    Main function demonstrating various usage examples
    """
    print("LangChain Semantic Search Engine - Usage Examples")
    print("=" * 60)
    
    examples = [
        ("Document Processing", example_document_processing),
        ("Semantic Search Setup", example_semantic_search),
        ("RAG Engine Setup", example_rag_setup),
        ("Performance Testing", example_performance_testing),
        ("Full Pipeline", example_full_pipeline),
    ]
    
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    
    print("\nRunning all examples...")
    print("=" * 60)
    
    for name, example_func in examples:
        try:
            await example_func()
        except Exception as e:
            print(f"❌ Error in {name}: {str(e)}")
        
        print()  # Add spacing between examples
    
    print("=" * 60)
    print("✅ All examples completed!")
    
    print("\n💡 Next steps:")
    print("1. Provide sample PDF files in the examples/ directory")
    print("2. Set up PostgreSQL with pgvector extension")
    print("3. Configure your .env file with database credentials")
    print("4. Run the FastAPI server: python main.py")
    print("5. Test the API with: python examples/test_api.py")

if __name__ == "__main__":
    asyncio.run(main())