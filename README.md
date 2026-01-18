# Decodo Python Automation

Enterprise-grade training data curation and automation platform for LLM fine-tuning using Decodo + Python automation.

## Overview

A comprehensive Python automation framework that provides a production-ready workflow for intelligent data processing and training dataset generation. Designed with async-first architecture, modular components, and seamless integration with Decodo.

### Key Capabilities

- **Multi-Format Document Loading** - PDF, DOCX, TXT, MD, HTML, JSON, CSV, and web URLs
- **Intelligent Text Processing** - Chunking, preprocessing, and text analysis
- **Automated Task Generation** - Q&A pairs, classification, summarization, NER, red-teaming
- **Quality Assessment** - Automated quality evaluation and filtering
- **Dataset Export** - Multiple export formats (JSONL, JSON) for training pipelines
- **Web Interface** - Interactive FastAPI application with modern UI
- **Cloud Integration** - Supabase support for configuration and storage

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
import asyncio
from bot import TrainingDataBot
from models import TaskType

async def main():
    bot = TrainingDataBot()
    
    # Load documents from files and URLs
    docs = await bot.load_documents([
        "/path/to/document.pdf",
        "/path/to/corpus/",
        "https://example.com/article"
    ])
    
    # Process and generate training data
    dataset = await bot.process_documents(
        documents=docs,
        task_types=[TaskType.QA_GENERATION, TaskType.SUMMARIZATION]
    )
    
    # Export dataset
    await bot.export_dataset(dataset, "./output/dataset.jsonl")

asyncio.run(main())
```

### Web Interface (Interactive)

Start the FastAPI web application for an interactive experience:

```bash
python app.py
# Visit http://localhost:8000
```

Features:
- Upload multiple documents (drag & drop)
- Input URLs for web content
- Select task types to generate
- Download results in JSONL or JSON format
- Real-time processing status

## Installation & Setup

### Core Dependencies

All core dependencies are in `requirements.txt`:

```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6
aiofiles>=23.2.1
supabase>=2.4.0
```

### Optional Dependencies

Install additional packages for enhanced functionality:

```bash
# PDF support
pip install PyMuPDF

# DOCX support
pip install python-docx

# HTML parsing
pip install beautifulsoup4

# Web fetching
pip install httpx

# Install all optional dependencies
pip install PyMuPDF python-docx beautifulsoup4 httpx
```

## Project Architecture

### Directory Structure

```
.
├── core/                      # Core utilities
│   ├── config.py             # Settings management
│   ├── logging.py            # Logging setup
│   ├── config_supabase.py    # Supabase config
│   └── exceptions.py         # Custom exceptions
├── sources/                  # Document loading
│   ├── base_loader.py        # Base loader interface
│   ├── document_loader.py    # File loader (TXT/MD/HTML/JSON/CSV/DOCX)
│   ├── pdf_loader.py         # PDF loader (PyMuPDF)
│   ├── web_loader.py         # URL loader
│   └── unified.py            # Auto-detection & unified interface
├── tasks/                    # Task generation
│   ├── task_base.py          # Base task interface
│   └── __init__.py           # Task generators
├── models.py                 # Data models & enums
├── bot.py                    # Main orchestrator
├── preprocessing.py          # Text processing
├── evaluation.py             # Quality evaluation
├── storage.py                # Export & persistence
├── ai.py                     # AI client interface
├── decodo.py                 # Decodo integration
├── app.py                    # FastAPI web server
├── __init__.py               # Package exports
└── requirements.txt          # Dependencies
```

### Core Modules

**Core Configuration & Utilities**
- `core/config.py` - Runtime settings and configuration
- `core/logging.py` - Structured logging with context
- `core/exceptions.py` - Domain-specific exceptions
- `core/config_supabase.py` - Supabase integration

**Data Models**
- `models.py` - All domain entities and enums
  - `Document` - Loaded document representation
  - `TextChunk` - Text segments for processing
  - `TrainingExample` - Generated training example
  - `Dataset` - Collection of training examples
  - `TaskTemplate` - Task definition template
  - `DocumentType`, `TaskType`, `ExportFormat` - Enums

**Document Loading (sources/)**
- `base_loader.py` - Abstract loader interface
- `document_loader.py` - File-based documents
- `pdf_loader.py` - PDF via PyMuPDF
- `web_loader.py` - Web URLs via httpx & BeautifulSoup
- `unified.py` - Auto-detection and unified API

**Task Management (tasks/)**
- Task generators for common ML tasks
- `QAGenerator` - Generate question-answer pairs
- `ClassificationGenerator` - Classification examples
- `SummarizationGenerator` - Summarization tasks
- `TaskManager` - Orchestrate and manage tasks

**Pipeline Services**
- `preprocessing.py` - Text chunking and preprocessing
- `evaluation.py` - Quality assessment and scoring
- `storage.py` - Dataset export (JSONL/JSON) and database management
- `ai.py` - AI/LLM client interface (stub)
- `decodo.py` - Decodo service client

**Main Orchestrator**
- `bot.py` - `TrainingDataBot` class that wires everything together with async APIs

**Web Application**
- `app.py` - FastAPI server with REST API and interactive UI

## API Usage

### Main Entry Point

The `TrainingDataBot` class is the primary interface:

```python
from bot import TrainingDataBot
from models import TaskType, ExportFormat

bot = TrainingDataBot()
```

### Document Loading

```python
# Load from multiple sources (files, directories, URLs)
docs = await bot.load_documents([
    "./documents/report.pdf",
    "./corpus/",
    "https://example.com/article"
])

# Load from directory
docs = await bot.loader.load_directory("./corpus")

