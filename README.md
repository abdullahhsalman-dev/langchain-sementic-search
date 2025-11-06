# LangChain Semantic Search Engine

A powerful semantic search engine built with LangChain, FastAPI, and PostgreSQL that enables intelligent document search and question-answering over PDF documents using **completely free technologies**.

## ✨ Features

- **📁 Automatic PDF Processing**: Simply drop PDF files in the `data/` folder for automatic processing
- **🔍 Semantic Search**: Find relevant content using natural language queries instead of keyword matching
- **🤖 RAG Question Answering**: Get comprehensive answers to questions based on your document content
- **🆓 Completely Free**: Uses only free and open-source technologies
- **🚀 High Performance**: Optimized vector storage with PostgreSQL and pgvector
- **📊 RESTful API**: Clean FastAPI interface with automatic documentation
- **💾 Persistent Storage**: All data stored in PostgreSQL with vector indexing
- **📈 Analytics**: Built-in performance monitoring and search statistics
- **🔄 Smart Processing**: Only processes new or modified files, skips duplicates

## 🛠️ Technology Stack

### Core Technologies (All Free!)
- **FastAPI**: Modern Python web framework for building APIs
- **LangChain**: Framework for developing LLM-powered applications
- **PostgreSQL + pgvector**: Vector database for efficient similarity search
- **Sentence Transformers**: Free, high-quality text embeddings
- **Hugging Face Transformers**: Free language models for text generation

### Key Dependencies
- `sentence-transformers`: Generates semantic embeddings
- `pgvector`: PostgreSQL extension for vector operations
- `pymupdf`: Robust PDF text extraction
- `transformers`: Language model inference
- `psycopg2`: PostgreSQL database connectivity

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   LangChain      │    │  PostgreSQL     │
│   Web Server    │◄──►│   Processing     │◄──►│  + pgvector     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        ▲                        ▲                       ▲
        │                        │                       │
        ▼                        ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   PDF Upload    │    │  Sentence        │    │  Vector Search  │
│   & Processing  │    │  Transformers    │    │  & Storage      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🧩 What Does What - Component Breakdown

### 📁 **Project Structure & File Roles**

```
langchain-sementic-search/
├── main.py                    # 🚀 FastAPI application & API endpoints
├── requirements.txt           # 📦 Python dependencies
├── .env.example              # ⚙️  Environment configuration template
├── setup.py                  # 🔧 Automated setup & installation script
├── src/                      # 📚 Core application modules
│   ├── document_processor.py # 📄 PDF processing & text chunking
│   ├── database.py           # 🗄️  PostgreSQL & vector operations
│   ├── semantic_search.py    # 🔍 Embeddings & similarity search
│   ├── rag_engine.py         # 🤖 Question answering engine
│   └── data_loader.py        # 📁 Automatic PDF folder processing
├── data/                     # 📂 Place your PDF files here for auto-processing
└── examples/                 # 💡 Usage examples & testing tools
    ├── test_api.py           # 🧪 Complete API testing suite
    └── example_usage.py      # 📖 Direct module usage examples
```

### 🔧 **Core Modules Explained**

#### **1. `main.py` - FastAPI Web Server**
**What it does:**
- Creates REST API endpoints for all functionality
- Handles HTTP requests and responses
- Manages application startup and component initialization
- Provides automatic API documentation at `/docs`

**Key endpoints:**
- `POST /process-data-folder` → Process PDFs from data/ directory
- `GET /data-folder-info` → Get info about processed files
- `POST /search` → Perform semantic search
- `POST /rag` → Ask questions using RAG
- `GET /documents` → List all processed documents
- `DELETE /documents/{id}` → Remove documents

#### **2. `src/document_processor.py` - PDF Processing Engine**
**What it does:**
- Extracts text from PDF files using PyMuPDF
- Cleans and preprocesses extracted text
- Splits documents into manageable chunks
- Generates metadata for documents and chunks

**Key functions:**
- `process_pdf()` → Main PDF processing pipeline
- `_extract_pdf_text()` → Raw text extraction from PDF
- `_clean_text()` → Text normalization and cleaning
- `_generate_document_id()` → Unique document identification

**Why chunking matters:**
- Large documents need to be split for effective search
- Overlapping chunks preserve context between sections
- Optimal chunk size balances specificity vs context

#### **3. `src/database.py` - PostgreSQL Vector Database**
**What it does:**
- Manages PostgreSQL database connections
- Stores document metadata and text chunks
- Handles vector embeddings storage with pgvector
- Performs vector similarity searches

**Key components:**
- `Document` model → Stores document metadata
- `DocumentChunk` model → Stores text chunks + embeddings
- `DatabaseManager` → Database operations and connections
- Vector indexing → HNSW indexes for fast similarity search

