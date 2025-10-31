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

### License

MIT (or your chosen license)


