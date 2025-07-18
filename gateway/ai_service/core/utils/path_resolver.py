# core/utils/path_resolver.py
import os

def is_running_in_docker():
    return os.path.exists('/.dockerenv') or os.environ.get('RUNNING_IN_DOCKER') == '1'

def resolve_model_path(config_path: str) -> str:
    if config_path is None:
        return None

    if is_running_in_docker():
        return config_path  # e.g. "/app/models/translation_model"
    
    # Convert "/app/models/..." → "./models/..."
    local_base = os.path.abspath(os.path.join(os.getcwd(), "models"))
    return config_path.replace("/app/models", local_base)


if __name__ == "__main__":
    import sys
    test_path = sys.argv[1] if len(sys.argv) > 1 else "/app/models/translation_model"
    
    try:
        resolved = resolve_model_path(test_path)
        print(f"Resolved Path: {resolved}")
    except Exception as e:
        print(f"Error: {e}")
