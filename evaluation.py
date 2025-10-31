from .models import Dataset, QualityReport


class QualityEvaluator:
    """Naive evaluator that computes a simple score."""

    async def evaluate(self, dataset: Dataset, detailed_report: bool = True) -> QualityReport:
        total = len(dataset.examples)
        overall = 1.0 if total > 0 else 0.0
        return QualityReport(
            target_id=dataset.id,
            overall_score=overall,
            passed=overall >= 0.5,
            metric_scores={"count": total},
            issues=[] if overall >= 0.5 else ["Dataset is empty"],
            warnings=[],
        )