**Why PostgreSQL + pgvector:**
- Production-ready database with ACID compliance
- Native vector operations with efficient indexing
- Scalable for large document collections
- Free and open-source

#### **4. `src/semantic_search.py` - Embedding & Search Engine**
**What it does:**
- Loads sentence transformer models for embeddings
- Converts text to high-dimensional vectors
- Performs semantic similarity search
- Caches embeddings for performance

**Key features:**
- `generate_embedding()` → Convert text to vector
- `generate_batch_embeddings()` → Efficient batch processing
- `search()` → Semantic similarity search
- Embedding cache → Speeds up repeated queries

**How semantic search works:**
1. Convert query text to vector embedding
2. Find similar vectors in database using cosine similarity
3. Return most relevant text chunks with similarity scores
4. No keyword matching - understands meaning and context

#### **5. `src/rag_engine.py` - Question Answering Engine**
**What it does:**
- Retrieves relevant context using semantic search
- Generates human-like answers using language models
- Combines retrieval and generation for accurate responses
- Calculates confidence scores for answers

**RAG Process:**
1. **Retrieve** → Find relevant documents for the question
2. **Augment** → Add context to the question prompt
3. **Generate** → Use language model to create comprehensive answer

**Key features:**
- `generate_answer()` → Complete RAG pipeline
- Context preparation → Formats retrieved documents
- Confidence scoring → Estimates answer reliability
- Fallback handling → Works even if model loading fails

#### **6. `src/data_loader.py` - Automatic PDF Folder Processing**
**What it does:**
- Scans the data/ directory for PDF files
- Tracks processed files to avoid duplicates
- Processes new or modified files automatically
- Provides batch processing for efficiency

**Key features:**
- `process_all_files()` → Process all PDFs in data/ folder
- `scan_data_directory()` → Find all PDF files recursively
- File change detection → Only process modified files
- Processing cache → Remembers what's been processed
- Batch operations → Efficient processing of multiple files

**How it works:**
1. Scans data/ directory for PDF files (including subdirectories)
2. Calculates file hashes to detect changes
3. Processes only new or modified files
4. Stores processing metadata in cache file
5. Automatically runs on application startup

### 🔄 **Data Flow - How Everything Works Together**

#### **Document Processing Flow:**
```
PDF Files in data/ → data_loader → document_processor → Text Chunks → 
semantic_search → Vector Embeddings → database → PostgreSQL Storage
```

1. **PDF Detection**: Application scans data/ directory for PDF files
2. **Change Detection**: Check file hashes to identify new/modified files
3. **Text Extraction**: PyMuPDF extracts raw text from each PDF
4. **Text Cleaning**: Remove unwanted characters, normalize spacing
5. **Chunking**: Split text into overlapping segments (default: 1000 chars)
6. **Embedding Generation**: Convert each chunk to 384-dimension vector
7. **Database Storage**: Store chunks + embeddings in PostgreSQL
8. **Cache Update**: Remember processed files to avoid duplicates

#### **Search Flow:**
```
User Query → semantic_search → Vector Embedding → database → 
Similarity Search → Ranked Results → JSON Response
```

1. **Query Input**: User submits search query via `/search` endpoint
2. **Query Embedding**: Convert query to same vector space as documents
3. **Vector Search**: PostgreSQL finds similar vectors using cosine similarity
4. **Ranking**: Results ranked by similarity score (0-1)
5. **Response**: Return matching text chunks with metadata

#### **RAG Question Answering Flow:**
```
Question → semantic_search → Relevant Context → rag_engine → 
Language Model → Generated Answer → Confidence Score
```

1. **Question Input**: User asks question via `/rag` endpoint
2. **Context Retrieval**: Find 3-5 most relevant document chunks
3. **Prompt Construction**: Combine question + context into structured prompt
4. **Answer Generation**: Language model generates comprehensive response
5. **Confidence Scoring**: Calculate reliability based on context quality

### 🛠️ **Technology Choices Explained**

#### **Why These Technologies?**

**FastAPI:**
- Modern, fast Python web framework
- Automatic API documentation with Swagger UI
- Built-in request/response validation
- Async support for better performance

**PostgreSQL + pgvector:**
- Production-ready relational database
- Native vector operations (no separate vector DB needed)
- ACID compliance and data integrity
- Mature ecosystem and tooling

**Sentence Transformers:**
- State-of-the-art embedding models
- Pre-trained on massive datasets
- Completely free to use
- Multiple model options for different needs

**Hugging Face Transformers:**
- Access to thousands of free language models
- Easy model switching and experimentation
- Local inference (no API calls needed)
- GPU acceleration support

### 🎯 **Key Features Breakdown**

