def highlight_text(text: str, entities: dict) -> str:
    highlighted = text
    for label, items in entities.items():
        for entity_text in items:
            highlighted = highlighted.replace(entity_text, f"[{entity_text}|{label}]")
    return highlighted