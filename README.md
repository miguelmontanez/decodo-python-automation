## Training Data Curation Bot

Enterprise-grade training data curation bot for LLM fine-tuning using Decodo + Python automation.

### What is this?

This package provides a high-level, batteries-included workflow to:
- Load documents from files or the web (PDF, DOCX, TXT, MD, HTML, JSON, CSV, URLs)
- Chunk and preprocess text
- Generate task-specific training examples (Q&A, classification, summarization)
- Evaluate quality
- Export datasets (JSONL/JSON)

It exposes a clean package “front desk” via `__init__.py` so users can import the most useful parts from one place.

### Quickstart

```python
import asyncio
from training_data_bot import TrainingDataBot, TaskType


async def main():
    async with TrainingDataBot() as bot:
        docs = await bot.load_documents(["/path/to/my.pdf", "https://example.com"])
        dataset = await bot.process_documents(
            documents=docs,
            task_types=[TaskType.QA_GENERATION, TaskType.SUMMARIZATION],
        )
        await bot.export_dataset(dataset, "./output/dataset.jsonl")

asyncio.run(main())
```

### Package entry points (front desk)

From the package root you can import the most common classes:

```python
from training_data_bot import (
    TrainingDataBot,
    settings, get_logger, TrainingDataBotError,
    PDFLoader, WebLoader, DocumentLoader, UnifiedLoader,
    QAGenerator, ClassificationGenerator, SummarizationGenerator, TaskManager, TaskTemplate,
    DecodoClient, TextPreprocessor, QualityEvaluator, DatasetExporter,
)
```

### Architecture overview

- Core
  - `core/config.py`: Simple `settings` for runtime configuration
  - `core/logging.py`: `get_logger` and `LogContext`
  - `core/exceptions.py`: Domain exceptions
- Models
  - `models.py`: Entities (`Document`, `TextChunk`, `TrainingExample`, `Dataset`, `QualityReport`) and enums (`DocumentType`, `TaskType`, `ExportFormat`)
- Sources
  - `sources/base_loader.py`: Common loader base
  - `sources/document_loader.py`: TXT/MD/HTML/JSON/CSV/DOCX
  - `sources/pdf_loader.py`: PDF via PyMuPDF (optional dependency)
  - `sources/web_loader.py`: URLs via httpx (+ BeautifulSoup if installed)
  - `sources/unified.py`: Auto-detects and dispatches to the right loader; supports directories and parallel loading
- Tasks
  - `tasks/`: `TaskManager` plus simple generators (`QAGenerator`, `ClassificationGenerator`, `SummarizationGenerator`)
- Pipeline services
  - `preprocessing.py`: `TextPreprocessor` (simple chunker)
  - `evaluation.py`: `QualityEvaluator` (naive scoring)
  - `storage.py`: `DatasetExporter` (JSONL/JSON) and `DatabaseManager` stub
  - `ai.py`: `AIClient` stub
  - `decodo.py`: `DecodoClient` stub
- Orchestrator
  - `bot.py`: `TrainingDataBot` wires everything together with async APIs

### Feature highlights

- Unified loading for many formats and URLs (auto-detection)
- Async pipeline; parallelized document loading
- Pluggable tasks and simple default generators
- Minimal evaluator and exporter included out of the box

### Installation notes (optional dependencies)

Some capabilities require extra packages:
- PDF loading: `pip install PyMuPDF`
- DOCX loading: `pip install python-docx`
- HTML parsing: `pip install beautifulsoup4`
- Web fetching: `pip install httpx`

Install everything:

```bash
pip install PyMuPDF python-docx beautifulsoup4 httpx
```

### API snippets

- Load many documents from a directory:

```python
docs = await bot.loader.load_directory("./my_corpus")
```

- Process with a specific task selection:

```python
from training_data_bot.models import TaskType

dataset = await bot.process_documents(
    documents=docs,
    task_types=[TaskType.QA_GENERATION, TaskType.CLASSIFICATION],
)
```

- Export to JSONL:

```python
from training_data_bot.models import ExportFormat

await bot.export_dataset(dataset, "./out/data.jsonl", format=ExportFormat.JSONL)
```

### Design principles

- Clear, minimal public API via package root
- Separation of concerns: loaders, preprocessing, tasks, evaluation, export
- Extensible base classes; reasonable defaults
- Async-first for scalability

### Limitations and next steps

- Generators and evaluator are heuristic stubs; plug in real AI models and metrics for production
- Add richer logging/telemetry and persistent storage if required
- Extend loaders for more formats as needed

## 🌐 Web Deployment

The project includes a ready-to-deploy FastAPI web application with a beautiful UI!