#### **Semantic Search vs Keyword Search:**
- **Keyword**: Searches for exact word matches
- **Semantic**: Understands meaning, context, and intent
- **Example**: Query "car" finds documents about "automobile", "vehicle"

#### **RAG vs Simple QA:**
- **Simple QA**: Answers from model's training data only
- **RAG**: Answers based on your specific documents
- **Advantage**: Up-to-date, domain-specific, factual responses

#### **Chunking Strategy:**
- **Purpose**: Break large documents into searchable segments
- **Overlap**: Preserves context between chunks
- **Size**: Balance between specificity and context (1000 chars default)

#### **Vector Embeddings:**
- **What**: High-dimensional numerical representations of text
- **Why**: Enable mathematical similarity comparisons
- **Dimension**: 384 numbers per text chunk (all-MiniLM-L6-v2 model)

### 📊 **Performance Optimizations**

#### **Caching Layer:**
- Embedding cache → Avoids re-computing same embeddings
- Connection pooling → Reuses database connections
- Batch processing → Processes multiple texts efficiently

#### **Database Optimizations:**
- HNSW indexes → Fast approximate similarity search
- Vector-optimized storage → Efficient embedding storage
- Query optimization → Smart similarity thresholds

#### **Model Optimizations:**
- GPU acceleration → Faster embedding generation
- Model caching → Avoid reloading models
- Batch embedding → Process multiple texts together

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed on your system
2. **PostgreSQL 12+** with superuser access
3. **Git** for cloning the repository

### 1. Clone the Repository

```bash
git clone <repository-url>
cd langchain-sementic-search
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Set Up PostgreSQL Database

#### Install PostgreSQL and pgvector

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo apt install postgresql-14-pgvector  # Adjust version as needed
```

**macOS (using Homebrew):**
```bash
brew install postgresql
brew install pgvector
```

**Windows:**
- Download PostgreSQL from [official website](https://www.postgresql.org/download/windows/)
- Install pgvector following [these instructions](https://github.com/pgvector/pgvector#installation)

#### Create Database

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE semantic_search_db;
CREATE USER your_username WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE semantic_search_db TO your_username;

# Exit PostgreSQL
\q
```

### 4. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
nano .env
```

**Update `.env` with your configuration:**
```env
# Database Configuration
DATABASE_URL=postgresql://your_username:your_password@localhost:5432/semantic_search_db

# Server Configuration
HOST=127.0.0.1
PORT=8000

# Embedding Model Configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2

# LLM Configuration
LLM_MODEL=microsoft/DialoGPT-medium
```

### 5. Initialize Database

The application will automatically create tables and install the pgvector extension on first run.

### 6. Run the Application

```bash
# Start the FastAPI server
python main.py

# Or using uvicorn directly
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 7. Add PDF Files and Start Using

```bash
# Add your PDF files to the data directory
cp your_document.pdf data/

# The application will automatically process them on startup
# Or manually trigger processing via API
```

### 8. Access the Application

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📖 API Usage

### Process PDF Documents

**Automatic Processing:**
PDF files are automatically processed when placed in the `data/` directory and the application starts.

**Manual Processing:**
```bash
# Process all new/modified files in data/ folder
curl -X POST "http://localhost:8000/process-data-folder"

# Force reprocess all files
curl -X POST "http://localhost:8000/process-data-folder?force_reprocess=true"
```

**Response:**
```json
{
  "message": "Data folder processing completed",
  "processing_summary": {
    "files_processed": 2,
    "files_skipped": 1,
    "total_processing_time": 15.3,
    "processed_documents": ["doc_report_20231105_a1b2c3d4", "doc_manual_20231105_e5f6g7h8"]
  }
}
```

### Check Data Folder Status

```bash
curl -X GET "http://localhost:8000/data-folder-info"
```

### Perform Semantic Search

```bash
curl -X POST "http://localhost:8000/search" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main benefits of renewable energy?",
    "top_k": 5,
    "similarity_threshold": 0.7
  }'
```

**Response:**
```json
[
  {
    "content": "Renewable energy sources offer numerous advantages including reduced greenhouse gas emissions, energy independence, and long-term cost savings...",
    "similarity_score": 0.92,
    "metadata": {
      "document_id": "doc_energy_report_20231105_a1b2c3d4",
      "filename": "energy_report.pdf",
      "chunk_index": 12
    },
    "chunk_id": "doc_energy_report_20231105_a1b2c3d4_chunk_12"
  }
]
```

### Ask Questions (RAG)

```bash
curl -X POST "http://localhost:8000/rag" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main challenges facing renewable energy adoption?",
    "top_k": 3,
    "max_tokens": 512
  }'
