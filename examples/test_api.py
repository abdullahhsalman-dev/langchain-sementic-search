#!/usr/bin/env python3
"""
API Testing Script for LangChain Semantic Search Engine
=======================================================

This script demonstrates how to interact with the semantic search API
and provides examples for all major endpoints.

Usage:
    python examples/test_api.py

Make sure the FastAPI server is running on http://localhost:8000
"""

import requests
import json
import time
import os
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"
SAMPLE_PDF_PATH = "examples/sample_document.pdf"  # You'll need to provide this

class SemanticSearchAPITester:
    """
    Test client for the Semantic Search API
    
    Provides methods to test all API endpoints with detailed output
    and error handling.
    """
    
    def __init__(self, base_url: str = API_BASE_URL):
        """Initialize the API tester with base URL"""
        self.base_url = base_url
        self.session = requests.Session()
        
        # Store document IDs for cleanup
        self.uploaded_documents = []
    
    def test_health_check(self):
        """Test the health check endpoint"""
        print("🔍 Testing Health Check...")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                health_data = response.json()
                print("✅ Health Check Passed")
                print(f"   Status: {health_data.get('status')}")
                print(f"   Database: {health_data.get('database')}")
                print(f"   Components: {health_data.get('components')}")
                return True
            else:
                print(f"❌ Health Check Failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Health Check Error: {str(e)}")
            return False
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        print("\n🔍 Testing Root Endpoint...")
        
        try:
            response = self.session.get(f"{self.base_url}/")
            
            if response.status_code == 200:
                root_data = response.json()
                print("✅ Root Endpoint Working")
                print(f"   Message: {root_data.get('message')}")
                print(f"   Available Endpoints: {list(root_data.get('endpoints', {}).keys())}")
                return True
            else:
                print(f"❌ Root Endpoint Failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Root Endpoint Error: {str(e)}")
            return False
    
    def test_upload_pdf(self, pdf_path: str = None):
        """Test PDF upload functionality"""
        print("\n📄 Testing PDF Upload...")
        
        # Use provided path or default
        if not pdf_path:
            pdf_path = SAMPLE_PDF_PATH
        
        # Check if file exists
        if not os.path.exists(pdf_path):
            print(f"❌ PDF file not found: {pdf_path}")
            print("   Please provide a sample PDF file to test uploads")
            return False, None
        
        try:
            with open(pdf_path, 'rb') as pdf_file:
                files = {'file': (os.path.basename(pdf_path), pdf_file, 'application/pdf')}
                
                print(f"   Uploading: {os.path.basename(pdf_path)}")
                start_time = time.time()
                
                response = self.session.post(
                    f"{self.base_url}/upload-pdf",
                    files=files
                )
                
                upload_time = time.time() - start_time
                
                if response.status_code == 200:
                    upload_data = response.json()
                    document_id = upload_data.get('document_id')
                    
                    print("✅ PDF Upload Successful")
                    print(f"   Document ID: {document_id}")
                    print(f"   Chunks Created: {upload_data.get('chunks_created')}")
                    print(f"   Upload Time: {upload_time:.2f}s")
                    
                    # Store document ID for later tests
                    if document_id:
                        self.uploaded_documents.append(document_id)
                    
                    return True, document_id
                else:
                    print(f"❌ PDF Upload Failed: {response.status_code}")
                    print(f"   Error: {response.text}")
                    return False, None
                    
        except requests.exceptions.RequestException as e:
            print(f"❌ PDF Upload Error: {str(e)}")
            return False, None
        except FileNotFoundError:
            print(f"❌ PDF file not found: {pdf_path}")
            return False, None
    
    def test_semantic_search(self, query: str = "What is machine learning?"):
        """Test semantic search functionality"""
        print(f"\n🔍 Testing Semantic Search...")
        print(f"   Query: '{query}'")
        
        search_payload = {
            "query": query,
            "top_k": 5,
            "similarity_threshold": 0.7
        }
        
        try:
            start_time = time.time()
            
            response = self.session.post(
                f"{self.base_url}/search",
                json=search_payload,
                headers={'Content-Type': 'application/json'}
            )
            
            search_time = time.time() - start_time
            
            if response.status_code == 200:
                results = response.json()
                
                print("✅ Semantic Search Successful")
                print(f"   Results Found: {len(results)}")
                print(f"   Search Time: {search_time:.3f}s")
                
                for i, result in enumerate(results[:3]):  # Show top 3 results
                    print(f"\n   Result {i+1}:")
                    print(f"     Similarity: {result.get('similarity_score', 0):.3f}")
                    print(f"     Content: {result.get('content', '')[:100]}...")
                    print(f"     Source: {result.get('metadata', {}).get('filename', 'Unknown')}")
                
                return True, results
            else:
                print(f"❌ Semantic Search Failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False, None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Semantic Search Error: {str(e)}")
            return False, None
    
    def test_rag_query(self, question: str = "What are the main benefits discussed in the document?"):
        """Test RAG (Retrieval Augmented Generation) functionality"""
        print(f"\n🤖 Testing RAG Query...")
        print(f"   Question: '{question}'")
        
        rag_payload = {
            "question": question,
            "top_k": 3,
            "max_tokens": 512
        }
        
        try:
            start_time = time.time()
            
            response = self.session.post(
                f"{self.base_url}/rag",
                json=rag_payload,
                headers={'Content-Type': 'application/json'}
            )
            
            rag_time = time.time() - start_time
            
            if response.status_code == 200:
                rag_data = response.json()
                
                print("✅ RAG Query Successful")
                print(f"   Answer Generated in: {rag_time:.2f}s")
                print(f"   Confidence Score: {rag_data.get('confidence_score', 0):.3f}")
                print(f"   Source Documents: {len(rag_data.get('source_documents', []))}")
                
                answer = rag_data.get('answer', '')
                print(f"\n   Generated Answer:")
                print(f"   {answer[:300]}{'...' if len(answer) > 300 else ''}")
                
                return True, rag_data
            else:
                print(f"❌ RAG Query Failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False, None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ RAG Query Error: {str(e)}")
            return False, None
    
    def test_list_documents(self):
        """Test document listing functionality"""
        print("\n📚 Testing Document Listing...")
        
        try:
            response = self.session.get(f"{self.base_url}/documents")
            
            if response.status_code == 200:
                docs_data = response.json()
                documents = docs_data.get('documents', [])
                
                print("✅ Document Listing Successful")
                print(f"   Total Documents: {docs_data.get('total_documents', 0)}")
                
                for i, doc in enumerate(documents[:3]):  # Show first 3 documents
                    print(f"\n   Document {i+1}:")
                    print(f"     ID: {doc.get('document_id', 'Unknown')}")
                    print(f"     Filename: {doc.get('filename', 'Unknown')}")
                    print(f"     Chunks: {doc.get('chunk_count', 0)}")
                    print(f"     Size: {doc.get('file_size_bytes', 0)} bytes")
                
                return True, documents
            else:
                print(f"❌ Document Listing Failed: {response.status_code}")
                return False, None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Document Listing Error: {str(e)}")
            return False, None
    
    def test_delete_document(self, document_id: str):
        """Test document deletion functionality"""
        print(f"\n🗑️  Testing Document Deletion...")
        print(f"   Document ID: {document_id}")
        
        try:
            response = self.session.delete(f"{self.base_url}/documents/{document_id}")
            
            if response.status_code == 200:
                delete_data = response.json()
                print("✅ Document Deletion Successful")
                print(f"   Message: {delete_data.get('message')}")
                return True
            elif response.status_code == 404:
                print("⚠️  Document Not Found (already deleted or doesn't exist)")
                return True  # Consider this a success for cleanup
            else:
                print(f"❌ Document Deletion Failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Document Deletion Error: {str(e)}")
            return False
    
    def cleanup_uploaded_documents(self):
        """Clean up any documents uploaded during testing"""
        if not self.uploaded_documents:
            return
        
        print(f"\n🧹 Cleaning up {len(self.uploaded_documents)} uploaded documents...")
        
        for doc_id in self.uploaded_documents:
            self.test_delete_document(doc_id)
        
        self.uploaded_documents.clear()
    
    def run_full_test_suite(self):
        """Run all tests in sequence"""
        print("🚀 Starting Full API Test Suite")
        print("=" * 50)
        
        test_results = {}
        
        # Basic connectivity tests
        test_results['health'] = self.test_health_check()
        test_results['root'] = self.test_root_endpoint()
        
        # Document management tests
        upload_success, document_id = self.test_upload_pdf()
        test_results['upload'] = upload_success
        
        if upload_success and document_id:
            # Only test search and RAG if we have documents
            test_results['search'] = self.test_semantic_search()[0]
            test_results['rag'] = self.test_rag_query()[0]
        
        # Administrative tests
        test_results['list_docs'] = self.test_list_documents()[0]
        
        # Cleanup
        self.cleanup_uploaded_documents()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Test Results Summary")
        print("=" * 50)
        
        passed = sum(1 for result in test_results.values() if result)
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.upper():15} {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All tests passed! Your API is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the error messages above.")
        
        return test_results

def main():
    """Main function to run API tests"""
    print("LangChain Semantic Search Engine - API Tester")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Server not responding correctly at {API_BASE_URL}")
            print("   Make sure the FastAPI server is running:")
            print("   python main.py")
            return
    except requests.exceptions.RequestException:
        print(f"❌ Cannot connect to server at {API_BASE_URL}")
        print("   Make sure the FastAPI server is running:")
        print("   python main.py")
        return
    
    # Create tester and run tests
    tester = SemanticSearchAPITester()
    
    # Check for sample PDF
    if not os.path.exists(SAMPLE_PDF_PATH):
        print(f"\n⚠️  Sample PDF not found at {SAMPLE_PDF_PATH}")
        print("   Some tests may be skipped without a sample document")
        print("   You can provide any PDF file for testing")
    
    # Run the test suite
    results = tester.run_full_test_suite()
    
    return results

if __name__ == "__main__":
    main()