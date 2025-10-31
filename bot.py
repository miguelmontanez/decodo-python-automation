import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from .core.config import settings
from .core.exceptions import ConfigurationError
from .core.logging import LogContext, get_logger
from .models import (
    Dataset,
    Document,
    DocumentType,
    ExportFormat,
    QualityReport,
    TaskType,
    TextChunk,
    TrainingExample,
)
from .sources.unified import UnifiedLoader
from .decodo import DecodoClient
from .ai import AIClient
from .tasks import TaskManager, QAGenerator, ClassificationGenerator, SummarizationGenerator
from .preprocessing import TextPreprocessor
from .evaluation import QualityEvaluator
from .storage import DatasetExporter, DatabaseManager


class TrainingDataBot:
    """
    Main Training Data Bot class.

    High-level interface for:
    - Loading documents from various sources
    - Processing text with task templates
    - Quality assessment and filtering
    - Dataset creation and export
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.logger = get_logger("training_data_bot")
        self.config = config or {}
        self._init_components()
        self.logger.info("Training Data Bot initialized successfully")

    def _init_components(self):
        try:
            self.loader = UnifiedLoader()
            self.decodo_client = DecodoClient()
            self.ai_client = AIClient()
            self.task_manager = TaskManager()
            self.preprocessor = TextPreprocessor()
            self.evaluator = QualityEvaluator()
            self.exporter = DatasetExporter()
            self.db_manager = DatabaseManager()

            # State
            self.documents: Dict[UUID, Document] = {}
            self.datasets: Dict[UUID, Dataset] = {}
            self.jobs: Dict[UUID, Dict[str, Any]] = {}
        except Exception as e:
            raise ConfigurationError("Failed to initialize bot components") from e

    async def load_documents(
        self,
        sources: Union[str, Path, List[Union[str, Path]]],
        doc_types: Optional[List[DocumentType]] = None,
        **kwargs,
    ) -> List[Document]:
        if isinstance(sources, (str, Path)):
            sources = [sources]

        documents: List[Document] = []
        for src in sources:
            p = Path(src)
            if p.is_dir():
                dir_docs = await self.loader.load_directory(p)
                documents.extend(dir_docs)
            else:
                doc = await self.loader.load_single(src)
                documents.append(doc)

        for doc in documents:
            self.documents[doc.id] = doc
        return documents

    async def process_documents(
        self,
        documents: Optional[List[Document]] = None,
        task_types: Optional[List[TaskType]] = None,
        quality_filter: bool = True,
        **kwargs,
    ) -> Dataset:
        documents = documents or list(self.documents.values())
        if not documents:
            return Dataset(name="empty", description="No documents provided", examples=[], total_examples=0)

        # Choose tasks
        selected = task_types or [TaskType.QA_GENERATION, TaskType.SUMMARIZATION]
        gens = []
        for t in selected:
            if t == TaskType.QA_GENERATION:
                gens.append(QAGenerator(self.task_manager.get_default_templates()[t]))
            elif t == TaskType.CLASSIFICATION:
                gens.append(ClassificationGenerator(self.task_manager.get_default_templates()[t]))
            elif t == TaskType.SUMMARIZATION:
                gens.append(SummarizationGenerator(self.task_manager.get_default_templates()[t]))

        examples: List[TrainingExample] = []
        for doc in documents:
            chunks: List[TextChunk] = self.preprocessor.chunk_text(doc.id, doc.content)
            for chunk in chunks:
                for gen in gens:
                    ex = await gen.generate(chunk.content)
                    ex.source_document_id = doc.id
                    ex.source_chunk_id = chunk.id
                    examples.append(ex)

        if quality_filter and settings.enable_quality_filter:
            # Minimal heuristic filter: keep non-empty outputs
            examples = [e for e in examples if e.output_text and e.input_text]

        dataset = Dataset(name="dataset", description="Generated dataset", examples=examples, total_examples=len(examples))
        self.datasets[dataset.id] = dataset
        return dataset

    async def evaluate_dataset(self, dataset: Dataset, detailed_report: bool = True) -> QualityReport:
        return await self.evaluator.evaluate(dataset, detailed_report=detailed_report)

    async def export_dataset(
        self,
        dataset: Dataset,
        output_path: Union[str, Path],
        format: ExportFormat = ExportFormat.JSONL,
        split_data: bool = True,
        **kwargs,
    ) -> Path:
        return await self.exporter.export(dataset, output_path, format=format)

    def get_statistics(self) -> Dict[str, Any]:
        return {
            "documents": {
                "total": len(self.documents),
                "total_size": sum(len(d.content) for d in self.documents.values()) if self.documents else 0,
            },
            "datasets": {
                "total": len(self.datasets),
                "total_examples": sum(len(ds.examples) for ds in self.datasets.values()) if self.datasets else 0,
            },
            "jobs": {
                "total": len(self.jobs),
            },
        }

    async def cleanup(self):
        try:
            await self.db_manager.close()
            if hasattr(self.decodo_client, "close"):
                await self.decodo_client.close()
            if hasattr(self.ai_client, "close"):
                await self.ai_client.close()
            self.logger.info("Bot cleanup completed")
        except Exception:
            pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()

    async def quick_process(
        self,
        source: Union[str, Path],
        output_path: Union[str, Path],
        task_types: Optional[List[TaskType]] = None,
        export_format: ExportFormat = ExportFormat.JSONL,
    ) -> Dataset:
        documents = await self.load_documents([source])
        dataset = await self.process_documents(documents=documents, task_types=task_types)
        await self.export_dataset(dataset=dataset, output_path=output_path, format=export_format)
        return dataset