```

**Response:**
```json
{
  "answer": "Based on the documents, the main challenges facing renewable energy adoption include: 1) High initial capital costs for installation, 2) Intermittency issues with solar and wind power, 3) Need for improved energy storage solutions, and 4) Existing infrastructure that favors fossil fuels. However, technological advances and government incentives are helping to address these challenges.",
  "source_documents": [...],
  "confidence_score": 0.85
}
```

### List All Documents

```bash
curl -X GET "http://localhost:8000/documents"
```

### Delete a Document

```bash
curl -X DELETE "http://localhost:8000/documents/doc_your_document_20231105_a1b2c3d4"
```

## 🐳 Docker Setup (Optional)

### Using Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg15
    environment:
      POSTGRES_DB: semantic_search_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/semantic_search_db
    depends_on:
      - postgres
    volumes:
      - ./:/app

volumes:
  postgres_data:
```

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔧 Configuration Options

### Embedding Models

You can use different sentence transformer models by updating the `EMBEDDING_MODEL` in your `.env` file:

```env
# Fast and lightweight (384 dimensions)
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Better quality (768 dimensions)
EMBEDDING_MODEL=all-mpnet-base-v2

# Multilingual support
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
```

### Language Models for RAG

Update the `LLM_MODEL` in your `.env` file:

```env
# Conversational model (default)
LLM_MODEL=microsoft/DialoGPT-medium

# General purpose model
LLM_MODEL=gpt2

# Instruction-following model
LLM_MODEL=microsoft/DialoGPT-large
```

### Document Processing

Modify chunking parameters in `src/document_processor.py`:

```python
DocumentProcessor(
    chunk_size=1000,        # Characters per chunk
    chunk_overlap=200,      # Overlap between chunks
    min_chunk_size=100      # Minimum chunk size
)
```

## 📊 Performance Optimization

### Database Indexing

The application automatically creates HNSW indexes for fast vector similarity search:

```sql
CREATE INDEX document_chunks_embedding_idx 
ON document_chunks USING hnsw (embedding vector_cosine_ops);
```

### Memory Management

- **Embedding Cache**: Frequently used embeddings are cached in memory
- **Batch Processing**: Documents are processed in batches for efficiency
- **Connection Pooling**: Database connections are pooled for better performance

### GPU Acceleration

If you have a CUDA-compatible GPU, the application will automatically use it for faster embedding generation and text generation.

## 🧪 Testing

### Manual Testing

1. **Health Check**: Visit http://localhost:8000/health
2. **Upload Test PDF**: Use the `/docs` interface to upload a sample PDF
3. **Test Search**: Try searching for content from your uploaded document
4. **Test RAG**: Ask questions about your document content

### Automated Testing

```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest tests/
```

## 🔍 Troubleshooting

### Common Issues

#### 1. pgvector Extension Not Found
```bash
# Install pgvector extension
sudo apt install postgresql-14-pgvector

# Or build from source
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

#### 2. Memory Issues with Large Models
- Use smaller embedding models (all-MiniLM-L6-v2)
- Reduce batch sizes in processing
- Enable model offloading for GPU systems

#### 3. Database Connection Issues
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify database credentials in `.env`
- Ensure database exists and user has proper permissions

#### 4. PDF Processing Failures
- Ensure PDF is not password-protected
- Check PDF is not corrupted
- Some PDFs may have non-standard formats

### Debug Mode

Enable debug logging by setting environment variable:
```bash
export FASTAPI_DEBUG=true
python main.py
```

## 🤝 Contributing

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd langchain-sementic-search

# Create development environment
python -m venv dev-env
source dev-env/bin/activate

# Install development dependencies
pip install -r requirements.txt
pip install black flake8 pytest

# Install pre-commit hooks
pre-commit install
```

### Code Style

```bash
# Format code
black .

# Check linting
flake8 src/

# Run type checking
mypy src/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangChain** for the excellent framework for LLM applications
- **Sentence Transformers** for providing free, high-quality embeddings
- **pgvector** for efficient vector operations in PostgreSQL
- **FastAPI** for the modern Python web framework
- **Hugging Face** for democratizing access to language models

## 📞 Support

For questions, issues, or contributions:

1. **GitHub Issues**: Report bugs or request features
2. **Documentation**: Check this README and API docs at `/docs`
3. **Community**: Join discussions in the issues section

## 🗺️ Roadmap

### Upcoming Features

- [ ] **Multiple File Types**: Support for Word documents, text files, and web pages
- [ ] **Advanced RAG**: Multi-document reasoning and citation tracking
- [ ] **User Management**: Authentication and user-specific document collections
- [ ] **Real-time Processing**: WebSocket support for live document processing
- [ ] **Advanced Analytics**: Document similarity analysis and topic modeling
- [ ] **API Keys**: Rate limiting and API key management
- [ ] **Cloud Deployment**: Docker containers and cloud deployment guides

---

**Happy Searching! 🔍✨**