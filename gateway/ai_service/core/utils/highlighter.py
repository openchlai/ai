def highlight_text(text: str, entities) -> str:
    highlighted = text
    if isinstance(entities, dict):
        for label, items in entities.items():
            for entity_text in items:
                highlighted = highlighted.replace(entity_text, f"[{entity_text}|{label}]")
    elif isinstance(entities, list):
        # Handle if entities is a list of dicts like:
        # [{"label": "PERSON", "text": "Alice"}, ...]
        for entity in entities:
            label = entity.get("label")
            entity_text = entity.get("text")
            if label and entity_text:
                highlighted = highlighted.replace(entity_text, f"[{entity_text}|{label}]")
    else:
        # Unexpected format
        raise ValueError(f"Unexpected entities type: {type(entities)}")
    return highlighted
