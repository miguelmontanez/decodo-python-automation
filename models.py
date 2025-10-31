import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4


@dataclass
class BaseEntity:
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"
    HTML = "html"
    JSON = "json"
    CSV = "csv"
    URL = "url"


class TaskType(str, Enum):
    QA_GENERATION = "qa_generation"
    CLASSIFICATION = "classification"
    SUMMARIZATION = "summarization"
    NER = "named_entity_recognition"
    RED_TEAMING = "red_teaming"
    INSTRUCTION_RESPONSE = "instruction_response"


class ExportFormat(str, Enum):
    JSONL = "jsonl"
    JSON = "json"


@dataclass
class Document(BaseEntity):
    title: str = ""
    content: str = ""
    source: str = ""
    doc_type: DocumentType = DocumentType.TXT
    word_count: int = 0
    char_count: int = 0


@dataclass
class TextChunk(BaseEntity):
    document_id: UUID = field(default_factory=uuid4)
    content: str = ""
    start_index: int = 0
    end_index: int = 0
    chunk_index: int = 0
    token_count: int = 0


@dataclass
class TaskTemplate(BaseEntity):
    name: str = ""
    task_type: TaskType = TaskType.QA_GENERATION
    description: str = ""
    prompt_template: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResult(BaseEntity):
    task_id: UUID = field(default_factory=uuid4)
    input_chunk_id: UUID = field(default_factory=uuid4)
    output: str = ""
    confidence: float = 0.0
    quality_scores: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0


@dataclass
class TrainingExample(BaseEntity):
    input_text: str = ""
    output_text: str = ""
    task_type: TaskType = TaskType.QA_GENERATION
    source_document_id: UUID = field(default_factory=uuid4)
    source_chunk_id: Optional[UUID] = None
    quality_scores: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Dataset(BaseEntity):
    name: str = "dataset"
    description: str = ""
    examples: List[TrainingExample] = field(default_factory=list)
    total_examples: int = 0
    train_split: float = 0.8
    validation_split: float = 0.1
    test_split: float = 0.1

    def to_jsonl(self) -> List[str]:
        lines: List[str] = []
        for ex in self.examples:
            lines.append(json.dumps({
                "input": ex.input_text,
                "output": ex.output_text,
                "task_type": ex.task_type,
            }, ensure_ascii=False))
        return lines


@dataclass
class QualityReport(BaseEntity):
    target_id: UUID = field(default_factory=uuid4)
    overall_score: float = 0.0
    passed: bool = True
    metric_scores: Dict[str, Any] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


