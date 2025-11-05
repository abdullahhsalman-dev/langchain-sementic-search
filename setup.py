#!/usr/bin/env python3
"""
Setup Script for LangChain Semantic Search Engine
=================================================

This script helps set up the environment and dependencies for the semantic search engine.

Usage:
    python setup.py
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} is compatible")
    return True

def check_postgresql():
    """Check if PostgreSQL is installed and accessible"""
    print("\n🐘 Checking PostgreSQL...")
    
    try:
        result = subprocess.run(['psql', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ PostgreSQL found: {version}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("❌ PostgreSQL not found or not accessible")
    print("   Please install PostgreSQL:")
    
    system = platform.system().lower()
    if system == "linux":
        print("   sudo apt update && sudo apt install postgresql postgresql-contrib")
    elif system == "darwin":  # macOS
        print("   brew install postgresql")
    elif system == "windows":
        print("   Download from: https://www.postgresql.org/download/windows/")
    
    return False

def install_requirements():
    """Install Python requirements"""
    print("\n📦 Installing Python requirements...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def setup_environment():
    """Set up environment configuration"""
    print("\n⚙️  Setting up environment configuration...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_example.exists():
        print("❌ .env.example not found")
        return False
    
    # Copy example to .env
    try:
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ Created .env file from template")
        print("   Please edit .env with your database credentials")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def check_pgvector():
    """Check if pgvector extension is available"""
    print("\n🔍 Checking pgvector extension...")
    
    # This would require database connection, so we'll just provide instructions
    print("⚠️  Please ensure pgvector extension is installed:")
    
    system = platform.system().lower()
    if system == "linux":
        print("   sudo apt install postgresql-14-pgvector")
    elif system == "darwin":  # macOS
        print("   brew install pgvector")
    elif system == "windows":
        print("   Follow instructions at: https://github.com/pgvector/pgvector#installation")
    
    print("\n   After installation, connect to PostgreSQL and run:")
    print("   CREATE EXTENSION IF NOT EXISTS vector;")
    
    return True

def create_sample_structure():
    """Create necessary directories and sample files"""
    print("\n📁 Creating project structure...")
    
    directories = [
        "examples",
        "tests",
        "logs"
    ]
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"   Created: {directory}/")
    
    # Create a simple test PDF info file
    sample_info = Path("examples/README.md")
    if not sample_info.exists():
        with open(sample_info, 'w') as f:
            f.write("""# Examples Directory

Place your sample PDF files here for testing.

## Sample Files Needed

- `sample_document.pdf` - A sample PDF for testing document processing
- Any other PDF files you want to test with

## Running Examples

```bash
# Test the API
python examples/test_api.py

# Run usage examples
python examples/example_usage.py
```
""")
        print("   Created: examples/README.md")
    
    print("✅ Project structure created")
    return True

def print_next_steps():
    """Print next steps for the user"""
    print("\n🎯 Next Steps:")
    print("-" * 40)
    
    steps = [
        "1. Edit .env file with your PostgreSQL credentials",
        "2. Create PostgreSQL database: CREATE DATABASE semantic_search_db;",
        "3. Install pgvector extension in your database",
        "4. Place sample PDF files in examples/ directory",
        "5. Run the application: python main.py",
        "6. Test the API: python examples/test_api.py",
        "7. Visit http://localhost:8000/docs for API documentation"
    ]
    
    for step in steps:
        print(f"   {step}")

def main():
    """Main setup function"""
    print("LangChain Semantic Search Engine - Setup")
    print("=" * 50)
    
    success = True
    
    # Run all setup checks
    checks = [
        ("Python Version", check_python_version),
        ("PostgreSQL", check_postgresql),
        ("Requirements", install_requirements),
        ("Environment", setup_environment),
        ("pgvector", check_pgvector),
        ("Project Structure", create_sample_structure),
    ]
    
    for name, check_func in checks:
        if not check_func():
            success = False
    
    print("\n" + "=" * 50)
    
    if success:
        print("✅ Setup completed successfully!")
        print_next_steps()
    else:
        print("⚠️  Setup completed with some issues")
        print("   Please resolve the issues above before running the application")
    
    print("\n📚 Documentation:")
    print("   - README.md: Complete setup and usage guide")
    print("   - http://localhost:8000/docs: API documentation (after starting server)")
    print("   - examples/: Usage examples and test scripts")

if __name__ == "__main__":
    main()