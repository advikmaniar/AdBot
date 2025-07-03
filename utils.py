def clean_text(text: str) -> str:
    # Remove headings
    text = text.replace("###", "").replace("####", "")
    # Convert bold markers
    text = text.replace("**", "*")
    # Flatten nested bullets
    text = text.replace("  -", "•").replace("- ", "• ")
    # Remove redundant blank lines
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)