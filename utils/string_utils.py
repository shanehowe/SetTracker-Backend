def to_camel(string: str) -> str:
    return "".join(
        word.capitalize() if i else word for i, word in enumerate(string.split("_"))
    )