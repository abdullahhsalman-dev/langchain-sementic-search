# Data Directory

Place your PDF files in this directory for automatic processing.

## How it works

1. **Add PDFs**: Simply copy your PDF files into this `data/` directory
2. **Auto-Processing**: The application will automatically detect and process new PDFs on startup
3. **Re-processing**: If you add new PDFs, restart the application or use the `/process-data-folder` endpoint

## Supported formats

- PDF files (`.pdf`)
- Files should be readable (not password-protected)
- Any size supported (larger files take longer to process)

## File naming

- Use descriptive filenames for better organization
- Avoid special characters in filenames
- Examples: `research_paper.pdf`, `company_report_2023.pdf`

## Processing status

The application will:
- Automatically detect new PDF files
- Extract text and create searchable chunks
- Generate embeddings for semantic search
- Store everything in the PostgreSQL database
- Log processing progress to console

## Example structure

```
data/
├── research_papers/
│   ├── machine_learning_2023.pdf
│   └── ai_trends_report.pdf
├── company_docs/
│   ├── quarterly_report.pdf
│   └── product_specs.pdf
└── misc/
    └── user_manual.pdf
```

Subdirectories are supported and will be processed recursively.