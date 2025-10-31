class TrainingDataBotError(Exception):
    """Base error for Training Data Bot."""


class ConfigurationError(TrainingDataBotError):
    """Raised when initialization or configuration fails."""


class DocumentLoadError(TrainingDataBotError):
    """Raised when a document cannot be loaded or parsed."""