### Quick Start (Local Development)

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the web server:**
```bash
python app.py
# OR
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

3. **Open in browser:**
```
http://localhost:8000
```

### Features

- 📤 **Upload multiple documents** (PDF, TXT, DOCX, MD, HTML, JSON, CSV)
- 🔗 **Process URLs** from the web
- ✅ **Select task types** (Q&A, Classification, Summarization)
- 📥 **Download generated datasets** (JSONL/JSON format)
- 🎨 **Modern, responsive UI** with real-time progress

### Deployment Options

#### Option 1: Railway (Recommended - Easiest)

1. **Install Railway CLI:**
```bash
npm i -g @railway/cli
railway login
```

2. **Deploy:**
```bash
railway init
railway up
```

Or use the Railway web dashboard:
- Go to [railway.app](https://railway.app)
- Create new project
- Connect your GitHub repo
- Railway auto-detects the `Procfile` and deploys!

**Benefits:** Free tier available, auto-deploys on git push, SSL included

#### Option 2: Render

1. Go to [render.com](https://render.com)
2. Create new Web Service
3. Connect your GitHub repo
4. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Environment:** Python 3

**Benefits:** Free tier, easy setup, auto-deploys

#### Option 3: Heroku

1. **Install Heroku CLI:**
```bash
heroku login
heroku create your-app-name
```

2. **Deploy:**
```bash
git push heroku main
```

**Note:** Requires Heroku account (free tier available)

#### Option 4: Docker (Any Platform)

1. **Build and run:**
```bash
docker-compose up --build
```

Or use Docker directly:
```bash
docker build -t training-data-bot .
docker run -p 8000:8000 training-data-bot
```

**Deploy to:**
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances
- DigitalOcean App Platform
- Any Docker host

#### Option 5: Vercel (Serverless)

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Create `vercel.json`:
```json
{
  "builds": [{"src": "app.py", "use": "@vercel/python"}],
  "routes": [{"src": "/(.*)", "dest": "app.py"}]
}
```

3. Deploy:
```bash
vercel
```

**Note:** May need adjustments for file uploads (consider cloud storage)

### Supabase Configuration (Optional)

Enable dynamic config and cloud storage:

1) Install dep:
```bash
pip install supabase
```

2) Create a table for config overrides:
```sql
create table if not exists app_config (
  key text primary key,
  value jsonb
);
-- example values
insert into app_config (key, value) values
  ('max_parallel_loaders', '4'::jsonb)
on conflict (key) do update set value = excluded.value;
```

3) (Optional) Create a public Storage bucket (e.g. `datasets`) and make it public, or rely on signed URLs.

4) Set env vars:
```bash
export SUPABASE_URL=...            # Project URL
export SUPABASE_SERVICE_ROLE_KEY=...  # Service role (server-side only)
export SUPABASE_STORAGE_BUCKET=datasets
```

On startup, the app will:
- Load `app_config` and overlay values onto `settings`
- Upload exported datasets to the bucket and return a public/signed URL in the API response (`supabase_url`)

### Environment Variables

No required environment variables to run locally, but if you want Supabase integration:

```bash
SUPABASE_URL=your-project-url
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_STORAGE_BUCKET=your-bucket-name   # optional, for dataset uploads

# Optional: Adjust bot settings (can also be set via Supabase app_config table)
MAX_PARALLEL_LOADERS=4
HTTP_TIMEOUT=30
```

### API Endpoints

The web app exposes these REST endpoints:

- `GET /` - Web UI
- `POST /api/process` - Process documents (multipart/form-data)
  - `files`: Uploaded files
  - `urls`: JSON array of URLs
  - `task_types`: JSON array of task types
  - `format`: "jsonl" or "json"
- `GET /api/download/{filename}` - Download generated dataset
- `GET /api/health` - Health check

### Production Considerations

1. **File Storage:** Consider using cloud storage (S3, GCS) instead of local filesystem for `uploads/` and `outputs/`
2. **Rate Limiting:** Add rate limiting for production use
3. **Authentication:** Add user auth if needed
4. **Database:** Add persistent storage for job tracking
5. **Background Jobs:** Use Celery/Redis for long-running processing
6. **Monitoring:** Add logging, metrics, error tracking

### Example Production Setup

```python
# Add to app.py for cloud storage
from google.cloud import storage  # or boto3 for S3

# Replace local file saving with cloud upload
# Replace file serving with cloud download URLs
```

### Troubleshooting

**Port already in use:**
```bash
uvicorn app:app --port 8001
```

**Dependencies missing:**
```bash
pip install -r requirements.txt
```

**File upload errors:**
- Check `uploads/` directory permissions
- Ensure sufficient disk space

### License

MIT (or your chosen license)