# Load single source
doc = await bot.loader.load_single("./document.pdf")
```

### Processing Documents

```python
# Process with specific task types
dataset = await bot.process_documents(
    documents=docs,
    task_types=[
        TaskType.QA_GENERATION,
        TaskType.CLASSIFICATION,
        TaskType.SUMMARIZATION
    ]
)

# Process all documents
dataset = await bot.process_all_documents()
```

### Quality Evaluation

```python
# Evaluate dataset quality
report = await bot.evaluate_dataset(dataset)

# Get quality scores
print(f"Quality: {report.scores}")
print(f"Summary: {report.summary}")
```

### Dataset Export

```python
# Export to JSONL (line-delimited JSON)
await bot.export_dataset(
    dataset,
    "./output/training_data.jsonl",
    format=ExportFormat.JSONL
)

# Export to JSON
await bot.export_dataset(
    dataset,
    "./output/training_data.json",
    format=ExportFormat.JSON
)
```

## Web Application API

### REST Endpoints

**Process Documents**
```bash
POST /api/process
Content-Type: multipart/form-data

Files: [document1.pdf, document2.txt, ...]
URLs: ["https://example.com"]
task_types: ["qa_generation", "summarization"]
format: "jsonl"
```

**Download Dataset**
```bash
GET /api/download/{filename}
```

**Health Check**
```bash
GET /api/health
```

## Deployment

### Local Development

```bash
python app.py
# Or with auto-reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
# Using Docker Compose
docker-compose up

# Or Docker directly
docker build -t decodo-python-automation .
docker run -p 8000:8000 decodo-python-automation
```

### Railway (Recommended)

Simple deployment to Railway:

```bash
npm i -g @railway/cli
railway login
railway up
```

Or via Railway web dashboard at [railway.app](https://railway.app)

### Heroku

```bash
heroku create your-app-name
git push heroku main
```

### Render

1. Go to [render.com](https://render.com)
2. Create Web Service
3. Connect GitHub repo
4. Settings:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app:app --host 0.0.0.0 --port $PORT`

### Cloud Run (Google Cloud)

```bash
gcloud run deploy decodo-python-automation \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Configuration

### Environment Variables

**Optional - Supabase Integration:**
```bash
SUPABASE_URL=your-project-url
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_STORAGE_BUCKET=datasets
```

**Optional - Processing Settings:**
```bash
MAX_PARALLEL_LOADERS=4
HTTP_TIMEOUT=30
CHUNK_SIZE=512
CHUNK_OVERLAP=100
```

### Supabase Setup

Enable cloud configuration and storage:

1. Create config table:
```sql
create table if not exists app_config (
  key text primary key,
  value jsonb
);

insert into app_config (key, value) values
  ('max_parallel_loaders', '4'::jsonb),
  ('http_timeout', '30'::jsonb);
```

2. Create storage bucket (optional):
```sql
create bucket datasets;
```

3. Set environment variables (see above)

## Features & Capabilities

✨ **Multi-Format Support**
- PDF, DOCX, TXT, Markdown, HTML, JSON, CSV
- Web URLs with automatic content extraction
- Directory scanning with parallel loading

⚡ **Async-First Architecture**
- Fully asynchronous pipeline
- Non-blocking I/O operations
- Parallel document processing

🔌 **Modular & Extensible**
- Base classes for custom loaders
- Pluggable task generators
- Custom evaluators and exporters

🎯 **Task Generation**
- Question-Answer generation
- Text classification
- Summarization
- Named entity recognition (NER)
- Red-teaming
- Instruction-response pairs

📊 **Quality Evaluation**
- Automated quality scoring
- Filtering and deduplication
- Performance metrics

💾 **Multiple Export Formats**
- JSONL (streaming-friendly)
- JSON (nested structure)
- Database integration

🌐 **Web Interface**
- Modern, responsive UI
- Real-time progress tracking
- Drag-and-drop file upload
- URL input support

## Design Principles

- **Clean Public API** - Easy imports from package root
- **Separation of Concerns** - Each module has clear responsibility
- **Extensibility** - Base classes for custom implementations
- **Async-First** - Non-blocking operations throughout
- **Type Safety** - Full type hints for IDE support
- **Production-Ready** - Error handling and logging

## Production Considerations

### File Storage
For production, use cloud storage instead of local filesystem:
- AWS S3
- Google Cloud Storage
- Azure Blob Storage

### Rate Limiting
Add rate limiting for public deployments:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
```

### Authentication
Implement user authentication if needed:
```python
from fastapi.security import HTTPBearer
```

### Monitoring
Set up logging and error tracking:
- Structured logging with context
- Error reporting (Sentry, etc.)
- Performance metrics

### Background Jobs
For long-running tasks, use:
- Celery with Redis/RabbitMQ
- Task queues for scalability

## Troubleshooting

**Port already in use**
```bash
uvicorn app:app --port 8001
```

**Module import errors**
```bash
pip install -r requirements.txt
```

**PDF loading fails**
```bash
pip install PyMuPDF
```

**Web requests timeout**
```bash
pip install httpx
```

## Development

### Running locally
```bash
python app.py
```

### Testing
```bash
python evaluation.py
```

### Adding new loaders
1. Extend `sources/base_loader.py`
2. Implement `load()` method
3. Register in `sources/unified.py`

### Adding new task types
1. Create generator in `tasks/`
2. Register in `TaskManager`
3. Update `TaskType` enum in `models.py`

## License

See LICENSE file for details.

## Support

For questions, issues, or contributions:
1. Check existing documentation
2. Review code examples
3. Contact the development team

---

**Version:** 0.1.0  
**Last Updated:** January 2026
