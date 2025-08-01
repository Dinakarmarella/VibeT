def read_file(file_path: str) -> str:
    """Reads a file and returns its content."""
    with open(file_path, "r") as f:
        return f.read()
