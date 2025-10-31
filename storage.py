from pathlib import Path

from .models import Dataset, ExportFormat


class DatasetExporter:
    async def export(self, dataset: Dataset, output_path: str | Path, format: ExportFormat = ExportFormat.JSONL) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if format == ExportFormat.JSONL:
            lines = dataset.to_jsonl()
            output_path.write_text("\n".join(lines), encoding="utf-8")
        elif format == ExportFormat.JSON:
            # simple wrapper using JSONL content
            output_path.write_text("[\n" + ",\n".join(dataset.to_jsonl()) + "\n]", encoding="utf-8")
        else:
            raise ValueError(f"Unsupported export format: {format}")
        return output_path


class DatabaseManager:
    async def close(self) -> None:
        return None


