from dataclasses import dataclass
from typing import Any, Dict

from models import TaskTemplate, TaskType, TrainingExample


class TaskGenerator:
    """Base interface for task generators."""

    task_type: TaskType

    def __init__(self, template: TaskTemplate | None = None) -> None:
        self.template = template

    async def generate(self, text: str, **kwargs) -> TrainingExample:
        raise NotImplementedError


@dataclass
class TaskManager:
    """Coordinates running multiple task generators."""

    def get_default_templates(self) -> Dict[TaskType, TaskTemplate]:
        return {
            TaskType.QA_GENERATION: TaskTemplate(
                name="Default Q&A",
                task_type=TaskType.QA_GENERATION,
                description="Generate question-answer pairs from text",
                prompt_template="Generate a relevant Q&A from: {text}",
            ),
            TaskType.CLASSIFICATION: TaskTemplate(
                name="Default Classification",
                task_type=TaskType.CLASSIFICATION,
                description="Classify the text",
                prompt_template="Classify this text: {text}",
            ),
            TaskType.SUMMARIZATION: TaskTemplate(
                name="Default Summarization",
                task_type=TaskType.SUMMARIZATION,
                description="Summarize the text concisely",
                prompt_template="Summarize: {text}",
            ),
        }


