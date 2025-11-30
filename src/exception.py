class TemplateFileNotFoundError(Exception):
    def __init__(self, missing_files: list[str]):
        message = f"The following template files were not found: {', '.join(missing_files)}"
        super().__init__(message)
        self.missing_files = missing_files