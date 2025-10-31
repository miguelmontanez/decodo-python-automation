from .task_base import TaskManager, TaskGenerator

from ..models import TaskTemplate, TaskType, TrainingExample


class QAGenerator(TaskGenerator):
    task_type = TaskType.QA_GENERATION

    async def generate(self, text: str, **kwargs) -> TrainingExample:
        # Placeholder naive generation
        question = f"What is the main idea of: {text[:80]}?"
        answer = text[:120] if text else ""
        return TrainingExample(
            input_text=question,
            output_text=answer,
            task_type=self.task_type,
            quality_scores={"heuristic": 0.5},
        )


class ClassificationGenerator(TaskGenerator):
    task_type = TaskType.CLASSIFICATION

    async def generate(self, text: str, **kwargs) -> TrainingExample:
        label = "neutral"
        return TrainingExample(
            input_text=text,
            output_text=label,
            task_type=self.task_type,
            quality_scores={"heuristic": 0.5},
        )


class SummarizationGenerator(TaskGenerator):
    task_type = TaskType.SUMMARIZATION

    async def generate(self, text: str, **kwargs) -> TrainingExample:
        summary = (text[:200] + "...") if len(text) > 200 else text
        return TrainingExample(
            input_text=text,
            output_text=summary,
            task_type=self.task_type,
            quality_scores={"heuristic": 0.5},
        )

__all__ = [
    "TaskManager",
    "TaskGenerator",
    "QAGenerator",
    "ClassificationGenerator",
    "SummarizationGenerator",
    "TaskTemplate",
    "TaskType",
]


